import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

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


@pytest.fixture
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def create_index(es_client):
    _index = None

    async def inner(index, schema):
        nonlocal _index
        _index = index
        # await es_client.indices.create(index=index, body=schema)

    yield inner
    await es_client.indices.delete(index=_index)


# @pytest.fixture
# async def delete_index(es_client):
#     async def inner(index):
#         await es_client.indices.delete(index=index)
#
#     yield inner

@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + '/api_service/v1/genres' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
