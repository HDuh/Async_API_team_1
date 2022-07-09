import factory
from factory import fuzzy

from src.models import models
from .base_factory import ElasticBaseFactory

__all__ = (
    'PersonFactory',
)


class PersonFactory(ElasticBaseFactory):
    id = factory.Faker('uuid4')
    full_name = factory.Faker('name')
    role = fuzzy.FuzzyChoice(('actor', 'writer', 'director'))
    film_ids = factory.Faker('uuid4')

    class Meta:
        model = models.Person
