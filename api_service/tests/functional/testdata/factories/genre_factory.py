import factory
from factory import fuzzy

from functional.settings import GENRES
from src.models import models
from .base_factory import ElasticBaseFactory

__all__ = (
    'GenreFactory',
)


class GenreFactory(ElasticBaseFactory):
    """Фабрика жанров. Используется базовая модель жанров.
    Уникальность сгенерированных значений контролирует metaclass MetaModel
    """
    id = factory.Faker('uuid4')
    name = fuzzy.FuzzyChoice(GENRES)

    class Meta:
        model = models.Genre
