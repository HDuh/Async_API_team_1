import logging

import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1 import films, genres, persons
from core import PROJECT_NAME, LOGGING, REDIS_CONFIG
from db import redis

app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api_service/openapi',
    openapi_url='/api_service/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.from_url(REDIS_CONFIG, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis.redis), prefix=f'{PROJECT_NAME}_cache')


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()


app.include_router(films.router, prefix='/api_service/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api_service/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api_service/v1/persons', tags=['persons'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        reload=True,
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
