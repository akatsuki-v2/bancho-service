from __future__ import annotations

from typing import Any
from typing import Literal
from typing import Mapping

from app.common import json as jsonu
from app.common.context import Context
from httpx import Response as HTTPXResponse
from httpx._types import CookieTypes
from httpx._types import HeaderTypes
from httpx._types import QueryParamTypes
from httpx._types import RequestContent
from httpx._types import RequestData
from httpx._types import RequestFiles
from httpx._types import URLTypes
MethodTypes = Literal["POST", "PUT", "PATCH",
                      "GET", "HEAD", "DELETE", "OPTIONS"]


# TODO: read & implement things from
# https://www.python-httpx.org/advanced


class ServiceResponse:
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


async def forward_request(ctx: Context,
                          method: MethodTypes,
                          url: URLTypes,
                          content: RequestContent | None = None,
                          data: RequestData | None = None,
                          files: RequestFiles | None = None,
                          json: Any | None = None,
                          params: QueryParamTypes | None = None,
                          headers: HeaderTypes | None = None,
                          cookies: CookieTypes | None = None,
                          ) -> ServiceResponse:
    if json is not None:
        json = jsonu.preprocess_json(json)

    httpx_response = await ctx.http_client.request(method=method,
                                                   content=content,
                                                   data=data,
                                                   url=url,
                                                   files=files,
                                                   json=json,
                                                   params=params,
                                                   headers=headers,
                                                   cookies=cookies)

    response = await ServiceResponse.from_httpx_response(httpx_response)
    return response
