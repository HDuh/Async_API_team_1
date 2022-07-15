import random
from http import HTTPStatus

import pytest

from src.api.v1.schemas import FilmApiShortSchema, FilmApiSchema
from tests.functional.utils import uuid_to_str
from .helpers_for_tests import BAD_ID_CASES, get_page_from_structure, sorted_lists_for_tests_all

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
    expected_data, response_data, = sorted_lists_for_tests_all(expected_structure, response.json())

    assert response.status_code == HTTPStatus.OK
    assert len(films) == len(response.json())
    assert expected_data == response_data
    assert await redis_client.dbsize() == cache_size + 1


async def test_all_films_pagination_size(create_list_films, fastapi_client):
    """Тест на правильность размера пагинаци"""
    _ = create_list_films
    random_size = random.randint(1, 10)

    response = await fastapi_client.get(f"/api_service/v1/films/?page_page=1&page_size={random_size}")

    assert response.status_code == HTTPStatus.OK
    assert random_size == len(response.json())


async def test_all_films_pagination_page(create_list_films, fastapi_client):
    """Тест на правильность данных на странице"""
    films = create_list_films
    expected_structure = [
        uuid_to_str(FilmApiShortSchema.build_from_model(film)).__dict__
        for film in films
    ]
    page = random.randint(1, 5)
    page_size = 2
    expected_page_content = get_page_from_structure(page=page,
                                                    size=page_size,
                                                    structure=expected_structure)

    response = await fastapi_client.get(f"/api_service/v1/films/?"
                                        f"sort=-imdb_rating&page_page={page}&page_size={page_size}")

    assert response.status_code == HTTPStatus.OK
    assert expected_page_content == response.json()


@pytest.mark.parametrize("page_page", [0, float('inf'), 'some_page'])
@pytest.mark.parametrize("page_size", [0, float('inf'), 'some_size'])
async def test_all_films_pagination_bad_cases(create_list_films, fastapi_client, page_page, page_size):
    """Тест на нулевой размер страницы"""
    _ = create_list_films
    response = await fastapi_client.get(f"/api_service/v1/films/?page_page={page_page}&page_size={page_size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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


@pytest.mark.parametrize("test_id, expected", BAD_ID_CASES)
async def test_films_by_id_bad_cases(fastapi_client, test_id, expected):
    """Тест на несуществующий и некорректный id"""
    response = await fastapi_client.get(f"/api_service/v1/films/{test_id}")
    assert response.status_code == expected


async def test_search_film(create_list_films, fastapi_client, redis_client):
    """Тест на поиск в фильмах"""
    films = create_list_films
    film_for_find = random.choice(films)
    expected_structure = [uuid_to_str(FilmApiShortSchema.build_from_model(film_for_find)).__dict__]
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/films/search/?query={film_for_find.title}",
                                        follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert response.json() >= expected_structure
    assert await redis_client.dbsize() == cache_size + 1


async def test_search_film_not_exist(fastapi_client):
    """Тест на поиск несуществующего рез-та в фильмах"""
    bad_response = await fastapi_client.get(f"/api_service/v1/films/search/?query=test_data",
                                            follow_redirects=True)
    assert bad_response.status_code == HTTPStatus.NOT_FOUND


async def test_all_films_sort_asc(create_list_films, fastapi_client):
    """Тест на правильность сортировки фильмов по возрастанию"""
    films = create_list_films
    expected_structure = [
        uuid_to_str(FilmApiShortSchema.build_from_model(film)).__dict__
        for film in films
    ]
    expected = sorted(expected_structure, key=lambda d: d['imdb_rating'])

    response = await fastapi_client.get(f"/api_service/v1/films/?sort=imdb_rating")

    assert response.status_code == HTTPStatus.OK
    assert expected == response.json()


async def test_all_films_sort_desc(create_list_films, fastapi_client):
    """Тест на правильность сортировки фильмов по убыванию"""
    films = create_list_films
    expected_structure = [
        uuid_to_str(FilmApiShortSchema.build_from_model(film)).__dict__
        for film in films
    ]
    expected = sorted(expected_structure, key=lambda d: -d['imdb_rating'])

    response = await fastapi_client.get(f"/api_service/v1/films/?sort=-imdb_rating")

    assert response.status_code == HTTPStatus.OK
    assert expected == response.json()


async def test_all_films_sort_incorrect(fastapi_client):
    """Тест на несуществующий параметр сортировки"""
    response = await fastapi_client.get(f"/api_service/v1/films/?sort=incorrect_sort")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
