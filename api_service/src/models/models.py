import uuid

from typing import Optional, Union

import orjson

from pydantic import BaseModel

__all__ = (
    'Film',
    'Genre',
    'Person',
)


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    role: Union[list[str], None]
    film_ids: Union[list[uuid.UUID], None]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: Optional[float] = 0.0
    description: Optional[str]
    genre: Optional[list[Genre]]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    directors: Optional[list[Person]]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
