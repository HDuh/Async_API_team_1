import uuid

from pydantic import BaseModel

from models import Genre, Person

__all__ = (
    'FilmApiSchema',
    'FilmApiShortSchema',
)


class FilmApiSchema(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float
    description: str = None
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]


class FilmApiShortSchema(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float
