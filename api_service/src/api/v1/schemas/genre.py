import uuid

from pydantic import BaseModel

__all__ = (
    'GenreApiSchema',
)


class GenreApiSchema(BaseModel):
    id: uuid.UUID
    name: str
