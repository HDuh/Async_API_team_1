import logging
from contextlib import contextmanager

import backoff
from aioredis import Redis

from core.config import BACKOFF_CONFIG, REDIS_CONFIG_DICT


@contextmanager
def redis_client():
    client = Redis(**REDIS_CONFIG_DICT)
    yield client
    client.close()


@backoff.on_exception(**BACKOFF_CONFIG)
def wait_for_redis():
    with redis_client() as re_client:
        if re_client.ping():
            re_client.flushall()  # очистка кэша
            logging.info('REDIS connected')
            return
        raise ConnectionError('REDIS NOT PING')


if __name__ == '__main__':
    wait_for_redis()
