import uuid
from dataclasses import dataclass
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Search, Q
from core import config


@dataclass
class ModelManager:
    model: Any

    def __post_init__(self):
        self.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])

    # TODO: открывается коннект сразу при создании инстанса класса

    def filter(self, **kwargs):
        # print(1)
        # # elastic_dsl использоавать Q объекты
        # a = Search(using=self.es, index=self.model.Config.es_index).query('match_all', title={})
        # return
        # for item in data:
        #     yield self.model(**item)
        ...

    async def get(self, idx: uuid.UUID):
        try:
            data = await self.es.get(self.model.Config.es_index, idx)
            return self.model(**data['_source'])
        except NotFoundError:
            return


class QueriesManager:
    def __init__(self, model, **kwargs):
        self.model = model
