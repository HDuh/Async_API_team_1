import time
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Type

from elasticsearch import Elasticsearch, helpers

from utils import logger_config
from utils.config import ELASTIC_DSL
from state.redis_state import RedisState
from .models import BaseModel, MoviesES, GenresES, PersonsES

__all__ = (
    'ElasticController',
)
logger = logger_config.get_logger(__name__)


class ElasticController:
    def __init__(self, index, state: RedisState) -> None:
        self.index: str = index
        self._state: RedisState = state
        self.model: Type[BaseModel] = self._get_model()
        self._state_key: str = f'{self.index}_state'

    @contextmanager
    def elastic(self) -> Type[Elasticsearch]:
        connection = Elasticsearch(ELASTIC_DSL)
        try:
            yield connection
        finally:
            connection.close()

    # TODO: нужно ли делать проверку индекса?
    #   Если да - тогда нужно добавить логику проверки
    #                       и загрузки индекса в еластик
    # def check_index(self, elastic: Elasticsearch, index: str) -> None:
    #     try:
    #         elastic.indices.get_alias()[index]
    #     except KeyError:
    #         self.create_index(elastic, index)

    # @staticmethod
    # def create_index(elastic: Elasticsearch, index: str) -> None:
    #     elastic.indices.create(index=index, body=schema)

    def _insert(self, data: Generator) -> bool:
        """ Основной метод загрузки данных в ES """
        with self.elastic() as elastic:
            # время начал загрузки данных в ES
            start_time = time.time()
            rows, errors = helpers.bulk(
                client=elastic,
                actions=self._transform(data),
                index=self.index
            )

            # затраченное время на загрузку данных в ES
            time_delta = round((time.time() - start_time) * 1000, 2)

            if rows == 0:
                logger.info(f"No update for index: {self.index}", )
            else:
                # обновление состояния после загрузки всех полей в ES
                time_now = datetime.now().isoformat()
                self._state.save_state(self._state_key, time_now)

                logger.info(f"Index: {self.index} | "
                            f"saved: {rows} rows |"
                            f"time: {time_delta} ms.")

            return bool(errors)

    def _transform(self, data: Generator) -> Generator:
        """ Преобразование данных их PG в формат модели для ES """
        model = self._get_model()
        transformed_data = (model(**row).dict() for row in data)
        return (
            {
                "_index": self.index,
                '_id': item['id'],
                **item
            } for item in transformed_data
        )

    def _get_model(self) -> Type[BaseModel]:
        """ Маппинг модели по индексу """
        mapping = {
            'movies': MoviesES,
            'genres': GenresES,
            'persons': PersonsES,
        }

        try:
            return mapping[self.index]
        except KeyError:
            raise ValueError(f'Not query for index {self.index}')

    def __call__(self, data: Generator) -> bool:
        return self._insert(data)
