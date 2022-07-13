import logging
from contextlib import contextmanager

import backoff
from elasticsearch import Elasticsearch

from core.config import ELASTIC_CONFIG, BACKOFF_CONFIG


@contextmanager
def elastic_client():
    client = Elasticsearch(ELASTIC_CONFIG)
    yield client
    client.close()


@backoff.on_exception(**BACKOFF_CONFIG)
def elastic_wait():
    with elastic_client() as es_client:
        if es_client.ping():
            logging.info('ELASTICSEARCH connected')
            return
        raise ConnectionError('ELASTICSEARCH NO PING')


if __name__ == '__main__':
    elastic_wait()
