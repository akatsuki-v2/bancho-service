from __future__ import annotations

from fastapi import APIRouter

from . import bancho
from . import web

router = APIRouter()

router.include_router(bancho.router)
router.include_router(web.router)
