from app.common import logging
from app.common import settings
from app.common.context import Context
from app.models.scores import Score
from app.services.http_client import ServiceResponse

SERVICE_URL = "http://scores-service"


class ScoresClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # scores

    async def submit_score(self, beatmap_md5: str, account_id: int, username: str,
                           mode: str, mods: int, score: int, performance: float,
                           accuracy: float, max_combo: int, count_50s: int,
                           count_100s: int, count_300s: int, count_gekis: int,
                           count_katus: int, count_misses: int, grade: str,
                           passed: bool, perfect: bool, seconds_elapsed: int,
                           anticheat_flags: int, client_checksum: str,
                           status: str) -> Score | None:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/scores",
            json={
                "beatmap_md5": beatmap_md5,
                "account_id": account_id,
                "username": username,
                "mode": mode,
                "mods": mods,
                "score": score,
                "performance": performance,
                "accuracy": accuracy,
                "max_combo": max_combo,
                "count_50s": count_50s,
                "count_100s": count_100s,
                "count_300s": count_300s,
                "count_gekis": count_gekis,
                "count_katus": count_katus,
                "count_misses": count_misses,
                "grade": grade,
                "passed": passed,
                "perfect": perfect,
                "seconds_elapsed": seconds_elapsed,
                "anticheat_flags": anticheat_flags,
                "client_checksum": client_checksum,
                "status": status,
            },
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to submit score",
                          status=response.status_code,
                          response=response.json)
            return None

        return Score(**response.json['data'])

    async def get_score(self, score_id: int) -> Score | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/scores/{score_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get score",
                          status=response.status_code,
                          response=response.json)
            return None

        return Score(**response.json['data'])

    async def get_scores(self, beatmap_md5: str | None = None,
                         account_id: int | None = None,
                         mode: str | None = None,
                         mods: int | None = None,
                         passed: bool | None = None,
                         perfect: bool | None = None,
                         status: str | None = None,
                         page: int = 1,
                         page_size: int = settings.DEFAULT_PAGE_SIZE,
                         ) -> list[Score] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/scores",
            params={
                "beatmap_md5": beatmap_md5,
                "account_id": account_id,
                "mode": mode,
                "mods": mods,
                "passed": passed,
                "perfect": perfect,
                "status":  status,
                "page": page,
                "page_size": page_size,
            },
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get scores",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Score(**rec) for rec in response.json['data']]

    async def delete_score(self, score_id: int) -> Score | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/scores/{score_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to delete score",
                          status=response.status_code,
                          response=response.json)
            return None

        return Score(**response.json['data'])
