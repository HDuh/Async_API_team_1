import uuid
from http import HTTPStatus
from random import choice

import pytest

from src.api.v1.schemas import FilmApiShortSchema, FilmApiSchema
from tests.functional.utils import uuid_to_str

pytestmark = pytest.mark.asyncio


async def test_all_films(create_list_films, fastapi_client, redis_client):
    """Тест на получение списка фильмов"""
    films = create_list_films
    expected_structure = [
        uuid_to_str(FilmApiShortSchema.build_from_model(film)).__dict__
        for film in films
    ]
    cache_size = await redis_client.dbsize()
    response = await fastapi_client.get("/api_service/v1/films/")
    response_sorted_list = sorted(response.json(), key=lambda d: d['id'])
    expected_sorted_list = sorted(expected_structure, key=lambda d: d['id'])

    assert response.status_code == HTTPStatus.OK
    assert len(films) == len(response.json())
    assert expected_sorted_list == response_sorted_list
    assert await redis_client.dbsize() == cache_size + 1


async def test_film_by_id(create_one_film, fastapi_client, redis_client):
    """Тест на получение фильма по id"""
    film = create_one_film
    expected_structure = uuid_to_str(FilmApiSchema.build_from_model(film))
    cache_size = await redis_client.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/films/{film.id}")

    assert response.status_code == HTTPStatus.OK
    assert film.id == response.json().get('id')
    assert expected_structure == response.json()
    assert await redis_client.dbsize() == cache_size + 1

    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/films/{test_id}")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND

    bad_response = await fastapi_client.get("/api_service/v1/films/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_search_film(create_list_films, fastapi_client, redis_client):
    """Тест на поиск в фильмах"""
    films = create_list_films
    film_for_find = choice(films)
    expected_structure = [uuid_to_str(FilmApiShortSchema.build_from_model(film_for_find)).__dict__]
    cache_size = await redis_client.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/films/search/?query={film_for_find.title}",
                                        follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert response.json() >= expected_structure
    assert await redis_client.dbsize() == cache_size + 1

    bad_response = await fastapi_client.get(f"/api_service/v1/films/search/?query=test_data",
                                            follow_redirects=True)

    assert bad_response.status_code == HTTPStatus.NOT_FOUND
