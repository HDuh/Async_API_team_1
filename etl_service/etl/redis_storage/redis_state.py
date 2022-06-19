from contextlib import contextmanager
from datetime import datetime

from redis import Redis

from utils import logger_etl, REDIS_CONFIG

__all__ = (
    'RedisState',
)


class RedisState:
    """State на основе хранилища Redis"""

    @contextmanager
    def _connection(self):
        connection = Redis(**REDIS_CONFIG)
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def save_state(redis: Redis, key: str, value: str) -> None:
        """Создание пары ключ-значение в Redis"""
        redis.set(key, value.encode())
        logger_etl.info(f'State update -  {key}: {value}')

    @staticmethod
    def get_state(redis: Redis, key: str, default: str = datetime.min) -> str:
        """Получение значения по ключу"""
        if data := redis.get(key):
            return data.decode('utf-8')
        return default

    def __call__(self, key, value=None):
        with self._connection() as redis:
            if not value:
                return self.get_state(redis, key)
            self.save_state(redis, key, value)
