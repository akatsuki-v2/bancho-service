from __future__ import annotations

import json
from typing import Any
from uuid import UUID


def preprocess_json(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: preprocess_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [preprocess_json(v) for v in data]
    elif isinstance(data, UUID):
        return str(data)
    else:
        return data


def loads(s: str | bytes) -> Any:
    return json.loads(s)


def dumps(obj: Any) -> str:
    return json.dumps(obj)
