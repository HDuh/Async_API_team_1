import random
from http import HTTPStatus

import pytest

from .helpers_for_tests import BAD_ID_CASES, sorted_lists_for_tests_all
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
    expected_data, response_data = sorted_lists_for_tests_all(expected_structure, response.json())

    assert response.status_code == HTTPStatus.OK
    assert len(genres) == len(response.json())
    assert expected_data == response_data
    assert await redis_client.dbsize() == cache_size + 1


async def test_all_genres_pagination_size(create_list_genres_for_pagination, fastapi_client):
    """Тест на правильность размера пагинации"""
    _ = create_list_genres_for_pagination
    random_size = random.randint(1, 10)

    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page=1&page_size={random_size}")

    assert response.status_code == HTTPStatus.OK
    assert random_size == len(response.json())


@pytest.mark.parametrize("page_page", [0, float('inf'), 'some_page'])
@pytest.mark.parametrize("page_size", [0, float('inf'), 'some_size'])
async def test_all_genres_pagination_bad_cases(create_list_genres, fastapi_client, page_page, page_size):
    """Тест на нулевой размер страницы"""
    _ = create_list_genres
    response = await fastapi_client.get(f"/api_service/v1/genres/?page_page={page_page}&page_size={page_size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_genre_by_id(create_one_genre, fastapi_client, redis_client):
    """Тест на получение жанра по id"""
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/genres/{create_one_genre.id}")

    assert response.status_code == HTTPStatus.OK
    assert create_one_genre.id == response.json().get('id')
    assert await redis_client.dbsize() == cache_size + 1


@pytest.mark.parametrize("test_id, expected", BAD_ID_CASES)
async def test_genre_by_id_bad_cases(fastapi_client, test_id, expected):
    """Тест на несуществующий и некорректный id"""
    response = await fastapi_client.get(f"/api_service/v1/genres/{test_id}")
    assert response.status_code == expected
