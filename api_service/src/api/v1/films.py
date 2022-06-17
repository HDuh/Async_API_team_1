import uuid
from http import HTTPStatus
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models import Film
from services import FilmsService, get_films_service
from .genres import Genre
from .persons import Person

router = APIRouter()


class FilmApiSchema(BaseModel):
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


@router.get('/{film_id}', response_model=FilmApiSchema)
# @cache()
async def film_details(film_id: uuid.UUID, ) -> FilmApiSchema:
    film = await Film.manager().get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmApiSchema(id=film.id, title=film.title,
                         imdb_rating=film.imdb_rating,
                         description=film.description,
                         genre=film.genre, actors=film.actors,
                         writers=film.writers, directors=film.directors)


@router.get('', response_model=list[FilmForSearch])
# @cache()
async def sorted_films(sort: Union[str, None] = None,
                       genre_id: Union[uuid.UUID, None] = Query(default=None,
                                                                alias="filter[genre]")) -> list[FilmForSearch]:
    films = await Film.manager().filter(sort=sort, genre_id=genre_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    result = [
        FilmForSearch(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
    return result
