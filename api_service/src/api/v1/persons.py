import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Person

from services import PersonsService, get_persons_service, FilmsService,  get_films_service

router = APIRouter()


class PersonApiSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    role: list[str]
    film_ids: list[uuid.UUID]


class PersonFilm(BaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float


@router.get('/{person_id}', response_model=PersonApiSchema)
# @cache()
async def person_details(person_id: uuid.UUID) -> PersonApiSchema:
    person = await Person.manager().get(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonApiSchema(id=person.id, full_name=person.full_name, role=person.role, film_ids=person.film_ids)


@router.get('', response_model=list[PersonApiSchema])
# @cache()
async def all_persons(persons_service: PersonsService = Depends(get_persons_service)) -> list[PersonApiSchema]:
    persons = await persons_service.get_all_data()
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return [
        PersonApiSchema(id=person.id, full_name=person.full_name, role=person.role, film_ids=person.film_ids)
        for person in persons
    ]


# @router.get('/{person_id}/film', response_model=list[PersonFilm])
# # @cache()
# async def person_film(person_id: str, person_service: PersonService = Depends(get_person_service),
#                       films_service: FilmsService = Depends(get_films_service)):
#     person = await person_service.get_by_id(person_id)
#     if not person:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
#     all_films = await films_service.get_all_data()
#     person_films = [
#         PersonFilm(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
#         for film in all_films
#         if film.id in person.film_ids
#     ]
#     return person_films
