from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models import ModelsController

CACHE_EXPIRE_IN_SECONDS = 300


class BaseDetailInfoService:
    index = None

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        # self.index = index

    async def get_by_id(self, idx):
        """Получение данных по id"""
        data = await self.get_from_cache(idx)
        if not data:
            data = await self.get_from_elastic(idx)
            if not data:
                return
            await self.put_to_cache(data)
        return data

    async def get_from_cache(self, idx):
        """Получение данных из кэша"""
        data = await self.redis.get(idx)
        if not data:
            return
        model = ModelsController[self.index].value
        result = model.parse_raw(data)
        return result

    async def get_from_elastic(self, idx):
        """Получение данных из эластика"""
        try:
            doc = await self.elastic.get(self.index, idx)
        except NotFoundError:
            return
        model = ModelsController[self.index].value
        return model(**doc['_source'])

    async def put_to_cache(self, model):
        await self.redis.set(model.id, model.json(), expire=CACHE_EXPIRE_IN_SECONDS)
