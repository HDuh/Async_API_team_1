import os
import warnings
from logging import config as logging_config

from dotenv import load_dotenv
from elasticsearch import ElasticsearchDeprecationWarning
from pydantic import BaseSettings, Field

from .logger import LOGGING

__all__ = (
    'PROJECT_NAME',
    'BASE_DIR',
    'ELASTIC_CONFIG',
    'REDIS_CONFIG',
    'CACHE_EXPIRE_IN_SECONDS',
)

load_dotenv()
# Глушим Elasticsearch built-in security features are not enabled
warnings.filterwarnings('ignore', category=ElasticsearchDeprecationWarning)

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Время жизни в кеше
CACHE_EXPIRE_IN_SECONDS = 300


# Настройки Elasticsearch
class ElasticSettings(BaseSettings):
    host: str = Field(..., env='ELASTICSEARCH_HOST')
    port: int = Field(..., env='ELASTICSEARCH_PORT')

    def ger_settings(self):
        return [f'{self.host}:{self.port}']


# Настройки Redis
class RedisSettings(BaseSettings):
    host: str = Field(..., env='REDIS_HOST')
    port: int = Field(..., env='REDIS_PORT')

    def get_settings(self):
        return f'redis://{self.host}:{self.port}'


ELASTIC_CONFIG = ElasticSettings().ger_settings()
REDIS_CONFIG = RedisSettings().get_settings()
