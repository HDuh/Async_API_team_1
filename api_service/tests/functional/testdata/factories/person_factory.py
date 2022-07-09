import factory
from factory import fuzzy
from functional.utils import RoleTypes
from src.models import models
from .base_factory import ElasticBaseFactory

__all__ = (
    'PersonFactory',
)


class PersonFactory(ElasticBaseFactory):
    id = factory.Faker('uuid4')
    full_name = factory.Faker('name')
    role = fuzzy.FuzzyChoice((role.value for role in RoleTypes))
    film_ids = factory.Faker('uuid4')

    class Meta:
        model = models.Person
