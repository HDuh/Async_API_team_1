import time
import warnings

import backoff
from elasticsearch import ElasticsearchDeprecationWarning

from elastic import ElasticController
from postgres import PostgresController
from redis_storage import RedisState
from utils import APP_CONFIG, BACKOFF_CONFIG, logger_etl


@backoff.on_exception(**BACKOFF_CONFIG)
def get_from_postgres(index: str, timestamp: str) -> tuple:
    return tuple(postgres_db(index, timestamp))


@backoff.on_exception(**BACKOFF_CONFIG)
def send_to_elastic(index: str, data, timestamp) -> None:
    elasticsearch_db(index, data, timestamp)


@backoff.on_exception(**BACKOFF_CONFIG)
def get_last_update(index: str):
    return state(f"{index}_state")


def start_monitoring() -> None:
    """
    Функция запускает процесс проверки обновлений в Postgres
    для каждого индекса и загружает обновленные строки в ES
    """
    while True:
        logger_etl.info("Sync in progress >>>  ")
        for index_i in indexes:
            current_state_for_index = get_last_update(index_i)
            if data := get_from_postgres(index_i, current_state_for_index):
                send_to_elastic(index_i, data, state)
            else:
                logger_etl.info(f'No update for index: {index_i}')
        logger_etl.info(f'Sleep for {sleep_time} sec.')
        time.sleep(sleep_time)


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=ElasticsearchDeprecationWarning)
    sleep_time = APP_CONFIG.sleep_time
    indexes = APP_CONFIG.elastic_indexes
    postgres_db = PostgresController()
    elasticsearch_db = ElasticController()
    state = RedisState()
    start_monitoring()
