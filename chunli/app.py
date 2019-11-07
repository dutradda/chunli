import asyncio
import logging

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


@jsondaora
class GzipBody(GZipFactory):
    mode = 'rt'


def make_app() -> ASGIApp:
    loop = asyncio.get_running_loop()
    coros = []

    for _ in range(config.workers):
        coros.append(wait_for_ditributed_calls_in_background(loop, config))

    @route.background('/run', tasks_repository=config.redis_target)
    async def run(duration: int, rps_per_node: int, body: GzipBody) -> Results:
        calls = (line.strip('\n') for line in body.open())
        chunli_run = Caller(data_source_target=config.redis_target)

        await chunli_run.set_calls(calls)
        await chunli_run.start_distributed_calls(
            CallerConfig(duration=duration, rps_per_node=rps_per_node)
        )

        try:
            return await chunli_run.get_results(duration)
        except Exception as error:
            logger.exception(error)
            return Results(  # type: ignore
                error=Error(name=type(error).__name__, args=error.args)
            )

    return appdaora(run)


app = make_app()
