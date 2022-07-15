import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.main import app, models
from tests.functional.utils import clean_index, RoleTypes
from .settings import SERVICE_URL
from .testdata.factories import GenreFactory, FilmFactory, PersonFactory


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    """Фикстура получения коннекта redis"""
    client = await get_redis()
    yield client


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
@pytest.mark.asyncio
async def fastapi_client():
    """Фикстура создания клиента fastapi"""
    client = AsyncClient(app=app, base_url=SERVICE_URL)
    await app.router.startup()
    yield client
    await app.router.shutdown()
    await client.aclose()


@pytest_asyncio.fixture(scope='session', )
async def drop_indexes():
    """Фикстура удаления индексов из Elasticsearch после завершения тестирования"""
    yield
    es_client = await get_elastic()
    for model in models:
        await es_client.indices.delete(index=model.ModelConfig.es_index)


@pytest_asyncio.fixture(autouse=True)
async def drop_cache(redis_client):
    """Фикстура очистки кеша после каждого теста"""
    yield
    await redis_client.flushall()


@pytest_asyncio.fixture
async def create_list_genres():
    """Фикстура создания списка жанров"""
    genres = await GenreFactory.async_create_batch(10)
    yield genres
    await clean_index(genres)


@pytest_asyncio.fixture
async def create_one_genre():
    """Фикстура создания одного жанра"""
    genre = await GenreFactory.async_create()
    yield genre
    await clean_index(genre)


@pytest_asyncio.fixture
async def create_list_films():
    """Фикстура создания списка фильмов"""
    films = await FilmFactory.async_create_batch(10)
    yield films
    await clean_index(films)


@pytest_asyncio.fixture
async def create_one_film(create_list_genres, create_list_persons):
    """Фикстура для создания фильма. Для фильма создаются жанры и персоны.
    Передаются в фабрику фильмов для создания фильма"""
    genres = [genre.__dict__ for genre in create_list_genres]
    actors = [person.get_short() for person in create_list_persons if RoleTypes.ACTOR.value in person.role]
    writers = [person.get_short() for person in create_list_persons if RoleTypes.WRITER.value in person.role]
    directors = [person.get_short() for person in create_list_persons if RoleTypes.DIRECTOR.value in person.role]
    film = await FilmFactory.async_create(genre=genres, actors=actors, writers=writers, directors=directors)

    yield film
    await clean_index(film)


@pytest_asyncio.fixture
async def create_one_person(create_list_films):
    """Фикстура создания одной персоны с привязанными к ней фильмами"""
    films = create_list_films
    film_ids = [film.id for film in films]
    person = await PersonFactory.async_create(film_ids=film_ids)
    yield person
    await clean_index(person)


@pytest_asyncio.fixture
async def create_list_persons():
    """Фикстура создания списка персон"""
    persons = await PersonFactory.async_create_batch(10)
    yield persons
    await clean_index(persons)
