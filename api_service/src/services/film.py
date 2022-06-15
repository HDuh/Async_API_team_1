from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import ModelsController
from services import BaseDetailInfoService, BaseAllInfoService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


# TODO: Реализация Base класс, чтобы избежать дублирование кода
#  унести в него часть методов, общих для трех сервисов

# async def get_films_list(self, sort_param: str) -> Optional[list[Film]]:
#     films = await self._get_films_list_from_elastic(sort_param)
#     if not films:
#         return None
#     return films

# async def _get_films_list_from_elastic(self, sort_param: str) -> Optional[list[Film]]:
#     try:
#         query_body = {
#             "query": {
#                 "nested": {
#                     "path": "genre",
#                     "query": {
#                         "bool": {
#                             "must": [
#                                 {"match":
#                                      {"genre.name": "Adventure"}}
#                             ]
#                         }
#                     }
#                 }
#             }
#         }
#
#         query_body = {
#             "query": {
#                 "nested": {
#                     "path": "genre",
#                     "query": {
#                         "bool": {
#                             "must": [
#                                 {"match_all": {}}
#                             ]
#                         }
#                     }
#                 }
#             }
#         }
#         # TODO: подумать над параметром сортировки и как с ним работать
#         mapper = {
#             '-imdb_rating': "imdb_rating:desc",
#             'imdb_rating': "imdb_rating:asc"
#         }
#
#         sort = mapper.get(sort_param)
#
#         count_rows = await self.elastic.count(index='movies')
#
#         size = count_rows['count']
#         doc = await self.elastic.search(index="movies",
#                                         body=query_body,
#                                         sort=sort,
#                                         size=size)
#
#         result = [Film(**film['_source']) for film in doc['hits']['hits']]
#     except NotFoundError:
#         return None
#     return result

class FilmService(BaseDetailInfoService):
    index = 'movies'


class FilmsService(BaseAllInfoService):
    index = 'movies'


@lru_cache()
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticsearch = Depends(get_elastic), ) -> FilmService:
    return FilmService(redis, elastic)


@lru_cache()
def get_films_service(redis: Redis = Depends(get_redis),
                      elastic: AsyncElasticsearch = Depends(get_elastic), ) -> FilmsService:
    return FilmsService(redis, elastic)
