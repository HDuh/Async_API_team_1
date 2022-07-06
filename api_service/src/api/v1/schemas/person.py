import uuid

from pydantic import BaseModel

from .schemas_mixins import BuildFromModelMixin

__all__ = (
    'PersonApiSchema',
    'PersonFilmApiSchema',
)


class PersonApiSchema(BaseModel, BuildFromModelMixin):
    id: uuid.UUID
    full_name: str
    role: list[str]
    film_ids: list[uuid.UUID]


class PersonFilmApiSchema(BaseModel, BuildFromModelMixin):
    id: uuid.UUID
    title: str
    imdb_rating: float
