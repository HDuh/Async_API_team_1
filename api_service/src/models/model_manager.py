import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel

from core import ELASTIC_CONFIG
from .query_manager import QueriesManager


@dataclass
class ModelManager:
    model: Any

    # TODO: выпилить из мейн es client. Коннект до эластика будет создаваться тут.
    #  Ревьювер может докопаться что при каждом запросе открывается подключение
    @asynccontextmanager
    async def es_client(self):
        """Создание подключения к AsyncElasticsearch"""
        client = AsyncElasticsearch(ELASTIC_CONFIG)
        yield client
        await client.close()

    async def filter(self, sort: str = None, page: int = 1, size: int = 50, **kwargs) -> list[BaseModel]:
        """Выполнение запроса в Elasticsearch с использованием сортировки и параметров поиска"""
        async with self.es_client() as es:
            res = await es.search(
                index=self.model.ModelConfig.es_index,
                body=QueriesManager.create_query(self.model, **kwargs),
                sort=QueriesManager.transform_sorting(sort),
                from_=(page - 1) * (size + 1),
                size=size,
            )
            return [self.model(**item['_source']) for item in res['hits']['hits']]

    async def get(self, idx: uuid.UUID) -> BaseModel | None:

        """Выполнение запроса в Elasticsearch по конкретному id"""
        async with self.es_client() as es:
            try:
                data = await es.get(self.model.ModelConfig.es_index, idx)
                return self.model(**data['_source'])
            except NotFoundError:
                return

    async def async_save(self, instance):
        """Сохранение экземпляра модели в Elasticsearch"""
        async with self.es_client() as es:
            await es.create(index=instance.ModelConfig.es_index, id=instance.id, body=instance.__dict__, refresh=True)

    async def async_delete(self, instance):
        """Удаление экземпляра модели из Elasticsearch"""
        async with self.es_client() as es:
            await es.delete(index=instance.ModelConfig.es_index, id=instance.id)

    async def async_check_or_create_index(self):
        """Проверка или создание индекса в Elasticsearch"""
        async with self.es_client() as es:
            alias = await es.indices.get_alias()
            if not alias.get(self.model.ModelConfig.es_index):
                await es.indices.create(index=self.model.ModelConfig.es_index, body=self.model.ModelConfig.schema)
