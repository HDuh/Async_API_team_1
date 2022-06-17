import uuid
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import ModelsController
from queries_to_elastic import get_genre_id_filter
from services import BaseDetailInfoService, BaseAllInfoService

FILM_CACHE_EXPIRE_IN_SECONDS = 300  # 5 минут

#
# class FilmService(BaseDetailInfoService):
#     index = 'movies'


class FilmsService(BaseAllInfoService):
    index = 'movies'

    # # TODO: как сделать универсальный фильтр? - никак. Избегаем божественности
    # async def get_all_data_from_elastic(self, sort: str = None, genre_id: uuid.UUID = None):
    #     query_body = self.query_body
    #     if genre_id:
    #         query_body['query'] = get_genre_id_filter(genre_id)
    #     try:
    #         doc = await self.elastic.search(index=self.index, body=query_body, sort=sort)
    #     except NotFoundError:
    #         return
    #     model = ModelsController[self.index].value
    #     return [model(**item['_source']) for item in doc['hits']['hits']]

#
# @lru_cache()
# def get_film_service(redis: Redis = Depends(get_redis),
#                      elastic: AsyncElasticsearch = Depends(get_elastic), ) -> FilmService:
#     return FilmService(redis, elastic)


@lru_cache()
def get_films_service(redis: Redis = Depends(get_redis),
                      elastic: AsyncElasticsearch = Depends(get_elastic), ) -> FilmsService:
    return FilmsService(redis, elastic)
