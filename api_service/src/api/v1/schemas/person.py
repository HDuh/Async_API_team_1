import uuid

from pydantic import BaseModel

__all__ = (
    'PersonApiSchema',
    'PersonFilmApiSchema',
)


class PersonApiSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    role: list[str]
    film_ids: list[uuid.UUID]


class PersonFilmApiSchema(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float
