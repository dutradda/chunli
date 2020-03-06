from typing import Generator, List

from chunli.caller import Call


global get_calls_block


def get_calls_block() -> Generator[List[Call], None, None]:
    yield [
        Call(url='http://localhost:8001/hello', method='GET', headers=None,)
    ]
