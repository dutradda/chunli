from typing import TypedDict

from apidaora import appdaora, route
from jsondaora import jsondaora


@route.get('/hello')
def hello() -> str:
    return 'Hello World!'


@jsondaora
class Body(TypedDict):
    name: str


@route.post('/hello-body')
def hello_body(body: Body) -> str:
    return f"Hello {body['name']}!"


app = appdaora([hello, hello_body])
