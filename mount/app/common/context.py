from __future__ import annotations

from abc import ABC
from abc import abstractproperty

from app.services import database


class Context(ABC):
    @abstractproperty
    def db(self) -> database.ServiceDatabase:
        ...