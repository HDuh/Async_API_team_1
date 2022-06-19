import uuid
from http import HTTPStatus

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi_cache.decorator import cache

from core import CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from models import Genre
from .schemas import GenreApiSchema

router = APIRouter()


@router.get('',
            response_model=list[Genre],
            summary='Get list of films')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def all_genres(elastic: AsyncElasticsearch = Depends(get_elastic),
                     page: int | None = Query(default=1, alias='page[number]', gt=0),
                     size: int | None = Query(default=50, alias='page[size]', gt=0)) -> list[Genre]:
    """
    ## Get list of genres with the information below:
    - _id_
    - _name_


    Supporting query params:
    - **page[number]** - page number,
    - **page[size]** - number of items per page
    """
    genres = await Genre.manager.filter(elastic, page=page, size=size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [Genre(**genre.dict()) for genre in genres]


@router.get('/{genre_id}',
            response_model=GenreApiSchema,
            summary='Info about Genre by ID')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def detailed_genre_info(genre_id: uuid.UUID,
                              elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreApiSchema:
    """
    ## Get information about Genre by ID with the information below:
    - _id_
    - _name_

    URL params:
    - **{genre_id}**
    """

    genre = await Genre.manager.get(elastic, genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreApiSchema(**genre.dict())
