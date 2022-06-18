from elasticsearch_dsl import Q
from pydantic import BaseModel


class QueriesManager:
    @classmethod
    def create_query(cls, model: BaseModel, **kwargs):
        """Формирование запроса в Elasticsearch"""
        query = None
        for parameter, value in kwargs.items():
            if value:
                query = model.Config.filter_map[parameter](value).to_dict()
        if not query:
            query = Q().to_dict()
        return {'query': query}

    @classmethod
    def transform_sorting(cls, sorting_parameter: str):
        """Трансформация параметра сортировки в формат Elasticsearch"""
        if not sorting_parameter:
            return
        return f'{sorting_parameter[1:]}:desc' if sorting_parameter.startswith('-') else f'{sorting_parameter}:asc'
