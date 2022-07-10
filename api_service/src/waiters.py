import logging
import os

import backoff
from elasticsearch import Elasticsearch
from redis import Redis

from core.config import ELASTIC_CONFIG
from core.config import BACKOFF_CONFIG
from dotenv import load_dotenv

load_dotenv()


@backoff.on_exception(**BACKOFF_CONFIG)
def wait_for_es():
    es = Elasticsearch(ELASTIC_CONFIG)
    if es.ping():
        logging.info('Elasticsearch connect')
    else:
        raise ConnectionError('Elasticsearch')


@backoff.on_exception(**BACKOFF_CONFIG)
def wait_for_redis():
    redis = Redis(host=os.getenv('REDIS_HOST'),
                  port=os.getenv('REDIS_PORT'))
    if redis.ping():
        redis.flushall()  # очистка кэша
        logging.info('Redis connected')
    else:
        raise ConnectionError('Redis')


if __name__ == '__main__':
    wait_for_es()
    wait_for_redis()
