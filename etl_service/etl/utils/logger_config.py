import logging
from typing import ClassVar

from pydantic import BaseSettings, Field

__all__ = (
    'logger_etl',
)


class LoggerSettings(BaseSettings):
    format: str = Field('''%(asctime)s [%(levelname)s]: %(message)s  |  
    %(name)s  (%(filename)s).%(funcName)s(%(lineno)d)''')
    datefmt: str = Field('%Y-%m-%d %H:%M:%S')
    level: int = Field(logging.INFO)
    handlers: ClassVar = Field(default_factory=logging.StreamHandler)


LOGGER_SETTINGS = LoggerSettings().dict()
logging.basicConfig(**LOGGER_SETTINGS)
logger_etl = logging.getLogger('logger_etl')
