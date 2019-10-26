import logging

from apidaora import GZipFactory, appdaora, route
from apidaora.asgi.base import ASGIApp
from jsondaora import jsondaora

from . import caller, config


if config.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


@jsondaora
class GzipBody(GZipFactory):
    mode = 'rt'


def make_app() -> ASGIApp:
    @route.background('/run', tasks_repository=config.redis_target)
    async def run(
        duration: int, rps_per_node: int, body: GzipBody
    ) -> caller.Results:
        calls = (line.strip('\n') for line in body.open())
        chunli = await caller.make_caller(config)

        await chunli.set_calls(calls)
        await chunli.run_calls(duration, rps_per_node)

        return await chunli.get_results(duration)

    return appdaora(run)


app = make_app()
