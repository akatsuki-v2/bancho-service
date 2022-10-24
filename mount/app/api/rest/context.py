from app.common.context import Context
from fastapi import Request
from shared_modules.http_client import ServiceHTTPClient


class RequestContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def http_client(self) -> ServiceHTTPClient:
        return self.request.state.http_client
