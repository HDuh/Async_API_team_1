from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from .base_detail_service import BaseDetailInfoService
from .base_all_info_service import BaseAllInfoService
from db.elastic import get_elastic
from db.redis import get_redis


class GenreService(BaseDetailInfoService):
    pass


class GenresService(BaseAllInfoService):
    pass


@lru_cache()
def get_genre_service(redis: Redis = Depends(get_redis),
                      elastic: AsyncElasticsearch = Depends(get_elastic), ) -> GenreService:
    return GenreService(redis, elastic, 'genres')


@lru_cache()
def get_genres_service(redis: Redis = Depends(get_redis),
                       elastic: AsyncElasticsearch = Depends(get_elastic), ) -> GenresService:
    return GenresService(redis, elastic, 'genres')
