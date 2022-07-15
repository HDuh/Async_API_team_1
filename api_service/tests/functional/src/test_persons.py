import random
import uuid
from http import HTTPStatus

import pytest

from .helpers_for_tests import BAD_ID_CASES, sorted_lists_for_tests_all
from src.api.v1.schemas import PersonApiSchema, PersonFilmApiSchema
from tests.functional.utils import uuid_to_str

pytestmark = pytest.mark.asyncio


async def test_all_persons(create_list_persons, fastapi_client, redis_client):
    """Тест на получение списка персон"""
    persons = create_list_persons
    expected_structure = [
        uuid_to_str(PersonApiSchema.build_from_model(person)).__dict__
        for person in persons
    ]
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get("/api_service/v1/persons/")
    expected_data, response_data = sorted_lists_for_tests_all(expected_structure, response.json())

    assert response.status_code == HTTPStatus.OK
    assert len(persons) == len(response.json())
    assert expected_data == response_data
    assert await redis_client.dbsize() == cache_size + 1


async def test_person_by_id(create_one_person, fastapi_client, redis_client):
    """Тест на получение персоны по id"""
    person = create_one_person
    expected_structure = uuid_to_str(PersonApiSchema.build_from_model(person))
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/persons/{person.id}")

    assert response.status_code == HTTPStatus.OK
    assert person.id == response.json().get('id')
    assert expected_structure == response.json()
    assert await redis_client.dbsize() == cache_size + 1


async def test_all_persons_pagination_size(create_list_persons_for_pagination, fastapi_client):
    """Тест на правильность размера пагинаци"""
    _ = create_list_persons_for_pagination
    random_size = random.randint(1, 10)

    response = await fastapi_client.get(f"/api_service/v1/persons/?page_page=1&page_size={random_size}")

    assert response.status_code == HTTPStatus.OK
    assert random_size == len(response.json())


async def test_all_persons_pagination_page(create_list_persons_for_pagination, fastapi_client):
    """Тест на правильность данных на странице"""
    persons = create_list_persons_for_pagination
    expected_structure = [
        uuid_to_str(PersonApiSchema.build_from_model(person)).__dict__
        for person in persons
    ]
    page = random.randint(1, 4)
    page_size = 2
    from_ = 0 if page == 1 else (page - 1) * page_size
    page_structure = expected_structure[from_:from_+page_size]

    response = await fastapi_client.get(f"/api_service/v1/persons/?page_page={page}&page_size={page_size}")

    assert response.status_code == HTTPStatus.OK
    assert len(page_structure) == len(response.json())


@pytest.mark.parametrize("page_page", [0, float('inf'), 'some_page'])
@pytest.mark.parametrize("page_size", [0, float('inf'), 'some_size'])
async def test_all_persons_pagination_bad_cases(create_list_persons, fastapi_client, page_page, page_size):
    """Тест на нулевой размер страницы"""
    _ = create_list_persons
    response = await fastapi_client.get(f"/api_service/v1/persons/?page_page={page_page}&page_size={page_size}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_person_by_id_not_exist(fastapi_client):
    """Тест на несуществующий id"""
    test_id = uuid.uuid4()
    bad_response = await fastapi_client.get(f"/api_service/v1/persons/{test_id}")
    assert bad_response.status_code == HTTPStatus.NOT_FOUND


async def test_person_by_id_incorrect(fastapi_client):
    """Тест на некорректный id"""
    bad_response = await fastapi_client.get("/api_service/v1/persons/test_data")
    assert bad_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_search_film(create_list_persons, fastapi_client, redis_client):
    """Тест на поиск в персонах"""
    persons = create_list_persons
    person_for_find = random.choice(persons)
    expected_structure = [uuid_to_str(PersonApiSchema.build_from_model(person_for_find)).__dict__]
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/persons/search/?"
                                        f"query={person_for_find.full_name}",
                                        follow_redirects=True)

    assert response.status_code == HTTPStatus.OK
    assert response.json() >= expected_structure
    assert await redis_client.dbsize() == cache_size + 1


async def test_search_film_not_exist(fastapi_client):
    """Тест на поиск несуществующего рез-та в персонах"""
    bad_response = await fastapi_client.get("/api_service/v1/persons/search/?query=test_name",
                                            follow_redirects=True)
    assert bad_response.status_code == HTTPStatus.NOT_FOUND


async def test_person_films_by_id(create_one_film, fastapi_client, redis_client):
    """Тест на получение фильма по id персоны"""
    film = create_one_film
    persons_ids = [
        person['id']
        for role in ('actors', 'writers', 'directors')
        for person in film.__dict__[role]
        if film.__dict__.get(role)
    ]
    selected_person_id = random.choice(persons_ids)
    expected_structure = [uuid_to_str(PersonFilmApiSchema.build_from_model(film)).__dict__]
    cache_size = await redis_client.dbsize()

    response = await fastapi_client.get(f"/api_service/v1/persons/{selected_person_id}/film")

    assert response.status_code == HTTPStatus.OK
    assert expected_structure == response.json()
    assert await redis_client.dbsize() == cache_size + 1


@pytest.mark.parametrize("test_id, expected", BAD_ID_CASES)
async def test_persons_by_id_bad_cases(fastapi_client, test_id, expected):
    """Тест на несуществующий и некорректный id"""
    response = await fastapi_client.get(f"/api_service/v1/persons/{test_id}")
    assert response.status_code == expected
