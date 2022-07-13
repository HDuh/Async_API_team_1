__all__ = (
    'BuildFromModelMixin',
)


class BuildFromModelMixin:
    """Это дает соответствие строгим интерфейсам."""

    @classmethod
    def build_from_model(cls, instance):
        return cls(**instance.__dict__)
