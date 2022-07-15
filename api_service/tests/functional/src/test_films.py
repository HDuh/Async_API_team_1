import uuid
from http import HTTPStatus
import random

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
    expected_sorted_list = sorted(expected_structure, key=lambda d: -d['imdb_rating'])
    page = random.randint(1, 4)
    page_size = 2
    from_ = 0 if page == 1 else (page - 1) * page_size
    page_structure = expected_sorted_list[from_:from_+page_size]

    response = await fastapi_client.get(f"/api_service/v1/films/?sort=-imdb_rating&page_page={page}&page_size={page_size}")

    assert response.status_code == HTTPStatus.OK
    assert len(page_structure) == len(response.json())


async def test_all_films_pagination_zero_size(create_list_films, fastapi_client):
    """Тест на нулевой размер страницы"""
    _ = create_list_films
    response = await fastapi_client.get("/api_service/v1/films/?page_page=1&page_size=0")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_films_pagination_zero_page(create_list_films, fastapi_client):
    """Тест на нулевую страницу"""
    _ = create_list_films
    response = await fastapi_client.get("/api_service/v1/films/?page_page=0&page_size=5")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_films_pagination_inf_page(create_list_films, fastapi_client):
    """Тест на бесконечную страницу"""
    _ = create_list_films
    response = await fastapi_client.get(f"/api_service/v1/films/?page_page={float('inf')}&page_size=5")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_films_pagination_inf_size(create_list_films, fastapi_client):
    """Тест на бесконечный размер страницы"""
    _ = create_list_films
    response = await fastapi_client.get(f"/api_service/v1/films/?page_page=2&page_size={float('inf')}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_films_pagination_incorrect_size(create_list_films, fastapi_client):
    """Тест на некорректное значение размера страницы"""
    _ = create_list_films
    response = await fastapi_client.get("/api_service/v1/films/?page_page=2&page_size=some_sting")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_films_pagination_incorrect_page(create_list_films, fastapi_client):
    """Тест на некорректное значение страницы"""
    _ = create_list_films
    response = await fastapi_client.get("/api_service/v1/films/?page_page=some_string&page_size=4")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_film_by_id(create_one_film, fastapi_client, redis):
    """Тест на получение фильма по id"""
    film = create_one_film
    expected_structure = uuid_to_str(FilmApiSchema.build_from_model(film))
    cache_size = await redis_client.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/films/{film.id}")

    assert response.status_code == HTTPStatus.OK
    assert film.id == response.json().get('id')
    assert expected_structure == response.json()
    assert await redis_client.dbsize() == cache_size + 1


async def test_film_by_id_not_exist(fastapi_client):
    """Тест на несуществующий id"""
    test_id = uuid.uuid4()

    not_exist_response = await fastapi_client.get(f"/api_service/v1/films/{test_id}")

    assert not_exist_response.status_code == HTTPStatus.NOT_FOUND


async def test_film_by_id_incorrect(fastapi_client):
    """Тест на некорректный id"""
    bad_response = await fastapi_client.get("/api_service/v1/films/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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
    assert expected[0] == response.json()[0]
    assert expected[-1] == response.json()[-1]


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
    assert expected[0] == response.json()[0]
    assert expected[-1] == response.json()[-1]
