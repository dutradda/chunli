import asyncio
import logging
import time
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypedDict,
)

import aioredis  # type: ignore
import numpy as np
import orjson
import redis
import requests
from apidaora import MethodType
from dictdaora import DictDaora
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from . import AppConfig
from .call import Call
from .exceptions import ResultsTimeoutError


logger = logging.getLogger(__name__)


@jsondaora
class Latency(TypedDict):
    mean: float
    median: float
    percentile99: float
    percentile95: float


@jsondaora
class Error(TypedDict):
    name: str
    args: List[str]


@jsondaora
class Results(TypedDict):
    duration: Optional[float]
    requested_rps_per_node: Optional[float]
    realized_requests: Optional[float]
    realized_rps: Optional[float]
    latency: Optional[Latency]
    error: Optional[Error]
    nodes_quantity: Optional[int]
    errors_count: Optional[int]


class CallerConfig(TypedDict):
    duration: int
    rps_per_node: int


class Caller(DictDaora):
    data_source_target: str
    running = True
    _running_key = 'chunli:running'
    _results_key = 'chunli:results'
    _distributed_calls_key = 'chunli:distributed'
    _calls_key = 'chunli:calls'
    _script_key = 'chunli:script'

    async def set_calls(self, calls: Iterable[str]) -> None:
        data_source = await self.get_data_source()
        await data_source.delete(self._calls_key)
        await data_source.delete(self._script_key)

        for call_str in calls:
            try:
                calls_group = orjson.loads(call_str)

                if not isinstance(calls_group, list):
                    calls_group = [calls_group]

                for call in calls_group:
                    if 'method' not in call:
                        call['method'] = MethodType.GET.value

                calls_group = orjson.dumps(
                    [as_typed_dict(c, Call) for c in calls_group]
                )
                await data_source.rpush(self._calls_key, calls_group)

            except Exception:
                if call_str.startswith('http'):
                    try:
                        calls_group = orjson.dumps(
                            [
                                Call(
                                    url=call_str,
                                    method=MethodType.GET.value,
                                    headers={},
                                    body=None,
                                )
                            ]
                        )
                        await data_source.rpush(self._calls_key, calls_group)

                    except Exception as error:
                        logger.exception(error)
                        logger.warning(f'Invalid line {call_str}')

                else:
                    logger.warning(f'Invalid line {call_str}')

        data_source.close()

    async def set_script(self, script_content: str) -> None:
        data_source = await self.get_data_source()
        await data_source.set(self._script_key, script_content)

    async def get_data_source(self) -> aioredis.Redis:
        return await aioredis.create_redis_pool(self.data_source_target)

    def get_sync_data_source(self) -> aioredis.Redis:
        return redis.Redis.from_url(self.data_source_target)

    def run_distributed_calls(self) -> None:
        data_source = self.get_sync_data_source()
        pubsub = data_source.pubsub()
        pubsub.subscribe(self._distributed_calls_key)
        message = pubsub.get_message()

        while not message or message['data'] == 1:
            time.sleep(1)
            message = pubsub.get_message()
            continue

        if message['data'] == b'stop':
            raise SystemExit(0)

        configuration: CallerConfig = orjson.loads(message['data'])

        try:
            self._run_calls(
                configuration['duration'], configuration['rps_per_node']
            )
        except Exception as error:
            logger.exception(error)

        data_source.close()

    async def start_distributed_calls(
        self, configuration: CallerConfig
    ) -> None:
        data_source = self.get_sync_data_source()
        data_source.delete(self._running_key)
        data_source.delete(self._results_key)
        data_source.publish(
            self._distributed_calls_key, orjson.dumps(configuration)
        )
        data_source.close()

    def _run_calls(self, duration: int, rps_per_node: int) -> None:
        with requests.Session() as http_data_source:
            running_id = str(uuid.uuid4())
            logger.info(f'Starting calls for {running_id}')
            data_source = self.get_sync_data_source()
            responses_status_map: DefaultDict[int, int] = defaultdict(int)
            latencies: List[float] = []
            executor = ThreadPoolExecutor(max_workers=100)
            calls_start_time = time.time()
            futures = []
            calls_count_checkpoint = 0
            wait_checkpoint = calls_start_time
            last_wait_time = 0.1
            run_call_func = make_run_call_function(
                http_data_source, responses_status_map, latencies,
            )
            script_content = data_source.get(self._script_key)
            get_calls_block_ = None
            calls_count = 0

            if script_content:
                exec(script_content)
                get_calls_block_ = get_calls_block  # type: ignore  # noqa

            data_source.sadd(self._running_key, running_id)

            while should_running(calls_start_time, duration):
                try:
                    if get_calls_block_:
                        inputs = get_calls_block_()

                    else:
                        inputs = data_source.lpop(self._calls_key)

                        if inputs is None:
                            continue

                        else:
                            data_source.rpush(self._calls_key, inputs)

                        inputs = orjson.loads(inputs)

                    def call_inputs() -> None:
                        nonlocal calls_count
                        for input_ in inputs:
                            logger.debug(f'Getting output for: {input_}')
                            run_call_func(input_)
                            calls_count += 1

                    futures.append(executor.submit(call_inputs))
                    (
                        last_wait_time,
                        wait_checkpoint,
                        calls_count_checkpoint,
                    ) = wait_to_call(
                        wait_checkpoint=wait_checkpoint,
                        calls_count_checkpoint=calls_count_checkpoint,
                        last_wait_time=last_wait_time,
                        current_calls_count=calls_count,
                        rps=rps_per_node,
                    )

                except Exception as error_:
                    logger.exception(type(error_).__name__)

            for future in futures:
                future.result()
            executor.shutdown()

            data_source.delete(self._script_key)

            realized_requests = sum(responses_status_map.values())
            results = make_results(
                duration,
                rps_per_node,
                realized_requests,
                latencies,
                responses_status_map,
            )

            data_source.hset(
                self._results_key,
                running_id,
                typed_dict_asjson(results, Results),
            )
            data_source.srem(self._running_key, running_id)
            data_source.close()
            logger.info('Finishing calls')
            logger.debug(results)

    async def get_results(self, duration: int, timeout: int = 0) -> Results:
        start_wait = time.time()
        data_source = await self.get_data_source()

        while (
            await data_source.scard(self._running_key)
            or not await data_source.hlen(self._results_key)
            or start_wait + duration + timeout > time.time()
        ):
            await asyncio.sleep(1)

        if await data_source.scard(
            self._running_key
        ) or not await data_source.hlen(self._results_key):
            raise ResultsTimeoutError(duration + timeout)

        all_results = await data_source.hgetall(self._results_key)
        all_durations = []
        all_requested_rps_per_node = []
        all_realized_requests = []
        all_realized_rps = []
        all_means = []
        all_medians = []
        all_p99s = []
        all_p95s = []

        for result in all_results.values():
            result = orjson.loads(result)
            all_durations.append(result['duration'])
            all_requested_rps_per_node.append(result['requested_rps_per_node'])
            all_realized_requests.append(result['realized_requests'])
            all_realized_rps.append(result['realized_rps'])
            all_means.append(result['latency']['mean'])
            all_medians.append(result['latency']['median'])
            all_p99s.append(result['latency']['percentile99'])
            all_p95s.append(result['latency']['percentile95'])

        duration_ = float(np.mean(all_durations))
        realized_requests = float(np.sum(all_realized_requests))
        results = Results(
            duration=duration_,
            requested_rps_per_node=float(np.mean(all_requested_rps_per_node)),
            realized_requests=realized_requests,
            realized_rps=realized_requests / duration,
            latency=Latency(
                mean=float(np.mean(all_means)),
                median=float(np.mean(all_medians)),
                percentile99=float(np.mean(all_p99s)),
                percentile95=float(np.mean(all_p95s)),
            ),
            error=None,
            nodes_quantity=len(all_results),
            errors_count=0,
        )
        data_source.close()
        return results

    def stop(self) -> None:
        self.running = False


