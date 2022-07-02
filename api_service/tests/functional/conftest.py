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
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def fastapi_client():
    client = TestClient(app)
    yield client


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
def create_index(es_client):
    async def inner(index, schema):
        await es_client.indices.create(index=index, body=schema)
        yield
        await es_client.indices.delete(index=index)
    return inner

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
