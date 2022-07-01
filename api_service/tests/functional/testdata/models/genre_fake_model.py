import factory
from factory import fuzzy, DictFactory
from functional.settings import GENRES

__all__ = (
    'GenreFactory',
)


class GenreFactory(DictFactory):
    id = factory.Faker('uuid4')
    name = fuzzy.FuzzyChoice(GENRES)

# if __name__ == '__main__':
#     print(1)