def make_run_call_function(
    http_data_source: requests.Session,
    responses_status_map: DefaultDict[int, int],
    latencies: List[float],
) -> Callable[[Dict[str, Any]], None]:
    def run_call(input_: Dict[str, Any]) -> None:
        start_time = time.time()

        try:
            response = http_data_source.request(
                url=input_['url'],
                headers=input_['headers'],
                method=input_['method'],
                json=input_.get('body'),
            )
        except Exception as error:
            response = error  # type: ignore
            logger.exception(type(error).__name__)
            responses_status_map[-1] += 1
        else:
            logger.debug(f'Response status code: {response.status_code}')
            responses_status_map[response.status_code] += 1

        latency = time.time() - start_time
        latencies.append(latency)
        logger.debug(f'Output got: latency={latency}')

    return run_call


def wait_to_call(
    wait_checkpoint: float,
    calls_count_checkpoint: int,
    last_wait_time: float,
    current_calls_count: int,
    rps: int,
) -> Tuple[float, float, int]:
    wait_time = last_wait_time
    now = time.time()

    if now > wait_checkpoint + 1:
        current_rps = (current_calls_count - calls_count_checkpoint) * round(
            now - wait_checkpoint
        )
        rps_diff_percent = 1 - (current_rps / rps)
        wait_checkpoint = now
        calls_count_checkpoint = current_calls_count

        if not -1.01 <= rps_diff_percent <= 0.01:
            wait_time -= last_wait_time * rps_diff_percent

        wait_time = wait_time if wait_time >= 0 else 0

        logger.debug(
            f'current_rps={current_rps}, '
            f'rps_diff_percent={rps_diff_percent}, '
            f'wait_time={wait_time}'
        )

    time.sleep(wait_time)

    return wait_time, wait_checkpoint, calls_count_checkpoint


def make_results(
    duration: int,
    rps_per_node: int,
    realized_requests: float,
    latencies: Iterable[float],
    responses_status_map: DefaultDict[int, int],
    error: Optional[Error] = None,
    nodes_quantity: Optional[int] = None,
) -> Results:
    return Results(
        duration=duration,
        requested_rps_per_node=rps_per_node,
        realized_requests=realized_requests,
        realized_rps=realized_requests / duration,
        latency=Latency(
            mean=float(np.mean(latencies)),
            median=float(np.median(latencies)),
            percentile99=float(np.percentile(latencies, 99)),
            percentile95=float(np.percentile(latencies, 95)),
        ),
        errors_count=sum(
            (
                responses_status_map[500],
                responses_status_map[-1],
                responses_status_map[502],
                responses_status_map[503],
            )
        ),
        error=error,
        nodes_quantity=nodes_quantity,
    )


def wait_for_ditributed_calls_in_background(
    chunli: 'Caller', config: AppConfig
) -> None:
    while True:
        chunli.run_distributed_calls()


def should_running(calls_start_time: float, duration: int) -> bool:
    if time.time() - calls_start_time > duration:
        return False

    return True
