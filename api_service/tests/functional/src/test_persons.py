import uuid
from http import HTTPStatus
from random import choice

import pytest

from src.api.v1.schemas import PersonApiSchema, PersonFilmApiSchema
from tests.functional.utils import uuid_to_str

pytestmark = pytest.mark.asyncio


async def test_all_persons(create_list_persons, fastapi_client, redis):
    """Тест на получение списка персон"""
    persons = create_list_persons
    expected_structure = [
        uuid_to_str(PersonApiSchema.build_from_model(person)).__dict__
        for person in persons
    ]
    cache_size = await redis.dbsize()
    response = await fastapi_client.get("/api_service/v1/persons/")

    response_sorted_list = sorted(response.json(), key=lambda d: d['full_name'])
    expected_sorted_list = sorted(expected_structure, key=lambda d: d['full_name'])

    assert response.status_code == HTTPStatus.OK
    assert len(persons) == len(response.json())
    assert response_sorted_list == expected_sorted_list
    assert await redis.dbsize() == cache_size + 1


async def test_person_by_id(create_one_person, fastapi_client, redis):
    """Тест на получение персоны по id"""
    person = create_one_person
    expected_structure = uuid_to_str(PersonApiSchema.build_from_model(person))
    cache_size = await redis.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/persons/{person.id}")

    assert response.status_code == HTTPStatus.OK
    assert person.id == response.json().get('id')
    assert expected_structure == response.json()
    assert await redis.dbsize() == cache_size + 1

    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/persons/{test_id}")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND

    bad_response = await fastapi_client.get("/api_service/v1/persons/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_search_film(create_list_persons, fastapi_client, redis):
    """Тест на поиск в персонах"""
    persons = create_list_persons
    person_for_find = choice(persons)
    expected_structure = [uuid_to_str(PersonApiSchema.build_from_model(person_for_find)).__dict__]
    cache_size = await redis.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/persons/search/?query={person_for_find.full_name}",
                                        follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert response.json() >= expected_structure
    assert await redis.dbsize() == cache_size + 1

    bad_response = await fastapi_client.get("/api_service/v1/persons/search/?query=test_name",
                                            follow_redirects=True)
    assert bad_response.status_code == HTTPStatus.NOT_FOUND


async def test_person_films_by_id(create_one_film, fastapi_client, redis):
    """Тест на получение фильма по id персоны"""
    film = create_one_film
    persons_ids = [
        person['id']
        for role in ('actors', 'writers', 'directors')
        for person in film.__dict__[role]
        if film.__dict__.get(role)
    ]
    selected_person_id = choice(persons_ids)
    expected_structure = [uuid_to_str(PersonFilmApiSchema.build_from_model(film)).__dict__]
    cache_size = await redis.dbsize()
    response = await fastapi_client.get(f"/api_service/v1/persons/{selected_person_id}/film")

    assert response.status_code == HTTPStatus.OK
    assert expected_structure == response.json()
    assert await redis.dbsize() == cache_size + 1

    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/persons/{test_id}/film")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND

    bad_response = await fastapi_client.get("/api_service/v1/persons/test_some_id/film")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY