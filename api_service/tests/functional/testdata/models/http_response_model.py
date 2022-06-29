from dataclasses import dataclass

from multidict import CIMultiDictProxy

__all__ = (
    'HTTPResponse',
)


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
