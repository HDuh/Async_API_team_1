import uuid
from http import HTTPStatus

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_cache.decorator import cache

from core import CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from models import Person, Film
from .schemas import PersonApiSchema, PersonFilmApiSchema

router = APIRouter()


@router.get('', response_model=list[PersonApiSchema])
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def all_persons(elastic: AsyncElasticsearch = Depends(get_elastic),
                      page: int | None = Query(default=1, alias='page[number]', gt=0),
                      size: int | None = Query(default=50, alias='page[size]', gt=0)) -> list[PersonApiSchema]:
    """Получение всех персон"""
    persons = await Person.manager.filter(elastic, page=page, size=size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [PersonApiSchema(**person.dict()) for person in persons]


@router.get('/search', response_model=list[PersonApiSchema])
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def search_in_persons(elastic: AsyncElasticsearch = Depends(get_elastic),
                            query: str | None = None,
                            page: int | None = Query(default=1, alias='page[number]', gt=0),
                            size: int | None = Query(default=50, alias='page[size]', gt=0)) -> list[PersonApiSchema]:
    """Поиск по персонам"""
    persons = await Person.manager.filter(elastic, query=query, page=page, size=size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [PersonApiSchema(**person.dict()) for person in persons]


@router.get('/{person_id}', response_model=PersonApiSchema)
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def detailed_person_info(person_id: uuid.UUID,
                               elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonApiSchema:
    """Получение конкретной персоны по id"""
    person = await Person.manager.get(elastic, person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonApiSchema(**person.dict())


@router.get('/{person_id}/film', response_model=list[PersonFilmApiSchema])
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def person_films(person_id: uuid.UUID,
                       elastic: AsyncElasticsearch = Depends(get_elastic)) -> list[PersonFilmApiSchema]:
    """Получение фильмов с участием конкретной персоны по id"""
    all_films = await Film.manager.filter(elastic, person=person_id)
    if not all_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [PersonFilmApiSchema(**film.dict()) for film in all_films]
