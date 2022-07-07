from http import HTTPStatus

import pytest

from api.v1.schemas import FilmApiShortSchema


@pytest.mark.anyio
@pytest.mark.asyncio
async def test_all_films(create_list_films, fastapi_client):
    expected_structure = [FilmApiShortSchema.build_from_model(film).__dict__ for film in create_list_films]
    print(1)
    response = await fastapi_client.get("/api_service/v1/films/")
    #
    assert response.status_code == HTTPStatus.OK
    assert len(create_list_films) == len(response.json())
    assert expected_structure == response.json()


# @pytest.mark.anyio
# @pytest.mark.asyncio
# async def test_genre_by_id(create_one_film, fastapi_client):
#     response = await fastapi_client.get(f"/api_service/v1/films/{create_one_film.id}")
#
#     assert response.status_code == HTTPStatus.OK
#     assert create_one_film.id == response.json().get('id')
