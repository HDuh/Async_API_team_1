import asyncio

__all__ = (
    'MetaModel',
)


class MetaModel(type):
    """Метакласс для создания классов моделей.
    Менеджер инициализируется и становится атрибутом экземпляра класса модели.
    """

    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        x.manager = x.ManagerConfig.manager(x)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(x.manager.async_check_or_create_index())
        return x
