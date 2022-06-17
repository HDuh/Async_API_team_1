from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from .base_detail_service import BaseDetailInfoService
from .base_all_info_service import BaseAllInfoService
from db.elastic import get_elastic
from db.redis import get_redis

#
# class PersonService(BaseDetailInfoService):
#     index = 'persons'


class PersonsService(BaseAllInfoService):
    index = 'persons'


# @lru_cache()
# def get_person_service(redis: Redis = Depends(get_redis),
#                        elastic: AsyncElasticsearch = Depends(get_elastic), ) -> PersonService:
#     return PersonService(redis, elastic)


@lru_cache()
def get_persons_service(redis: Redis = Depends(get_redis),
                        elastic: AsyncElasticsearch = Depends(get_elastic), ) -> PersonsService:
    return PersonsService(redis, elastic)
