from typing import Any

from app.common import json
from app.common.errors import ServiceError


def success(content: Any, status_code: int = 200, headers: dict | None = None) -> json.ORJSONResponse:
    data = {"status": "success", "data": content}
    return json.ORJSONResponse(data, status_code, headers)


# TODO: make this more clear on the business case?


def failure(error: ServiceError, message: str, status_code: int = 400,
            headers: dict | None = None) -> json.ORJSONResponse:
    data = {"status": "error", "error": error, "message": message}
    return json.ORJSONResponse(data, status_code, headers)
