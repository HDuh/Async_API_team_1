import time
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Type

from elasticsearch import Elasticsearch, helpers

from redis_storage import RedisState
from utils import ELASTIC_DSL, logger_etl
from .indexes import get_schema
from .models_controller import get_index_model

__all__ = (
    'ElasticController',
)


class ElasticController:

    @contextmanager
    def elastic(self) -> Type[Elasticsearch]:
        connection = Elasticsearch(ELASTIC_DSL)
        try:
            yield connection
        finally:
            connection.close()

    def check_index(self, elastic: Elasticsearch, index: str) -> None:
        if not elastic.indices.get_alias().get(index):
            self.create_index(elastic, index)

    @staticmethod
    def create_index(elastic: Elasticsearch, index: str) -> None:
        elastic.indices.create(index=index, body=get_schema(index))

    def _insert(self, elastic: Elasticsearch, data: Generator, index: str, state: RedisState) -> None:
        """ Основной метод загрузки данных в ES """
        # время начал загрузки данных в ES
        start_time = time.time()
        rows, errors = helpers.bulk(
            client=elastic,
            actions=self._transform(index, data),
            index=index
        )

        # TODO: подумать как упростить
        # затраченное время на загрузку данных в ES
        time_delta = round((time.time() - start_time) * 1000, 2)

        if not rows:
            logger_etl.info(f"No update for index: {index}", )
        else:
            # обновление состояния после загрузки всех полей в ES
            time_now = datetime.now().isoformat()
            state(f'{index}_state', time_now)

            logger_etl.info(f'''Index: {index}
                            saved: {rows} rows
                            time: {time_delta} ms.''')

    @staticmethod
    def _transform(index: str, data: Generator) -> Generator:
        """ Преобразование данных их PG в формат модели для ES """
        model = get_index_model(index)
        transformed_data = (model(**row).dict() for row in data)
        return (
            {
                "_index": index,
                '_id': item['id'],
                **item
            } for item in transformed_data
        )

    def __call__(self, index: str, data: Generator, state: RedisState) -> None:
        with self.elastic() as elastic:
            self.check_index(elastic, index)
            self._insert(elastic, data, index, state)
