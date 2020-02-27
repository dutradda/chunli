"""chunli"""

from confdaora import confdaora_env
from dictdaora import DictDaora


__version__ = '0.5.1'


class AppConfig(DictDaora):
    redis_target: str = 'redis://'
    workers: int = 1
    debug: int = 0


config: AppConfig = confdaora_env(AppConfig)


from .app import app  # noqa isort:skip


__all__ = ['app', 'config']
