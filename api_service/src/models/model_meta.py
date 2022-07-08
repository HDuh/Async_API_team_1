import asyncio

__all__ = (
    'MetaModel',
)


class MetaModel(type):
    """Метакласс для создания классов моделей.
    Менеджер инициализируется и становится атрибутом экземпляра класса модели.
    """

    def __new__(cls, name, bases, dct):
        model_class = super().__new__(cls, name, bases, dct)
        model_class.manager = model_class.ManagerConfig.manager(model_class)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(model_class.manager.async_check_or_create_index())
        return model_class
