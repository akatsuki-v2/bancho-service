from __future__ import annotations

from pydantic import BaseModel as _pydantic_BaseModel

class BaseModel(_pydantic_BaseModel):
    class Config:
        anystr_strip_whitespace = True