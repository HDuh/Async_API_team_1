import uuid
from http import HTTPStatus
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate, add_pagination
from pydantic import BaseModel

from .genres import Genre
from .persons import Person

from services import FilmService, get_film_service, FilmsService, get_films_service

router = APIRouter()


class FilmInfo(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: Union[float, None] = 0.0
    description: Optional[str]
    genre: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]


class FilmForSearch(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: Union[float, None] = 0.0

    class Config:
        orm_model = True


@router.get('/{film_id}', response_model=FilmInfo)
async def film_details(film_id: uuid.UUID, film_service: FilmService = Depends(get_film_service)) -> FilmInfo:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmInfo(id=film.id, title=film.title,
                    imdb_rating=film.imdb_rating,
                    description=film.description,
                    genre=film.genre, actors=film.actors,
                    writers=film.writers, directors=film.directors)


@router.get('', response_model=list[FilmForSearch])
async def sorted_films(films_service: FilmsService = Depends(get_films_service),
                       sort: Union[str, None] = None,
                       genre_id: Union[uuid.UUID, None] = Query(default=None,
                                                                alias="filter[genre]")) -> list[FilmForSearch]:
    films = await films_service.get_all_data(sort, genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    result = [
        FilmForSearch(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return result
