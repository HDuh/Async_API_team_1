import orjson

from src.models.model_manager import ModelManager

__all__ = (
    'ManagerMixIn',
)


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class ManagerMixIn:
    class ManagerConfig:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        manager = ModelManager
