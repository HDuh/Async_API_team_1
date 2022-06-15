import uuid
from http import HTTPStatus
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, paginate, add_pagination
from pydantic import BaseModel, validator

from services import FilmService, get_film_service, FilmsService, get_films_service

router = APIRouter()


class IdMixin(BaseModel):
    id: uuid.UUID


class Person(IdMixin):
    full_name: str


class Genre(IdMixin):
    name: str


class FilmInfo(IdMixin):
    title: str
    imdb_rating: Union[float, None] = 0.01
    description: Optional[str]
    genre: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]


class FilmForSearch(IdMixin):
    title: str
    imdb_rating: Union[float, None] = 0.01

    class Config:
        orm_model = True


@router.get('/{film_id}', response_model=FilmInfo)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmInfo:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmInfo(id=film.id, title=film.title,
                    imdb_rating=film.imdb_rating,
                    description=film.description,
                    genre=film.genre, actors=film.actors,
                    writers=film.writers, directors=film.directors)


@router.get('', response_model=Page[FilmForSearch])
async def sorted_films(films_service: FilmsService = Depends(get_films_service),
                       sort: Union[str, None] = None,
                       genre_id: Union[str, None] = Query(default=None,
                                                          alias="filter[genre]")):
    films = await films_service.get_all_data(sort)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    result = [FilmForSearch(id=film.id,
                            title=film.title,
                            imdb_rating=film.imdb_rating) for film in films]
    if genre_id:
        return genre_id

    return paginate(result)


add_pagination(router)
