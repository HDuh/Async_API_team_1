import time
import warnings
from datetime import datetime

import backoff

from utils import logger_config
from utils.config import REDIS_CONFIG, APP_CONFIG, BACKOFF_CONFIG
from elastic import ElasticController
from elasticsearch import ElasticsearchDeprecationWarning
from postgres import PostgresController
from state.redis_state import RedisState

# Ужаление бесячего ворнинга об устаревших методах
warnings.filterwarnings("ignore", category=ElasticsearchDeprecationWarning)

# Подлючение своего логгера
logger = logger_config.get_logger(__name__)

# Определение хранилища состояний для индексов
state = RedisState(config=REDIS_CONFIG)

sleep_time = APP_CONFIG.sleep_time
indexes = APP_CONFIG.elastic_indexes


@backoff.on_exception(**BACKOFF_CONFIG)
def start_monitoring() -> None:
    """
    Функция запускает процесс проверки обновлений в Postgres
    для каждого индекса и загружает обновленные строки в ES
    """

    while True:
        logger.info("Sync in progress >>>  ")
        for index_i in indexes:
            current_state_for_index = state.get_state(f"{index_i}_state",
                                                      default=datetime.min)
            pg_db = PostgresController()
            es_db = ElasticController(index_i, state)

            # extract from PG
            data = pg_db(index_i, current_state_for_index)

            # transform and load to Elastic
            es_db(data)

        logger.info(f'Sleep for {sleep_time} sec.')
        time.sleep(sleep_time)


if __name__ == '__main__':
    start_monitoring()
