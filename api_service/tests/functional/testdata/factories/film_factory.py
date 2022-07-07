import factory
from factory import fuzzy

from functional.utils import unpack_factory
from src.models import models
from .base_factory import ElasticBaseFactory
from .genre_factory import GenreFactory

__all__ = (
    'FilmFactory',
)


class FilmFactory(ElasticBaseFactory):
    """Фабрика жанров. Используется базовая модель жанров.
    Уникальность сгенерированных значений контролирует metaclass MetaModel
    """
    id = factory.Faker('uuid4')
    title = factory.Faker('company')
    imdb_rating = fuzzy.FuzzyFloat(low=0, high=10.0, precision=1)
    description = factory.Faker('paragraph')
    genre = unpack_factory(factory.SubFactory(GenreFactory), fuzzy.FuzzyInteger(low=1, high=3))
    actors = []
    writers = []
    directors = []

    class Meta:
        model = models.Film
