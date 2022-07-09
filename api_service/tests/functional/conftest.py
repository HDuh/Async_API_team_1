import asyncio
from random import randint

import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import AsyncClient

from core import REDIS_CONFIG, PROJECT_NAME, ELASTIC_CONFIG
from functional.utils import clean_index, RoleTypes
from models import Genre, Film, Person
from src.main import app
from .settings import SERVICE_URL
from .testdata.factories import GenreFactory, FilmFactory, PersonFactory


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


@pytest.fixture(scope='session', autouse=True)
async def drop_indexes(es_client):
    models = (Genre, Film, Person,)
    yield
    for model in models:
        await es_client.indices.delete(index=model.ModelConfig.es_index)


@pytest.fixture
async def create_list_genres():
    genres = await GenreFactory.async_create_batch(randint(1, 10))
    yield genres
    await clean_index(genres)


@pytest.fixture
async def create_one_genre():
    genre = await GenreFactory.async_create()
    yield genre
    await clean_index(genre)


@pytest.fixture
async def create_list_films():
    films = await FilmFactory.async_create_batch(randint(1, 10))
    yield films
    await clean_index(films)


@pytest.fixture
async def create_one_film(create_list_genres, create_list_persons):
    """Фикстура для создания фильма. Для фильма создаются жанры и персоны.
    Передаются в фабрику фильмов для создания фильма"""
    genres = [genre.__dict__ for genre in create_list_genres]
    actors = [person.get_short() for person in create_list_persons if person.role == RoleTypes.ACTOR]
    writers = [person.get_short() for person in create_list_persons if person.role == RoleTypes.WRITER]
    directors = [person.get_short() for person in create_list_persons if person.role == RoleTypes.DIRECTOR]
    film = await FilmFactory.async_create(genre=genres, actors=actors, writers=writers, directors=directors)

    yield film
    await clean_index(film)


@pytest.fixture
async def create_one_person():
    person = await PersonFactory.async_create()
    yield person
    await clean_index(person)


@pytest.fixture
async def create_list_persons():
    persons = await PersonFactory.async_create_batch(randint(3, 10))
    yield persons
    await clean_index(persons)
