import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models import ModelsController

CACHE_EXPIRE_IN_SECONDS = 300


# TODO: при записи в кэш учитывать параметр сортировки и фильтрации (all_films_sorted_filter)
class BaseAllInfoService:
    index = None

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all_data(self, sort: str = None):
        """Процесс получения всех данных"""
        all_data = await self.get_all_data_from_cache()
        if not all_data:
            all_data = await self.get_all_data_from_elastic(sort=sort)
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
        result = [model.parse_raw(item) for item in orjson.loads(data)]
        return result

    # TODO: для того чтобы реализовать сортирку и фильтрацию в классах FilmsService, Persons, Genres переопределить данный метод.
    async def get_all_data_from_elastic(self, filter: str = None, sort: str = None):
        # page_size: int, page_number: int, sorting: str, filter: str
        """Получение всех данных из эластика"""
        try:
            doc = await self.elastic.search(index=self.index, body={'query': {'match_all': {}}})
        except NotFoundError:
            return
        model = ModelsController[self.index].value
        return [model(**item['_source']) for item in doc['hits']['hits']]

    async def put_all_to_cache(self, all_data):
        await self.redis.set(f'all_{self.index}',
                             orjson.dumps([item.json() for item in all_data]).decode('utf-8'),
                             expire=CACHE_EXPIRE_IN_SECONDS)
