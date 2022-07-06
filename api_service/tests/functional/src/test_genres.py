from http import HTTPStatus

import pytest


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_all_genrs(create_list_genres, fastapi_client):
    expected_structure = [genre.__dict__ for genre in create_list_genres]
    response = await fastapi_client.get("/api_service/v1/genres/")

    assert response.status_code == HTTPStatus.OK
    assert len(create_list_genres) == len(response.json())
    assert expected_structure == response.json()


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_genre_by_id(create_one_genre, fastapi_client):
    response = await fastapi_client.get(f"/api_service/v1/genres/{create_one_genre.id}")

    assert response.status_code == HTTPStatus.OK
    assert create_one_genre.id == response.json().get('id')
