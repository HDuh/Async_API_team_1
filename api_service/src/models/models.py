import uuid

import orjson
from pydantic import BaseModel, Field
from .model_manager import ModelManager

__all__ = (
    'Film',
    'Genre',
    'Person',
)


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class ManagerMixIn:
    @classmethod
    def manager(cls):
        return cls.Config.manager(cls)


class Genre(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(...,)
    name: str = Field(...,)

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        es_index = 'genres'
        manager = ModelManager


class Person(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(...,)
    full_name: str = Field(...,)
    role: list[str] = Field(default=[])
    film_ids: list[uuid.UUID] = Field(default=[])

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        es_index = 'persons'
        manager = ModelManager


class Film(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(...,)
    title: str = Field(...,)
    imdb_rating: float = Field(default=0.0)
    description: str = Field(default=None)
    genre: list[Genre] = Field(default=[])
    actors: list[Person] = Field(default=[])
    writers: list[Person] = Field(default=[])
    directors: list[Person] = Field(default=[])

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        es_index = 'movies'
        manager = ModelManager
