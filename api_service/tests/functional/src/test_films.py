from http import HTTPStatus
from random import choice

import pytest

from api.v1.schemas import FilmApiShortSchema, FilmApiSchema
from functional.utils import uuid_to_str


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_all_films(create_list_films, fastapi_client):
    """Тест на получение списка фильмов"""
    films = create_list_films
    expected_structure = [
        uuid_to_str(FilmApiShortSchema.build_from_model(film)).dict()
        for film in films
    ]
    response = await fastapi_client.get("/api_service/v1/films/")

    assert response.status_code == HTTPStatus.OK
    assert len(films) == len(response.json())
    assert expected_structure == response.json()


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_film_by_id(create_one_film, fastapi_client):
    """Тест на получение фильма по id"""
    film = create_one_film
    expected_structure = uuid_to_str(FilmApiSchema.build_from_model(film))
    response = await fastapi_client.get(f"/api_service/v1/films/{film.id}")

    assert response.status_code == HTTPStatus.OK
    assert film.id == response.json().get('id')
    assert expected_structure == response.json()


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_search_film(create_list_films, fastapi_client):
    """Тест на поиск в фильмах"""
    films = create_list_films
    film_for_find = choice(films)
    expected_structure = [uuid_to_str(FilmApiShortSchema.build_from_model(film_for_find)).dict()]
    response = await fastapi_client.get(f"/api_service/v1/films/search/?query={film_for_find.title}",
                                        follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert expected_structure == response.json()
