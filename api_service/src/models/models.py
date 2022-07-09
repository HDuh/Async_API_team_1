import uuid
from functools import reduce

from elasticsearch_dsl import Q

from core import ELASTIC_INDEX_SUFFIX
from etl_service.etl.elastic.indexes import genres_schema, persons_schema, movies_schema
from .model_meta import MetaModel
from .models_mixins import ManagerMixIn, BaseModelMixin

__all__ = (
    'Film',
    'Genre',
    'Person',
)


class Genre(ManagerMixIn, BaseModelMixin, metaclass=MetaModel):
    def __init__(self, id: uuid.UUID, name: str):
        self.id = id
        self.name = name

    class ModelConfig:
        es_index = f'genres{ELASTIC_INDEX_SUFFIX}'
        schema = genres_schema


class Person(ManagerMixIn, BaseModelMixin, metaclass=MetaModel):
    def __init__(self, id: uuid.UUID, full_name: str, role: list[str] = None, film_ids: list[uuid.UUID] = None):
        self.id = id
        self.full_name = full_name
        self.role = role if role else []
        self.film_ids = film_ids if film_ids else []

    def get_short(self) -> dict:
        return {
            'id': self.id,
            'full_name': self.full_name,
        }

    class ModelConfig:
        es_index = f'persons{ELASTIC_INDEX_SUFFIX}'
        schema = persons_schema
        filter_map = {
            'query': lambda query_text: Q('multi_match', query=query_text,
                                          fields=['full_name^3', 'role']),
        }


class Film(ManagerMixIn, BaseModelMixin, metaclass=MetaModel):
    def __init__(
            self, id: uuid.UUID, title: str | None, description: str | None, imdb_rating: float | None = 0,
            genre: list[Genre] = None, actors: list[Person] = None, writers: list[Person] = None,
            directors: list[Person] = None):
        self.id = id
        self.title = title
        self.imdb_rating = imdb_rating
        self.description = description
        self.genre = genre if genre else []
        self.actors = actors if actors else []
        self.writers = writers if writers else []
        self.directors = directors if directors else []

    class ModelConfig:
        es_index = f'movies{ELASTIC_INDEX_SUFFIX}'
        schema = movies_schema
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
