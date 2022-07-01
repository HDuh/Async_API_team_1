import warnings

from dotenv import load_dotenv
from elasticsearch import ElasticsearchDeprecationWarning
from pydantic import BaseSettings, Field

__all__ = (
    'SERVICE_URL',
    'ELASTIC_CONFIG',
    'GENRES',
)

load_dotenv()
warnings.filterwarnings('ignore', category=ElasticsearchDeprecationWarning)

SERVICE_URL = 'http://127.0.0.1:8000'


# Настройки Elasticsearch
class ElasticSettings(BaseSettings):
    host: str = Field(..., env='ELASTICSEARCH_HOST')
    port: int = Field(..., env='ELASTICSEARCH_PORT')

    def get_settings(self):
        return [f'{self.host}:{self.port}']


ELASTIC_CONFIG = ElasticSettings().get_settings()

GENRES = (
    'Action',
    'Adventure',
    'Fantasy',
    'Sci-Fi',
    'Drama',
    'Music',
    'Romance',
    'Thriller',
    'Mystery',
    'Comedy',
    'Animation',
    'Family',
    'Biography',
    'Musical',
    'Crime',
    'Short',
    'Western',
    'Documentary',
    'History',
    'War',
    'Game-Show',
    'Reality-TV',
    'Horror',
    'Sport',
    'Talk-Show',
    'News',
)
