import json

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models import ModelsController

CACHE_EXPIRE_IN_SECONDS = 300


class BaseAllInfoService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.redis = redis
        self.elastic = elastic
        self.index = index

    async def get_all_data(self):
        """Процесс получения всех данных"""
        all_data = await self.get_all_data_from_cache()
        if not all_data:
            all_data = await self.get_all_data_from_elastic()
            if not all_data:
                return
            await self.put_all_to_cache(all_data)
        return all_data

    async def get_all_data_from_cache(self):
        """Получение всех данных из кэша"""
        data = await self.redis.get(f'all_{self.index}')
        if not data:
            return
        model = ModelsController[self.index].value
        result = [model.parse_raw(item) for item in json.loads(data)]
        return result

    async def get_all_data_from_elastic(self):
        """Получение всех данных из эластика"""
        try:
            doc = await self.elastic.search(index=self.index, body={'query': {'match_all': {}}})
        except NotFoundError:
            return
        model = ModelsController[self.index].value
        return [model(**item['_source']) for item in doc['hits']['hits']]

    async def put_all_to_cache(self, all_data):
        await self.redis.set(f'all_{self.index}',
                             json.dumps([item.json() for item in all_data]),
                             expire=CACHE_EXPIRE_IN_SECONDS)
