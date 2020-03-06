from apidaora import appdaora, route


@route.get('/hello')
def hello() -> str:
    return 'Hello World!'


app = appdaora(hello)
