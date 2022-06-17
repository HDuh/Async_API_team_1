import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Genre
from services import GenresService, get_genres_service

router = APIRouter()


class GenreApiSchema(BaseModel):
    id: uuid.UUID
    name: str


@router.get('/{genre_id}', response_model=GenreApiSchema)
# @cache()
async def genre_details(genre_id: uuid.UUID) -> GenreApiSchema:
    genre = await Genre.manager().get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreApiSchema(id=genre.id, name=genre.name)


@router.get('', response_model=list[Genre])
# @cache()
async def all_genres(genres_service: GenresService = Depends(get_genres_service)) -> list[Genre]:
    genres = await genres_service.get_all_data()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [Genre(id=genre.id, name=genre.name) for genre in genres]
