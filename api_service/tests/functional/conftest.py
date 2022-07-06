import asyncio

import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import AsyncClient

from core import REDIS_CONFIG, PROJECT_NAME, ELASTIC_CONFIG
from functional.utils import clean_index
from src.main import app
from .settings import SERVICE_URL
from .testdata.factories import GenreFactory


# TODO: сделать глобальный teardown и в нем грохать индексы с test.


@pytest.fixture(scope='session', autouse=True)
async def es_client():
    client = AsyncElasticsearch(ELASTIC_CONFIG)
    yield client
    await client.close()


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def redis():
    redis.redis = await aioredis.from_url(REDIS_CONFIG, encoding='utf-8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis.redis), prefix=f'test_{PROJECT_NAME}_cache')
    yield redis.redis
    await redis.redis.close()


@pytest.fixture(scope='session')
async def fastapi_client():
    client = AsyncClient(app=app, base_url=SERVICE_URL)
    yield client
    await client.aclose()


# @pytest.fixture(scope='session', autouse=True)
# async def drop_indexes(es_client):
#     factories = (GenreFactory,)
#     yield
#     for factory in factories:
#         await es_client.indices.delete(index=factory.Meta.model.ModelConfig.es_index)


@pytest.fixture
async def create_list_genres():
    genres = await GenreFactory.async_create_batch(2)
    yield genres
    await clean_index(genres)


@pytest.fixture
async def create_one_genre():
    genre = await GenreFactory.async_create()
    yield genre
    await clean_index(genre)
