from typing import Dict, TypedDict

from apidaora import MethodType
from dictdaora import DictDaora
from jsondaora import jsondaora

import aioredis  # type: ignore

from . import AppConfig


class Caller(DictDaora):
    data_source: aioredis.Redis
    data_source_target: str


class Call(DictDaora):
    url: str
    method: MethodType
    headers: Dict[str, str]


async def make_caller(config: AppConfig) -> Caller:
    data_source = await aioredis.create_redis_pool(config.redis_target)
    return Caller(
        data_source=data_source, data_source_target=config.redis_target
    )


@jsondaora
class Results(TypedDict):
    duration: int
    rps_per_node: int


def run_calls(caller: Caller) -> Results:
    ...
