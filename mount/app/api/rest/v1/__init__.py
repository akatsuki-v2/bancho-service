from __future__ import annotations

from fastapi import APIRouter

from . import (
    bancho,
)

router = APIRouter()

router.include_router(bancho.router)
