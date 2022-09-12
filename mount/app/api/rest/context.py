from __future__ import annotations

from app.common.context import Context
from app.services.http_client import ServiceHTTPClient
from fastapi import Request


class RequestContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def http_client(self) -> ServiceHTTPClient:
        return self.request.state.http_client
