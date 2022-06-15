from enum import Enum, unique

from .models import Genre, Person, Film

__all__ = (
    'ModelsController',
)


@unique
class ModelsController(Enum):
    movies: Film = Film
    genres: Genre = Genre
    persons: Person = Person
