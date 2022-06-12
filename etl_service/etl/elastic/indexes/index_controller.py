from .index_genres import genres_schema
from .index_movies import movies_schema
from .index_persons import persons_schema

MAPPING = {
    'movies': movies_schema,
    'genres': genres_schema,
    'persons': persons_schema
}


def get_schema(index_name: str) -> str:
    return MAPPING[index_name]
