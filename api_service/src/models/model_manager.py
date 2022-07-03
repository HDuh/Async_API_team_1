import uuid
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError, Elasticsearch
from pydantic import BaseModel

from core import ELASTIC_CONFIG
from .query_manager import QueriesManager


@dataclass
class ModelManager:
    model: Any

    # TODO: выпилить из мейн es client. Коннект до эластика будет создаваться тут. Возможно асинк не нужен
    @asynccontextmanager
    async def es_client(self):
        client = AsyncElasticsearch(ELASTIC_CONFIG)
        yield client
        await client.close()

    async def filter(self, es: AsyncElasticsearch, sort: str = None,
                     page: int = 1, size: int = 50, **kwargs) -> list[BaseModel]:
        """Выполнение запроса в Elasticsearch с использованием сортировки и параметров поиска"""
        res = await es.search(
            index=self.model.Config.es_index,
            body=QueriesManager.create_query(self.model, **kwargs),
            sort=QueriesManager.transform_sorting(sort),
            from_=(page - 1) * size + 1,
            size=size,
        )
        return [self.model(**item['_source']) for item in res['hits']['hits']]

    async def get(self, es: AsyncElasticsearch, idx: uuid.UUID) -> BaseModel | None:
        """Выполнение запроса в Elasticsearch по конкретному id"""
        with self.es_client() as es:
            try:
                data = await es.get(self.model.Config.es_index, idx)
                return self.model(**data['_source'])
            except NotFoundError:
                return

    async def save(self, instance):
        """Сохранение данных в Elasticsearch"""
        async with self.es_client() as es:
            await es.create(index=instance.Config.es_index, id=instance.id, body=instance.dict(), refresh=True)
