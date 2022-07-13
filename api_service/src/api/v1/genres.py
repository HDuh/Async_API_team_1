import uuid
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Depends

from fastapi_cache.decorator import cache

from src.core import CACHE_EXPIRE_IN_SECONDS
from src.models import Genre
from .schemas import GenreApiSchema, Pagination

router = APIRouter()


@router.get('/', response_model=Any, summary='Get list of films')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def all_genres(pagination: Pagination = Depends()) -> list[GenreApiSchema]:
    """
    ## Get list of genres with the information below:
    - _id_
    - _name_


    Supporting query params:
    - **page_number** - page number,
    - **page_size** - number of items per page
    """
    genres = await Genre.manager.filter(**pagination.dict())

    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [GenreApiSchema.build_from_model(genre) for genre in genres]


@router.get('/{genre_id}', response_model=Any, summary='Info about Genre by ID')
@cache(expire=CACHE_EXPIRE_IN_SECONDS)
async def detailed_genre_info(genre_id: uuid.UUID) -> GenreApiSchema:
    """
    ## Get information about Genre by ID with the information below:
    - _id_
    - _name_

    URL params:
    - **{genre_id}**
    """

    genre = await Genre.manager.get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreApiSchema.build_from_model(genre)
