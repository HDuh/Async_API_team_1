import uuid
from dataclasses import dataclass
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from core import ELASTIC_CONFIG
from .query_manager import QueriesManager


@dataclass
class ModelManager:
    model: Any

    def __post_init__(self):
        """Открытие подключения Elasticsearch"""
        self.es = AsyncElasticsearch(ELASTIC_CONFIG)

    async def filter(self, sort: str = None, **kwargs) -> list[BaseModel]:
        """Выполнение запроса в Elasticsearch с использованием сортировки и параметров поиска"""
        res = await self.es.search(
            index=self.model.Config.es_index,
            body=QueriesManager.create_query(self.model, **kwargs),
            sort=QueriesManager.transform_sorting(sort),
        )
        await self.__close()
        return [self.model(**item['_source']) for item in res['hits']['hits']]

    async def get(self, idx: uuid.UUID) -> BaseModel | None:
        """Выполнение запроса в Elasticsearch по конкретному id"""
        try:
            data = await self.es.get(self.model.Config.es_index, idx)
            await self.__close()
            return self.model(**data['_source'])
        except NotFoundError:
            return

    async def __close(self):
        """Закрытие подключения Elasticsearch"""
        await self.es.close()
