from http import HTTPStatus

import pytest

from src.api.v1.schemas import GenreApiSchema
from tests.functional.utils import uuid_to_str


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_all_genres(create_list_genres, fastapi_client):
    genres = create_list_genres
    expected_structure = [
        uuid_to_str(GenreApiSchema.build_from_model(genre)).__dict__
        for genre in genres
    ]
    response = await fastapi_client.get("/api_service/v1/genres/")

    assert response.status_code == HTTPStatus.OK
    assert len(genres) == len(response.json())
    assert expected_structure == response.json()


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_genre_by_id(create_one_genre, fastapi_client):
    response = await fastapi_client.get(f"/api_service/v1/genres/{create_one_genre.id}")

    assert response.status_code == HTTPStatus.OK
    assert create_one_genre.id == response.json().get('id')
