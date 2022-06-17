import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Query

from models import Film
from .schemas import FilmApiShortSchema, FilmApiSchema

router = APIRouter()


@router.get('', response_model=list[FilmApiShortSchema])
# @cache()
async def all_films(sort: str | None = None,
                    genre_id: uuid.UUID | None = Query(default=None,
                                                       alias="filter[genre]")) -> list[FilmApiShortSchema]:
    """Получение всех фильмов"""
    films = await Film.manager.filter(sort=sort, genre=genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmApiShortSchema(**film.dict()) for film in films]


@router.get('/search', response_model=list[FilmApiShortSchema])
# @cache()
async def search_in_films(query: str | None = None) -> list[FilmApiShortSchema]:
    """Поиск по фильмам"""
    films = await Film.manager.filter(query=query)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmApiShortSchema(**film.dict()) for film in films]


@router.get('/{film_id}', response_model=FilmApiSchema)
# @cache()
async def detailed_film_info(film_id: uuid.UUID) -> FilmApiSchema:
    """Получение конкретного фильма по id"""
    film = await Film.manager.get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmApiSchema(**film.dict())
