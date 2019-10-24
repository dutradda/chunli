import asyncio
from typing import List, TypedDict

from apidaora import GZipFactory, appdaora, route
from apidaora.asgi.base import ASGIApp
from jsondaora import jsondaora

from . import caller, config


@jsondaora
class Results(TypedDict):
    duration: int
    rps_per_node: int
    calls: List[str]


@jsondaora
class GzipBody(GZipFactory):
    mode = 'rt'


def make_app() -> ASGIApp:
    # loop = asyncio.get_event_loop()
    # chunli = loop.create_task(
    #     caller.make_caller(config)
    # )

    @route.background('/run', tasks_repository=config.redis_target)
    async def run(duration: int, rps_per_node: int, body: GzipBody) -> Results:
        calls = []
        # caller.run_calls(chunli)

        for line in body.open():
            calls.append(line.strip('\n'))

        return Results(
            duration=duration, rps_per_node=rps_per_node, calls=calls
        )

    return appdaora(run)


app = make_app()
