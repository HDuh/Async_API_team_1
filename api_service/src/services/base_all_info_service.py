import uuid

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from orjson import loads, dumps

from models import ModelsController
from queries_to_elastic import get_genre_id_filter

CACHE_EXPIRE_IN_SECONDS = 10


class BaseAllInfoService:
    index = None

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.query_body = {'query': {'match_all': {}}}

    async def get_all_data(self, sort: str = None,
                           genre_id: uuid.UUID = None,
                           person_id: uuid.UUID = None) -> list | None:
        """Процесс получения всех данных"""
        if sort:
            sort = f'{sort[1:]}:desc' if sort.startswith('-') else f'{sort}:asc'

        all_data = await self.get_all_data_from_cache(sort, genre_id, person_id)
        if not all_data:
            all_data = await self.get_all_data_from_elastic(sort=sort, genre_id=genre_id, person_id=person_id)
            if not all_data:
                return
            await self.put_all_to_cache(all_data, sort, genre_id, person_id)
        return all_data

    async def get_all_data_from_cache(self, *args):
        """Получение всех данных из кэша"""
        key = self.__generate_key(*args)
        data = await self.redis.get(key)
        if not data:
            return
        model = ModelsController[self.index].value
        result = [model.parse_raw(item) for item in loads(data)]
        return result

    async def get_all_data_from_elastic(self, sort: str = None,
                                        genre_id: uuid.UUID = None,
                                        person_id: uuid.UUID = None) -> list or None:
        """Получение всех данных из эластика"""
        if genre_id:
            self.query_body['query'] = get_genre_id_filter(genre_id)
        if person_id:
            ...
        try:
            doc = await self.elastic.search(index=self.index, body=self.query_body, sort=sort)
        except NotFoundError:
            return
        model = ModelsController[self.index].value
        return [model(**item['_source']) for item in doc['hits']['hits']]

    async def put_all_to_cache(self, all_data: list, *args) -> None:
        """Кэширование данных"""
        key = self.__generate_key(*args)
        await self.redis.set(key, dumps([item.json() for item in all_data]).decode('utf-8'),
                             expire=CACHE_EXPIRE_IN_SECONDS)

    def __generate_key(self, *args):
        """Генерирование ключа для кэширования"""
        key = f'all_{self.index}'
        for parameter in args:
            if parameter:
                key += f'_{parameter}'
        return key
