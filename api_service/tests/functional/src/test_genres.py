import random
import uuid
from http import HTTPStatus

import pytest

from src.api.v1.schemas import GenreApiSchema
from tests.functional.utils import uuid_to_str

pytestmark = pytest.mark.asyncio


async def test_all_genres(create_list_genres, fastapi_client, redis_client):
    """Тест на получение списка жанров"""
    genres = create_list_genres
    expected_structure = [
        uuid_to_str(GenreApiSchema.build_from_model(genre)).__dict__
        for genre in genres
    ]
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get("/api_service/v1/genres/")
    response_sorted_list = sorted(response.json(), key=lambda d: d['name'])
    expected_sorted_list = sorted(expected_structure, key=lambda d: d['name'])

    assert response.status_code == HTTPStatus.OK
    assert len(genres) == len(response.json())
    assert expected_sorted_list == response_sorted_list
    assert await redis_client.dbsize() == cache_size + 1


async def test_genre_by_id(create_one_genre, fastapi_client, redis_client):
    cache_size = await redis_client.dbsize()
async def test_all_genres_pagination_size(create_list_genres, fastapi_client):
    """Тест на правильность размера пагинации"""
    _ = create_list_genres
    random_size = random.randint(1, 10)

    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page=1&page_size={random_size}")

    assert response.status_code == HTTPStatus.OK
    assert random_size == len(response.json())


async def test_all_genres_pagination_page(create_list_genres, fastapi_client):
    """Тест на правильность данных на странице"""
    genres = create_list_genres
    expected_structure = [
        uuid_to_str(GenreApiSchema.build_from_model(genre)).__dict__
        for genre in genres
    ]
    page = 4
    page_size = 2
    from_ = 0 if page == 1 else (page - 1) * page_size
    page_structure = expected_structure[from_:from_+page_size]

    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page={page}&page_size={page_size}")

    assert response.status_code == HTTPStatus.OK
    assert page_structure == response.json()


async def test_all_genres_pagination_zero_size(create_list_genres, fastapi_client):
    """Тест на нулевой размер страницы"""
    _ = create_list_genres
    response = await fastapi_client.get("/api_service/v1/genres/?page_page=1&page_size=0")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_genres_pagination_zero_page(create_list_genres, fastapi_client):
    """Тест на нулевую страницу"""
    _ = create_list_genres
    response = await fastapi_client.get("/api_service/v1/genres/?page_page=0&page_size=5")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_genres_pagination_inf_page(create_list_genres, fastapi_client):
    """Тест на бесконечную страницу"""
    _ = create_list_genres
    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page={float('inf')}&page_size=5")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_genres_pagination_inf_size(create_list_genres, fastapi_client):
    """Тест на бесконечный размер страницы"""
    _ = create_list_genres
    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page=2&page_size={float('inf')}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_genres_pagination_incorrect_size(create_list_genres, fastapi_client):
    """Тест на некорректное значение размера страницы"""
    _ = create_list_genres
    response = await fastapi_client.get("/api_service/v1/genres/?page_page=2&page_size=some_sting")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_all_genres_pagination_incorrect_page(create_list_genres, fastapi_client):
    """Тест на некорректное значение страницы"""
    _ = create_list_genres
    response = await fastapi_client.get("/api_service/v1/genres/?page_page=some_string&page_size=4")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_genre_by_id(create_one_genre, fastapi_client, redis):
    """Тест на получение жанра по id"""
    cache_size = await redis.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/genres/{create_one_genre.id}")

    assert response.status_code == HTTPStatus.OK
    assert create_one_genre.id == response.json().get('id')
    assert await redis_client.dbsize() == cache_size + 1


async def test_genre_by_id_not_exist(fastapi_client):
    """Тест на несуществующий id"""
    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/genres/{test_id}")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND


async def test_genre_by_id_incorrect(fastapi_client):
    """Тест на некорректный id"""
    bad_response = await fastapi_client.get("/api_service/v1/genres/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
