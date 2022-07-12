import os
import warnings
from logging import config as logging_config
from typing import Callable

import backoff
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
    'ELASTIC_INDEX_SUFFIX',
    'BACKOFF_CONFIG',
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

    def get_settings(self):
        return [f'{self.host}:{self.port}']


# Настройки Redis
class RedisSettings(BaseSettings):
    host: str = Field(..., env='REDIS_HOST')
    port: int = Field(..., env='REDIS_PORT')

    def get_settings(self):
        return f'redis://{self.host}:{self.port}'


class BackoffSettings(BaseSettings):
    wait_gen: Callable = Field(backoff.expo)
    exception: type = Field(Exception)
    max_tries: int = Field(..., env='BACKOFF_MAX_RETRIES')


ELASTIC_CONFIG = ElasticSettings().get_settings()
REDIS_CONFIG = RedisSettings().get_settings()
BACKOFF_CONFIG = BackoffSettings().dict()

# Суффикс для индекса. Дополняет имя основного индекса для создания тестового
ELASTIC_INDEX_SUFFIX = ''
if PYTEST_RUN := os.getenv('PYTEST_RUN_CONFIG', False):
    ELASTIC_INDEX_SUFFIX = '_test'
