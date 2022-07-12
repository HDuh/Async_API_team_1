import factory
from factory import fuzzy

from src.models import models
from tests.functional.utils import RoleTypes
from .base_factory import ElasticBaseFactory

__all__ = (
    'PersonFactory',
)


class PersonFactory(ElasticBaseFactory):
    id = factory.Faker('uuid4')
    full_name = factory.Faker('name')
    role = factory.List([fuzzy.FuzzyChoice((role.value for role in RoleTypes))])
    film_ids = factory.ListFactory()

    class Meta:
        model = models.Person
