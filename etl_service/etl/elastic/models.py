from enum import Enum
from typing import Union
from uuid import UUID

from pydantic import BaseModel, validator


class GenresES(BaseModel):
    id: UUID
    name: str


class PersonsES(BaseModel):
    id: UUID
    full_name: str
    role: list[str]
    film_ids: list[UUID]

    @validator('film_ids', )
    def null_list(cls, value):
        return value if value else []


class Person(BaseModel):
    id: UUID
    full_name: str


class MoviesES(BaseModel):
    id: UUID
    imdb_rating: float = None
    genre: list[GenresES] = None
    title: str
    description: str = None
    actors: list[Person] = None
    writers: list[Person] = None
    directors: list[Person] = None

    @validator('directors', 'actors', 'writers', 'genre')
    def null_list(cls, value: Union[None, list]) -> list:
        """
        Валидатор проверяет переданные атрибуты на None.
        Если None, то заменяется на пустой список.
        """
        return value if value else []


class FilmTypes(str, Enum):
    movie = 'movie'
    tv_show = 'tv_show'


class PersonsType(str, Enum):
    actor = 'actor'
    director = 'director'
    writer = 'writer'
