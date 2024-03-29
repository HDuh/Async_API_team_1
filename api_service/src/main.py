import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.api.v1 import films, genres, persons
from src.core import PROJECT_NAME, LOGGING, REDIS_CONFIG, ELASTIC_CONFIG
from src.db import redis, elastic
from src.models import Film, Genre, Person

models = (Film, Genre, Person,)

app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api_service/openapi',
    openapi_url='/api_service/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.from_url(REDIS_CONFIG, encoding='utf-8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis.redis), prefix=f'{PROJECT_NAME}_cache')
    elastic.es = AsyncElasticsearch(ELASTIC_CONFIG)
    for model_class in models:
        await model_class.manager.async_check_or_create_index()


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films.router, prefix='/api_service/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api_service/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api_service/v1/persons', tags=['persons'])

if __name__ == '__main__':
    # only for develop (production use nginx + gunicorn server)
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        reload=True,
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
