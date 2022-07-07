from pydantic import BaseModel, Field


def page(string):
    return f'page_{string}'


class Pagination(BaseModel):
    number: int | None = Field(default=1, gt=0)
    size: int | None = Field(default=50, gt=0)

    class Config:
        allow_population_by_field_name = True
        alias_generator = page
