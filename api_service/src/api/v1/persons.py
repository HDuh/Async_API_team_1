import uuid
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from src.core import CACHE_EXPIRE_IN_SECONDS
from src.models import Person, Film
from .schemas import PersonApiSchema, PersonFilmApiSchema, Pagination

router = APIRouter()


@router.get('/', response_model=Any, summary='Get list of persons')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def all_persons(pagination: Pagination = Depends()) -> list[PersonApiSchema]:
    """
    ## Get list of genres with the information below:
    - _id_
    - _full_name_
    - _role_
    - _films_IDs_


    Supporting query params:
    - **page_number_** - page number,
    - **page_size_** - number of items per page
    """
    persons = await Person.manager.filter(**pagination.dict())
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [PersonApiSchema.build_from_model(person) for person in persons]


@router.get('/search', response_model=Any, summary='Search in persons')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def search_in_persons(query: str | None = None,
                            pagination: Pagination = Depends()) -> list[PersonApiSchema]:
    """
    ## Get list of persons with the information below:
    - _id_
    - _full_name_
    - _role_
    - _films_IDs_


    Supporting query params:
    - **page_number** - page number,
    - **page_size** - number of items per page
    - **query** - search request
    """
    persons = await Person.manager.filter(query=query, **pagination.dict())
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [PersonApiSchema.build_from_model(person) for person in persons]


@router.get('/{person_id}', response_model=Any, summary='Info about Person by ID')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def detailed_person_info(person_id: uuid.UUID) -> PersonApiSchema:
    """
    ## Get information about person by ID the information below:
    - _id_
    - _full_name_
    - _role_
    - _films_IDs_

    URL params:
    - **{person_id}**
    """
    person = await Person.manager.get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonApiSchema.build_from_model(person)


@router.get('/{person_id}/film', response_model=Any, summary='List of films for a specified person by id')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def person_films(person_id: uuid.UUID) -> list[PersonFilmApiSchema]:
    """
    ## Get list of films by Person ID with the information below:
    - _id_
    - _title_
    - _imdb_rating_


    URL params:
    - **{person_id}**
    """
    all_films = await Film.manager.filter(person=person_id)
    if not all_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [PersonFilmApiSchema.build_from_model(film) for film in all_films]
