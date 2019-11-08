import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict

from apidaora import GZipFactory, appdaora, route
from apidaora.asgi.base import ASGIApp
from jsondaora import jsondaora

from . import config
from .caller import (
    Caller,
    CallerConfig,
    Error,
    Results,
    wait_for_ditributed_calls_in_background,
)


if config.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def make_app() -> ASGIApp:
    executor = ThreadPoolExecutor(config.workers)
    chunli = Caller(data_source_target=config.redis_target)
    executor.submit(wait_for_ditributed_calls_in_background, chunli, config)

    @route.background('/run', tasks_repository=config.redis_target)
    async def run(duration: int, rps_per_node: int, body: GzipBody) -> Results:
        calls = (line.strip('\n') for line in body.open())
        chunli_run = Caller(data_source_target=config.redis_target)

        await chunli_run.set_calls(calls)
        await chunli_run.start_distributed_calls(
            CallerConfig(duration=duration, rps_per_node=rps_per_node)
        )

        try:
            results = await chunli_run.get_results(duration)

            return results

        except Exception as error:
            logger.exception(error)
            return Results(  # type: ignore
                error=Error(name=type(error).__name__, args=error.args)
            )

    @route.get('/status')
    async def status() -> Status:
        return Status(chunli=random.choice(_CHUN_LI_ATTACKS))

    return appdaora([run, status])


@jsondaora
class GzipBody(GZipFactory):
    mode = 'rt'


@jsondaora
class Status(TypedDict):
    chunli: str


# ref: https://liberproeliis.fandom.com/pt-br/wiki/Chun-Li
_CHUN_LI_ATTACKS = [
    'Hyakuretsukyaku',
    'Senretsukyaku',
    'Oyokukyaku',
    'Houyoku Sen',
    'Hosenka',
]


app = make_app()
