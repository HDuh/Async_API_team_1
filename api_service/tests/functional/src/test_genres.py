import pytest
from httpx import AsyncClient
from fastapi import FastAPI
# from src.main import app
from functional.testdata.models.genre_fake_model import GenreFactory
from urllib.parse import urljoin

SERVICE_URL = 'http://0.0.0.0:8000'

app = FastAPI()


@pytest.mark.asyncio
async def test_genre(create_index, make_get_request):
    genres = GenreFactory.build_batch(1)
    index, schema = genres[0].Config.es_index, genres[0].Config.schema
    await create_index(index, schema)
    for genre in genres:
        await genre.manager.save(genre)
    # async with AsyncClient(app=app, base_url=SERVICE_URL) as ac:
    #     response = await ac.get(urljoin(SERVICE_URL, '/api_service/v1/genres'))
    response = await make_get_request('/genres')
    print(1)
    # TODO: нужен фастапи клиент в виде фикстуры
    # TODO: генерация нужного количества объектов create_batch
    # возможно в моделях потребуется get or create
