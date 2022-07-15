import asyncio
import logging
from contextlib import asynccontextmanager

import aioredis
import backoff

from core.config import REDIS_CONFIG, BACKOFF_CONFIG


@asynccontextmanager
async def redis_client():
    client = await aioredis.from_url(REDIS_CONFIG, encoding='utf-8', decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


@backoff.on_exception(**BACKOFF_CONFIG)
async def wait_for_redis():
    async with redis_client() as re_client:
        if await re_client.ping():
            await re_client.flushall()
            logging.info('REDIS connected')
        else:
            raise ConnectionError('REDIS NOT PING')


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
