from __future__ import annotations

from enum import Enum
from enum import IntEnum
from typing import Any
from typing import Mapping
from typing import TypeVar

from pydantic import BaseModel as _pydantic_BaseModel


class Status(str, Enum):
    ACTIVE = 'active'
    DEACTIVATED = 'deactivated'
    DELETED = 'deleted'


class RankedStatus(IntEnum):
    GRAVEYARD = -2
    WORK_IN_PROGRESS = -1
    PENDING = 0
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4


T = TypeVar('T', bound=type['BaseModel'])


class BaseModel(_pydantic_BaseModel):
    class Config:
        anystr_strip_whitespace = True

    @classmethod
    def from_mapping(cls: T, mapping: Mapping[str, Any]) -> T:
        return cls(**{k: mapping[k] for k in cls.__fields__})
