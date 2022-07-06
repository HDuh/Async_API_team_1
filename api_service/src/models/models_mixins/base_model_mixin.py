__all__ = (
    'BaseModelMixin',
)


class BaseModelMixin:

    async def save(self) -> None:
        await self.manager.async_save(self)

    async def delete(self) -> None:
        await self.manager.async_delete(self)

    async def get_or_create(self):
        instance = await self.manager.get(self.id)
        if instance:
            return instance
        await self.save()
        return self
