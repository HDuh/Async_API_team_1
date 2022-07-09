import factory
from factory import fuzzy

from src.models import models
from .base_factory import ElasticBaseFactory

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
    genre = factory.ListFactory()
    actors = factory.ListFactory()
    writers = factory.ListFactory()
    directors = factory.ListFactory()

    class Meta:
        model = models.Film
