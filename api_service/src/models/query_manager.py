from typing import Any

from elasticsearch_dsl import Q
from pydantic import BaseModel


class QueriesManager:
    @classmethod
    def create_query(cls, model: Any, **kwargs):
        """Формирование запроса в Elasticsearch"""
        query = None
        for parameter, value in kwargs.items():
            if value:
                query = model.ModelConfig.filter_map[parameter](value).to_dict()
        if not query:
            query = Q().to_dict()
        return {'query': query}

    @classmethod
    def transform_sorting(cls, sorting_parameter: str):
        """Трансформация параметра сортировки в формат Elasticsearch"""
        if not sorting_parameter:
            return
        order = 'desc' if sorting_parameter.startswith('-') else 'asc'
        sort_field = sorting_parameter.removeprefix('-')
        return f'{sort_field}:{order}'
