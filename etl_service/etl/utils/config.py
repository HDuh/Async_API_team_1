import logging
from typing import Callable

from utils import logger_config
from dotenv import load_dotenv
import backoff
from pydantic import BaseSettings, Field

__all__ = (
    "POSTGRES_DSL",
    "ELASTIC_DSL",
    "APP_CONFIG",
    "REDIS_CONFIG",
    "BACKOFF_CONFIG",
)

load_dotenv()
logger = logger_config.get_logger(__name__)


class PostgresSettings(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_NAME")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    port: int = Field(..., env="POSTGRES_PORT")


class ElasticSettings(BaseSettings):
    host: str = Field(..., env="ELASTICSEARCH_HOST")
    port: int = Field(..., env="ELASTICSEARCH_PORT")

    def ger_settings(self):
        return [f"{self.host}:{self.port}"]


class RedisSettings(BaseSettings):
    host: str = Field(..., env="REDIS_HOST")
    port: int = Field(..., env="REDIS_PORT")


class AppSettings(BaseSettings):
    batch_size: str = Field(..., env="BATCH_SIZE")
    sleep_time: int = Field(..., env="SLEEP_TIME")
    backoff_max_retries: int = Field(..., env="BACKOFF_MAX_RETRIES")
    elastic_indexes: list = Field(..., env="ELASTICSEARCH_INDEXES")


class BackoffSettings(BaseSettings):
    wait_gen: Callable = Field(backoff.expo)
    exception: type = Field(Exception)
    logger: logging.Logger = Field(logger)
    max_tries: int = Field(..., env='BACKOFF_MAX_RETRIES')


# все конфиги в константах
POSTGRES_DSL = PostgresSettings().dict()
ELASTIC_DSL = ElasticSettings().ger_settings()
APP_CONFIG = AppSettings()
REDIS_CONFIG = RedisSettings()
BACKOFF_CONFIG = BackoffSettings().dict()
