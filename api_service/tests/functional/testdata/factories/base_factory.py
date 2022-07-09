from factory import Factory


class ElasticBaseFactory(Factory):
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Построение экземпляра модели model_class"""
        if args:
            raise ValueError('NEED VALUES!')
        instance = model_class(**kwargs)
        return instance

    @classmethod
    async def async_create(cls, **kwargs):
        """Создание экземпляра класса модели"""
        instance = cls.build(**kwargs)
        await instance.save()
        return instance

    @classmethod
    async def async_create_batch(cls, size, **kwargs):
        """Создание определенного количества экземпляров класса модели"""
        return [await cls.get_or_create(**kwargs) for _ in range(size)]

    @classmethod
    async def get_or_create(cls, **kwargs):
        """Получение или создание экземпляра класса модели"""
        instance = cls.build(**kwargs)
        return await instance.get_or_create()

    @classmethod
    async def async_build(cls, **kwargs):
        """Построение экземпляра класса модели"""
        instance = cls.build(**kwargs)
        return instance

    @classmethod
    async def async_build_batch(cls, size, **kwargs):
        """Построение определенного количества экземпляров класса модели"""
        instance = cls.build_batch(size, **kwargs)
        return instance
