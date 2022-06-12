from typing import Type

from pydantic import BaseModel

from .models import MoviesES, GenresES, PersonsES


def get_index_model(index_name) -> Type[BaseModel]:
    """ Маппинг модели по индексу """
    mapping = {
        'movies': MoviesES,
        'genres': GenresES,
        'persons': PersonsES,
    }

    try:
        return mapping[index_name]
    except KeyError:
        raise ValueError(f'No model for index {index_name}')
