from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extras import DictCursor

from utils import POSTGRES_DSL, APP_CONFIG
from .queries import index_mapper

__all__ = (
    'PostgresController',
)


class PostgresController:
    @contextmanager
    def _cursor(self):
        connection = psycopg2.connect(**POSTGRES_DSL, cursor_factory=DictCursor)
        try:
            cursor = connection.cursor()
            yield cursor
        finally:
            connection.close()

    @staticmethod
    def _prepared_query(current_index: str, state: str) -> str:
        """
        Формирование запроса на основе:
            индекса - current_index
            состояния обновления индекса - state
        """
        query = index_mapper(current_index, state)
        return query

    def _do_query(self, *args, packet_size: int = int(APP_CONFIG.batch_size)) -> Generator:
        """ Достает данные из подготовленного запроса - prepared_query """
        with self._cursor() as cursor:
            cursor.execute(self._prepared_query(*args))
            # TODO: использовать COUNT Для проверки на пустоту.
            while data := cursor.fetchmany(size=packet_size):
                yield from data

    def __call__(self, *args):
        return self._do_query(*args)
