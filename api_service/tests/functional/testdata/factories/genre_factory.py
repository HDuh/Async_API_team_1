import factory

from src.models import models
from tests.functional.settings import GENRES
from .base_factory import ElasticBaseFactory

__all__ = (
    'GenreFactory',
)


class GenreFactory(ElasticBaseFactory):
    """Фабрика жанров. Используется базовая модель жанров.
    Уникальность сгенерированных значений контролирует metaclass MetaModel
    """
    id = factory.Faker('uuid4')
    name = factory.Sequence(lambda n: GENRES[n % len(GENRES)])

    class Meta:
        model = models.Genre
