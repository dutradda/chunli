"""chunli"""

from confdaora import confdaora_env
from dictdaora import DictDaora


__version__ = '0.2.0'


class AppConfig(DictDaora):
    redis_target: str = 'redis://'
    debug: bool = False


config: AppConfig = confdaora_env(AppConfig)


from .app import app  # noqa isort:skip


__all__ = ['app', 'config']
