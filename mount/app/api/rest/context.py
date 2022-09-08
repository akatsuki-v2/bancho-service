from __future__ import annotations

from app.common.context import Context
from app.services import database
from fastapi import Request


class RequestContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def db(self) -> database.ServiceDatabase:
        return self.request.state.db