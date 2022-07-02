import asyncio

import factory
from factory import fuzzy, DictFactory, Factory
from functional.settings import GENRES
from src.models import models

__all__ = (
    'GenreFactory',
)


class ElasticBaseFactory(Factory):
    class Meta:
        abstract = True

    # @classmethod
    # def _create(cls, model_class, *args, **kwargs):
    #     instance = cls._build(model_class, *args, **kwargs)
    #     if not instance.Config.es_index.endswith('test'):
    #         instance.Config.es_index = f'{instance.Config.es_index}_test'
    #     loop = asyncio.new_event_loop()
    #     loop.run_until_complete(instance.manager.save(instance))

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        if args:
            raise ValueError('NEED VALUES!')
        instance = model_class(**kwargs)
        if not instance.Config.es_index.endswith('test'):
            instance.Config.es_index = f'{instance.Config.es_index}_test'
        return instance


class GenreFactory(ElasticBaseFactory):
    id = factory.Faker('uuid4')
    name = fuzzy.FuzzyChoice(GENRES)

    # TODO: можно модель заставить генерить уникальные значения из списка
    class Meta:
        model = models.Genre
