import uuid
from dataclasses import dataclass
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from .query_manager import QueriesManager


@dataclass
class ModelManager:
    model: Any

    async def filter(self, es: AsyncElasticsearch, sort: str = None,
                     number: int = 1, size: int = 50, **kwargs) -> list[BaseModel]:
        """Выполнение запроса в Elasticsearch с использованием сортировки и параметров поиска"""
        res = await es.search(
            index=self.model.Config.es_index,
            body=QueriesManager.create_query(self.model, **kwargs),
            sort=QueriesManager.transform_sorting(sort),
            from_=(number - 1) * size + 1,
            size=size,
        )
        return [self.model(**item['_source']) for item in res['hits']['hits']]

    async def get(self, es: AsyncElasticsearch, idx: uuid.UUID) -> BaseModel | None:
        """Выполнение запроса в Elasticsearch по конкретному id"""
        try:
            data = await es.get(self.model.Config.es_index, idx)
            return self.model(**data['_source'])
        except NotFoundError:
            return
