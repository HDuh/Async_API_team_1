import abc

import backoff
from redis import Redis

from utils import logger_config
from utils.config import REDIS_CONFIG, BACKOFF_CONFIG

logger = logger_config.get_logger(__name__)

__all__ = (
    "RedisState",
)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, key: str, value: str) -> None:
        """Сохранить состояние в Redis"""
        pass

    @abc.abstractmethod
    def get_state(self, key: str,
                  default: str = None) -> str:
        """Загрузить состояние  из Redis"""
        pass


class RedisState(BaseStorage):
    """ State на основе хранилиза Redis """
    def __init__(self, config: REDIS_CONFIG,
                 conn: Redis = None):
        self._config = config
        self._conn = conn

    @property
    def redis_connection(self) -> Redis:
        """ Проверка наличия соединения
        и создание нового, если соедининия нет"""
        if not self._conn or not self._conn.ping():
            self._conn = self._create_connection()
        return self._conn

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> Redis:
        """Создание новое соединение к Redis"""
        return Redis(**self._config.dict())

    @backoff.on_exception(**BACKOFF_CONFIG)
    def save_state(self, key: str, value: str) -> None:
        """Создание пары ключ-значение в Redis"""
        self.redis_connection.set(key, value.encode())
        logger.info(f'State update -  {key}: {value}')

    @backoff.on_exception(**BACKOFF_CONFIG)
    def get_state(self, key: str,
                  default: str = None) -> str:
        """Получение значения по ключу"""
        data: bytes = self.redis_connection.get(key)
        if data:
            return data.decode("utf-8")
        return default
