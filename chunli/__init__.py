"""chunli"""

from dataclasses import dataclass

from confdaora import confdaora_env


__version__ = '0.11.3'


@dataclass
class AppConfig:
    redis_target: str = 'redis://'
    workers: int = 1
    debug: int = 0
    http_max_connections: int = 4096
    http_timeout: int = 5


config: AppConfig = confdaora_env(AppConfig)


__all__ = ['app', 'config']
