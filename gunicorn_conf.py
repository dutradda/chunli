import os

import redis


def worker_exit(server, worker):
    r = redis.Redis.from_url(os.environ.get('REDIS_TARGET', 'redis://'))
    r.publish('chunli:distributed', 'stop')


def child_exit(server, worker):
    r = redis.Redis.from_url(os.environ.get('REDIS_TARGET', 'redis://'))
    r.publish('chunli:distributed', 'stop')
