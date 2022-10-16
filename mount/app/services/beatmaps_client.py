from datetime import datetime
from typing import Literal
from uuid import UUID

from app.common import settings
from app.common.context import Context
from app.services.http_client import ServiceResponse

SERVICE_URL = "http://beatmaps-service"


class BeatmapsClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # beatmaps

    async def get_beatmap(self, beatmap_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/beatmaps/{beatmap_id}",
        )
        return response

    async def get_beatmaps(self, set_id: int | None = None,
                           md5_hash: str | None = None,
                           mode: Literal['osu', 'taiko',
                                         'fruits', 'mania'] | None = None,
                           ranked_status: int | None = None,
                           status: str | None = None,
                           page: int = 1,
                           page_size: int = settings.DEFAULT_PAGE_SIZE,
                           ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/beatmaps",
            params={
                "set_id": set_id,
                "md5_hash": md5_hash,
                "mode": mode,
                "ranked_status": ranked_status,
                "status":  status,
                "page": page,
                "page_size": page_size,
            },
        )
        return response
