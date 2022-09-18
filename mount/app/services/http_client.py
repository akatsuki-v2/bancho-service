from __future__ import annotations

from typing import Any
from typing import Literal
from typing import Mapping

from app.common import json as jsonu
from httpx import AsyncClient
from httpx import Response as HTTPXResponse
MethodTypes = Literal["POST", "PUT", "PATCH",
                      "GET", "HEAD", "DELETE", "OPTIONS"]


class ServiceResponse:  # TODO: is this stupid?
    def __init__(self, status_code: int, headers: Mapping[str, Any], content: bytes) -> None:
        self.status_code = status_code
        self.headers = headers
        self.content = content

    @property
    def json(self) -> Any:
        return jsonu.loads(self.content)

    @classmethod
    async def from_httpx_response(cls, response: HTTPXResponse) -> "ServiceResponse":
        return cls(
            status_code=response.status_code,
            headers=response.headers,
            content=await response.aread(),
        )


class ServiceHTTPClient(AsyncClient):
    async def service_call(self, *args, **kwargs
                           ) -> ServiceResponse:
        if json := kwargs.get("json"):
            kwargs["json"] = jsonu.preprocess_json(json)

        httpx_response = await self.request(*args, **kwargs)

        response = await ServiceResponse.from_httpx_response(httpx_response)
        return response
