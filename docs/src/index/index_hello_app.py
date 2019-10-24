from apidaora import appdaora, route


@route.get('/hello')
def hello():
    return 'Hello World!'


app = appdaora(hello)
