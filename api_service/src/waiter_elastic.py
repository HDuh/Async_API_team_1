import asyncio
import logging
from contextlib import asynccontextmanager

import backoff
from elasticsearch import AsyncElasticsearch

from core.config import ELASTIC_CONFIG, BACKOFF_CONFIG


@asynccontextmanager
async def elastic_client():
    client = AsyncElasticsearch(ELASTIC_CONFIG)
    try:
        yield client
    finally:
        await client.close()


@backoff.on_exception(**BACKOFF_CONFIG)
async def elastic_wait():
    async with elastic_client() as es_client:
        if await es_client.ping():
            logging.info('ELASTICSEARCH connected')
        else:
            raise ConnectionError('ELASTICSEARCH NO PING')


if __name__ == '__main__':
    asyncio.run(elastic_wait())
