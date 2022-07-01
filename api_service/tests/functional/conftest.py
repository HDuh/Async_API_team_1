import asyncio
from typing import Optional

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from .settings import ELASTIC_CONFIG, SERVICE_URL, GENRES
from .testdata.models import HTTPResponse
from .testdata.elastic_test_indexes.genre_tests_index import genres_schema
from .testdata.models import GenreFactory
from elasticsearch.helpers import async_bulk


@pytest.fixture
async def es_client():
    client = AsyncElasticsearch(ELASTIC_CONFIG)
    yield client
    await client.close()


# @pytest.fixture
# async def session(scope='session'):
#     session = aiohttp.ClientSession()
#     yield session
#     await session.close()


@pytest.fixture
async def create_index_genre(es_client):
    await es_client.indices.create(index='test_genre', body=genres_schema)
    yield
    await es_client.indices.delete(index='test_genre')


@pytest.fixture
async def fill_genre_index(es_client):
    genres = [GenreFactory.create(name=_) for _ in GENRES]
    doc = (
        {
            '_index': 'test_genre',
            '_id': item['id'],
            **item
        } for item in genres
    )
    await async_bulk(es_client, doc)

# @pytest.fixture
# def make_get_request(session):
#     async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
#         params = params or {}
#         url = SERVICE_URL + '/api/v1' + method  # в боевых системах старайтесь так не делать!
#         async with session.get(url, params=params) as response:
#             return HTTPResponse(
#                 body=await response.json(),
#                 headers=response.headers,
#                 status=response.status,
#             )
#
#     return inner
