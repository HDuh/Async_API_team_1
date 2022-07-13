import uuid
from http import HTTPStatus

import pytest

from src.api.v1.schemas import GenreApiSchema
from tests.functional.utils import uuid_to_str

pytestmark = pytest.mark.asyncio


async def test_all_genres(create_list_genres, fastapi_client, redis):

    genres = create_list_genres
    expected_structure = [
        uuid_to_str(GenreApiSchema.build_from_model(genre)).__dict__
        for genre in genres
    ]
    cache_size = await redis.dbsize()
    response = await fastapi_client.get("/api_service/v1/genres/")

    response_sorted_list = sorted(response.json(), key=lambda d: d['name'])
    expected_sorted_list = sorted(expected_structure, key=lambda d: d['name'])

    assert response.status_code == HTTPStatus.OK
    assert len(genres) == len(response.json())
    assert expected_sorted_list == response_sorted_list
    assert await redis.dbsize() == cache_size + 1


async def test_genre_by_id(create_one_genre, fastapi_client, redis):
    cache_size = await redis.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/genres/{create_one_genre.id}")

    assert response.status_code == HTTPStatus.OK
    assert create_one_genre.id == response.json().get('id')
    assert await redis.dbsize() == cache_size + 1

    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/genres/{test_id}")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND

    bad_response = await fastapi_client.get("/api_service/v1/genres/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
