import logging
from typing import Any, Type

# _log_format: str = "%(asctime)s [%(levelname)s]: %(message)s  | " \
#                    " %(name)s  (%(filename)s).%(funcName)s(%(lineno)d)"
_log_format: str = "%(asctime)s [%(levelname)s]: %(message)s "


def get_stream_handler() -> logging.StreamHandler:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_log_format,
                                                  datefmt='%d.%m.%Y %I:%M:%S'))
    return stream_handler


def get_logger(name: Any) -> Type[logging.getLogger]:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_stream_handler())
    return logger
