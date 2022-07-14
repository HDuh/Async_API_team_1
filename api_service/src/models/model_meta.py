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
        return model_class
