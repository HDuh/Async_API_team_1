from http import HTTPStatus
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_cache.decorator import cache

from core import CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from models import Film
from .schemas import FilmApiShortSchema, FilmApiSchema, Pagination

router = APIRouter()


@router.get('', response_model=list[FilmApiShortSchema], summary='Get list of films')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def all_films(elastic: AsyncElasticsearch = Depends(get_elastic),
                    sort: str | None = None,
                    pagination: Pagination = Depends(),
                    genre_id: UUID | None = Query(default=None,
                                                  alias='filter[genre]')) -> list[FilmApiShortSchema]:
    """
    ## Get list of films with the information below:
    - _id_
    - _title_
    - _imdb_rating_

    Supporting query params:
    - **page_number** - page number,
    - **page_size** - number of items per page
    - **filter** by genre ID (show film only for a specified genre)
    - sorting:
        - abc: **"imdb_rating"**,
        - desc: **"-imdb_rating"**
    """
    films = await Film.manager.filter(elastic, sort=sort, **pagination.dict(), genre=genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmApiShortSchema(**film.dict()) for film in films]


@router.get('/search', response_model=list[FilmApiShortSchema], summary='Search in films')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def search_in_films(elastic: AsyncElasticsearch = Depends(get_elastic),
                          query: str | None = None,
                          pagination: Pagination = Depends()) -> list[FilmApiShortSchema]:
    """
    ## Get list of films with the information below:
    - _id_
    - _title_
    - _imdb_rating_

    Supporting query params:
    - **page_number** - page number,
    - **page_size** - number of items per page
    - **query** - search request
    """
    films = await Film.manager.filter(elastic, query=query, **pagination.dict())
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmApiShortSchema(**film.dict()) for film in films]


@router.get('/{film_id}', response_model=FilmApiSchema, summary='Detailed info about Film by ID')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def detailed_film_info(film_id: UUID, elastic: AsyncElasticsearch = Depends(get_elastic)) -> FilmApiSchema:
    """
    ## Get detailed information about Film:
    - _id_
    - _title_
    - _imdb_rating_
    - _description_
    - _genre_
    - _actors_
    - _writers_
    - _directors_

    URL params:
    - **{film_id}**
    """
    film = await Film.manager.get(elastic, film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmApiSchema(**film.dict())
