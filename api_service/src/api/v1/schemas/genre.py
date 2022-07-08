import uuid

from pydantic import BaseModel

from .schemas_mixins import BuildFromModelMixin

__all__ = (
    'GenreApiSchema',
)


class GenreApiSchema(BaseModel, BuildFromModelMixin):
    id: uuid.UUID
    name: str
