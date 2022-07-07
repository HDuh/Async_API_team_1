import uuid
from typing import Any

from pydantic import BaseModel

from .schemas_mixins import BuildFromModelMixin

__all__ = (
    'FilmApiSchema',
    'FilmApiShortSchema',
)


class FilmApiSchema(BaseModel, BuildFromModelMixin):
    id: uuid.UUID
    title: str
    imdb_rating: float
    description: str = None
    genre: list[Any]
    actors: list[Any]
    writers: list[Any]
    directors: list[Any]


class FilmApiShortSchema(BaseModel, BuildFromModelMixin):
    id: uuid.UUID
    title: str
    imdb_rating: float
