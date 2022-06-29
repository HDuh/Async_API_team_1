import warnings

from dotenv import load_dotenv
from elasticsearch import ElasticsearchDeprecationWarning
from pydantic import BaseSettings, Field

__all__ = (
    'SERVICE_URL',
    'ELASTIC_CONFIG',
)

load_dotenv()
warnings.filterwarnings('ignore', category=ElasticsearchDeprecationWarning)

SERVICE_URL = 'http://127.0.0.1:8000'


# Настройки Elasticsearch
class ElasticSettings(BaseSettings):
    host: str = Field(..., env='ELASTICSEARCH_HOST')
    port: int = Field(..., env='ELASTICSEARCH_PORT')

    def ger_settings(self):
        return [f'{self.host}:{self.port}']


ELASTIC_CONFIG = ElasticSettings().ger_settings()
