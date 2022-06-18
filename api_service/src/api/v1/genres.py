import uuid
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from models import Genre
from .schemas import GenreApiSchema

router = APIRouter()


@router.get('', response_model=list[Genre])
# @cache()
async def all_genres() -> list[Genre]:
    """Получение всех жанров"""
    genres = await Genre.manager.filter()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [Genre(**genre.dict()) for genre in genres]


@router.get('/{genre_id}', response_model=GenreApiSchema)
# @cache()
async def detailed_genre_info(genre_id: uuid.UUID) -> GenreApiSchema:
    """Получение конкретного жанра оп id"""
    genre = await Genre.manager.get(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return GenreApiSchema(**genre.dict())