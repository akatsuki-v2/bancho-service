from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from shared_modules.http_client import ServiceHTTPClient


class Context(ABC):
    @property
    @abstractmethod
    def http_client(self) -> ServiceHTTPClient:
        ...
