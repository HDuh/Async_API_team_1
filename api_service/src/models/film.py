from typing import Optional

import orjson

from pydantic import BaseModel

__all__ = (
    'Film',
)

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class IdMixin(BaseModel):
    id: str


class Person(IdMixin):
    full_name: str


class Genre(IdMixin):
    name: str


class Film(IdMixin):
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
