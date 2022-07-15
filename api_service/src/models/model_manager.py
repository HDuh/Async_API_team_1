import uuid
from dataclasses import dataclass
from typing import Any

from elasticsearch import NotFoundError
from pydantic import BaseModel

from src.db.elastic import get_elastic
from .query_manager import QueriesManager


@dataclass
class ModelManager:
    model: Any

    async def filter(self, sort: str = None, page: int = 1, size: int = 50, **kwargs) -> list[BaseModel]:
        """Выполнение запроса в Elasticsearch с использованием сортировки и параметров поиска"""
        es = await get_elastic()
        res = await es.search(
            index=self.model.ModelConfig.es_index,
            body=QueriesManager.create_query(self.model, **kwargs),
            sort=QueriesManager.transform_sorting(sort),
            from_=0 if page == 1 else (page - 1) * size,
            size=size,
        )
        return [self.model(**item['_source']) for item in res['hits']['hits']]

    async def get(self, idx: uuid.UUID) -> BaseModel | None:
        """Выполнение запроса в Elasticsearch по конкретному id"""
        es = await get_elastic()
        try:
            data = await es.get(self.model.ModelConfig.es_index, idx)
            return self.model(**data['_source'])
        except NotFoundError:
            return

    @staticmethod
    async def async_save(instance):
        """Сохранение экземпляра модели в Elasticsearch"""
        es = await get_elastic()
        await es.create(index=instance.ModelConfig.es_index, id=instance.id, body=instance.__dict__,
                        refresh=True)

    @staticmethod
    async def async_delete(instance):
        """Удаление экземпляра модели из Elasticsearch"""
        es = await get_elastic()
        await es.delete(index=instance.ModelConfig.es_index, id=instance.id, refresh=True)

    async def async_check_or_create_index(self):
        """Проверка или создание индекса в Elasticsearch"""
        es = await get_elastic()
        alias = await es.indices.get_alias()
        if not alias.get(self.model.ModelConfig.es_index):
            await es.indices.create(index=self.model.ModelConfig.es_index, body=self.model.ModelConfig.schema)
