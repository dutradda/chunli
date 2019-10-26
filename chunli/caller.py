import asyncio
import logging
import time
from typing import Dict, Iterable, List, Optional, TypedDict

import aioredis  # type: ignore
import httpx
import numpy as np
import orjson
from apidaora import MethodType
from dictdaora import DictDaora
from jsondaora import as_typed_dict, jsondaora, typed_dict_asjson

from . import AppConfig
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
    duration: float
    requested_rps_per_node: float
    realized_requests: float
    realized_rps: float
    latency: Latency
    error: Optional[Error]


@jsondaora
class Call(TypedDict):
    url: str
    method: str
    headers: Optional[Dict[str, str]]


class Caller(DictDaora):
    data_source: aioredis.Redis
    data_source_target: str
    _running_key = 'chunli:running'
    _results_key = 'chunli:results'
    _calls_key = 'chunli:calls'

    async def set_calls(self, calls: Iterable[str]) -> None:
        await self.data_source.delete(self._running_key)
        await self.data_source.delete(self._calls_key)
        await self.data_source.delete(self._results_key)

        for call in calls:
            try:
                call_ = typed_dict_asjson(
                    as_typed_dict(orjson.loads(call), Call), Call
                )
                await self.data_source.rpush(self._calls_key, call_)

            except Exception:
                if call.startswith('http'):
                    try:
                        call_ = typed_dict_asjson(
                            Call(  # type: ignore
                                url=call,
                                method=MethodType.GET.value,
                                headers={},
                            ),
                            Call,
                        )
                        await self.data_source.rpush(self._calls_key, call_)

                    except Exception as error:
                        logger.exception(error)
                        logger.warning(f'Invalid line {call}')

                else:
                    logger.warning(f'Invalid line {call}')

    async def run_calls(self, duration: int, rps_per_node: int) -> None:
        logger.info('Starting calls')
        wait_running = True

        async with httpx.AsyncClient() as http_data_source:
            latencies = []
            responses = []
            error: Optional[Exception] = None
            calls_start_time = time.time()
            inputs: List[bytes] = []

            await self.data_source.sadd(self._running_key, id(self))

            async def wait() -> bool:
                now = time.time()

                if now - calls_start_time >= duration:
                    wait_running = False  # noqa
                    return True

                await asyncio.sleep(0.001)
                return False

            while wait_running:
                input_ = await self.data_source.lpop(self._calls_key)

                if input_ is None:
                    if not inputs:
                        continue

                    await self.data_source.rpush(self._calls_key, *inputs)
                    inputs = []
                    continue

                else:
                    inputs.append(input_)

                input_ = orjson.loads(input_)
                logger.debug(f'Getting output for: {input_}')

                try:
                    start_time = time.time()
                    response = await http_data_source.get(
                        input_['url'], headers=input_['headers']
                    )
                    await response.read()
                    end_time = time.time()

                    latency = end_time - start_time
                    latencies.append(latency)
                    logger.debug(f'Output got: latency={latency}')

                    responses.append(response)
                    logger.debug(
                        f'Response status code: {response.status_code}'
                    )

                except Exception as error_:
                    wait_running = False
                    error = error_
                    logger.exception(error)
                    break

                if await wait():
                    break

        await self.data_source.srem(self._running_key, id(self))

        realized_requests = len(responses)
        results = Results(  # type: ignore
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
        )

        if error is not None:
            results['error'] = error

        try:
            await self.data_source.sadd(
                self._results_key, typed_dict_asjson(results, Results)
            )
        except Exception as error:
            logger.exception(error)

        logger.info('Finishing calls')
        logger.debug(results)

    async def get_results(self, timeout: int = 10) -> Results:
        start_wait = time.time()

        while (
            await self.data_source.scard(self._running_key)
            and start_wait + timeout > time.time()
        ):
            await asyncio.sleep(0.001)

        if await self.data_source.scard(self._running_key):
            raise ResultsTimeoutError(timeout)

        all_results = await self.data_source.smembers(self._results_key)
        all_durations = []
        all_requested_rps_per_node = []
        all_realized_requests = []
        all_realized_rps = []
        all_means = []
        all_medians = []
        all_p99s = []
        all_p95s = []

        for result in all_results:
            result = orjson.loads(result)
            all_durations.append(result['duration'])
            all_requested_rps_per_node.append(result['requested_rps_per_node'])
            all_realized_requests.append(result['realized_requests'])
            all_realized_rps.append(result['realized_rps'])
            all_means.append(result['latency']['mean'])
            all_medians.append(result['latency']['median'])
            all_p99s.append(result['latency']['percentile99'])
            all_p95s.append(result['latency']['percentile95'])

        results: Results = Results(
            duration=float(np.mean(all_durations)),
            requested_rps_per_node=float(np.mean(all_requested_rps_per_node)),
            realized_requests=float(np.mean(all_realized_requests)),
            realized_rps=float(np.mean(all_realized_rps)),
            latency=Latency(
                mean=float(np.mean(all_means)),
                median=float(np.mean(all_medians)),
                percentile99=float(np.mean(all_p99s)),
                percentile95=float(np.mean(all_p95s)),
            ),
            error=None,
        )
        return results


async def make_caller(config: AppConfig) -> Caller:
    data_source = await aioredis.create_redis_pool(config.redis_target)
    return Caller(
        data_source=data_source, data_source_target=config.redis_target
    )
