from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

# TODO: Реализация Base класс, чтобы избежать дублирование кода
#  унести в него часть методов, общих для трех сервисов


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films_list(self, sort_param: str) -> Optional[list[Film]]:
        films = await self._get_films_list_from_elastic(sort_param)
        if not films:
            return None
        return films

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # TODO: временно убранный кэш
        # film = await self._film_from_cache(film_id)
        film = None
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _get_films_list_from_elastic(self, sort_param: str) -> Optional[list[Film]]:
        try:
            # query_body = {
            #     "query": {
            #         "nested": {
            #             "path": "genre",
            #             "query": {
            #                 "bool": {
            #                     "must": [
            #                         {"match":
            #                              {"genre.name": "Adventure"}}
            #                     ]
            #                 }
            #             }
            #         }
            #     }
            # }

            query_body = {
                "query": {
                    "nested": {
                        "path": "genre",
                        "query": {
                            "bool": {
                                "must": [
                                    {"match_all": {}}
                                ]
                            }
                        }
                    }
                }
            }
            # TODO: подумать над параметром сортировки и как с ним работать
            mapper = {
                '-imdb_rating': "imdb_rating:desc",
                'imdb_rating': "imdb_rating:asc"
            }

            sort = mapper.get(sort_param)

            count_rows = await self.elastic.count(index='movies')

            size = count_rows['count']
            doc = await self.elastic.search(index="movies",
                                            body=query_body,
                                            sort=sort,
                                            size=size)

            result = [Film(**film['_source']) for film in doc['hits']['hits']]
        except NotFoundError:
            return None
        return result

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
