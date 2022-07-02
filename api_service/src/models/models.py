import uuid
from functools import reduce

import orjson
from elasticsearch_dsl import Q
from pydantic import BaseModel, Field, validator

from .model_manager import ModelManager
from etl_service.etl.elastic.indexes.index_genres import genres_schema

__all__ = (
    'Film',
    'Genre',
    'Person',
)


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class ManagerMixIn:
    @classmethod
    @property
    def manager(cls):
        return cls.Config.manager(cls)

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        manager = ModelManager


class Genre(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(..., )
    name: str = Field(..., )

    class Config(ManagerMixIn.Config):
        es_index = 'genres'
        schema = genres_schema
    # TODO: В моделях описать все атрибуты (индекс, структуру запроса)

class Person(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(..., )
    full_name: str = Field(..., )
    role: list[str] = Field(default=[])
    film_ids: list[uuid.UUID] = Field(default=[])

    class Config(ManagerMixIn.Config):
        es_index = 'persons'
        filter_map = {
            'query': lambda query_text: Q('multi_match', query=query_text,
                                          fields=['full_name^3', 'role']),
        }


class Film(BaseModel, ManagerMixIn):
    id: uuid.UUID = Field(..., )
    title: str | None = Field(..., )
    imdb_rating: float | None = Field(..., )
    description: str | None = Field(default=None)
    genre: list[Genre] = Field(default=[])
    actors: list[Person] = Field(default=[])
    writers: list[Person] = Field(default=[])
    directors: list[Person] = Field(default=[])

    @validator('imdb_rating')
    def rating_validator(cls, rating: float | None) -> float:
        if not rating:
            return 0.0
        return rating

    class Config(ManagerMixIn.Config):
        es_index = 'movies'
        filter_map = {
            'genre': lambda genre_id: Q('nested', path='genre', query=Q('match', genre__id=genre_id)),
            'person': lambda person_id: reduce(
                lambda x, y: x | y, (
                    Q('nested', path=role, query=Q('match', **{f'{role}.id': person_id}))
                    for role in ('actors', 'writers', 'directors')
                )
            ),
            'query': lambda query_text: Q('multi_match', query=query_text,
                                          fields=['title^3', 'description', 'genre', 'actors', 'writers', 'directors'])
        }
