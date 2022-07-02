import pytest

from functional.testdata.models.genre_fake_model import GenreFactory

SERVICE_URL = 'http://127.0.0.1:8000'


@pytest.mark.asyncio
async def test_genre(create_index):
    genres = GenreFactory.build_batch(1)
    index = genres[0].Config.es_index
    schema = genres[0].Config.schema
    create_index(index, schema)
    for genre in genres:
        await genre.manager.save(genre)
    print(1)
    # TODO: нужен фастапи клиент в виде фикстуры
    # TODO: генерация нужного количества объектов create_batch
    # возможно в моделях потребуется get or create
