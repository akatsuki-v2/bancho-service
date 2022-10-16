from datetime import datetime
from uuid import UUID

from app.common.context import Context
from app.services.http_client import ServiceResponse

SERVICE_URL = "http://users-service"


class UsersClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # accounts

    async def sign_up(self, username: str, password_md5: str,
                      email_address: str, country: str) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/accounts",
            json={
                "username": username,
                "password": password_md5,
                "email_address": email_address,
                "country": country,
            },
        )
        return response

    async def get_accounts(self) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts",
        )
        return response

    async def get_account(self, account_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
        )
        return response

    async def partial_update_account(self, account_id: int,
                                     json: dict  # TODO: model?
                                     ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
            json=json,
        )
        return response

    async def delete_account(self, account_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
        )
        return response

    # stats

    async def create_stats(self,
                           account_id: int,
                           game_mode: int,
                           total_score: int,
                           ranked_score: int,
                           performance: int,
                           play_count: int,
                           play_time: int,
                           accuracy: float,
                           max_combo: int,
                           total_hits: int,
                           replay_views: int,
                           xh_count: int,
                           x_count: int,
                           sh_count: int,
                           s_count: int,
                           a_count: int):
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats",
            json={
                "game_mode": game_mode,
                "total_score": total_score,
                "ranked_score": ranked_score,
                "performance": performance,
                "play_count": play_count,
                "play_time": play_time,
                "accuracy": accuracy,
                "max_combo": max_combo,
                "total_hits": total_hits,
                "replay_views": replay_views,
                "xh_count": xh_count,
                "x_count": x_count,
                "sh_count": sh_count,
                "s_count": s_count,
                "a_count": a_count,
            },
        )
        return response

    async def get_stats(self, account_id: int, game_mode: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
        )
        return response

    async def get_all_account_stats(self, account_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats",
        )
        return response

    async def partial_update_stats(self, account_id: int, game_mode: int,
                                   json: dict  # TODO: model?
                                   ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
            json=json,
        )
        return response

    async def delete_stats(self, account_id: int, game_mode: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
        )
        return response

    # sessions

    async def log_in(self, identifier: str, passphrase: str,
                     user_agent: str) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions",
            json={
                "identifier": identifier,
                "passphrase": passphrase,
                "user_agent": user_agent,
            },
        )
        return response

    async def log_out(self, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
        )
        return response

    async def get_session(self, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
        )
        return response

    async def get_all_sessions(self, account_id: int | None = None,
                               user_agent: str | None = None) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions",
            params={
                "account_id": account_id,
                "user_agent": user_agent,
            },
        )
        return response

    async def partial_update_session(self, session_id: UUID,
                                     expires_at: datetime | None,
                                     ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
            json={
                "expires_at": expires_at.isoformat() if expires_at else None,
            }
        )
        return response

    # presence

    async def create_presence(self, session_id: UUID, game_mode: int,
                              account_id: int,
                              username: str,
                              country_code: int,
                              privileges: int,
                              latitude: float,
                              longitude: float,
                              action: int,
                              info_text: str,
                              map_md5: str,
                              map_id: int,
                              mods: int,
                              osu_version: str,
                              utc_offset: int,
                              display_city: bool,
                              pm_private: bool,
                              ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/presences",
            json={
                "session_id": session_id,
                "game_mode": game_mode,
                "account_id": account_id,
                "username": username,
                "country_code": country_code,
                "privileges": privileges,
                "latitude": latitude,
                "longitude": longitude,
                "action": action,
                "info_text": info_text,
                "map_md5": map_md5,
                "map_id": map_id,
                "mods": mods,

                "osu_version": osu_version,
                "utc_offset": utc_offset,
                "display_city": display_city,
                "pm_private": pm_private,
            },
        )
        return response

    async def get_presence(self, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/presences/{session_id}",
        )
        return response

    async def get_all_presences(self, game_mode: int | None = None,
                                account_id: int | None = None,
                                username: str | None = None,
                                country_code: str | None = None,
                                # privileges: int | None = None,

                                osu_version: str | None = None,
                                utc_offset: int | None = None,
                                display_city: bool | None = None,
                                pm_private: bool | None = None,
                                ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/presences",
            params={
                "game_mode": game_mode,
                "account_id": account_id,
                "username": username,
                "country_code": country_code,
                # "privileges": privileges,
                "osu_version": osu_version,
                "utc_offset": utc_offset,
                "display_city": display_city,
                "pm_private": pm_private,
            },
        )
        return response

    async def partial_update_presence(self, session_id: UUID,
                                      game_mode: int | None = None,
                                      username: str | None = None,
                                      country_code: int | None = None,
                                      privileges: int | None = None,
                                      latitude: float | None = None,
                                      longitude: float | None = None,
                                      action: int | None = None,
                                      info_text: str | None = None,
                                      map_md5: str | None = None,
                                      map_id: int | None = None,
                                      mods: int | None = None,

                                      osu_version: str | None = None,
                                      utc_offset: int | None = None,
                                      display_city: bool | None = None,
                                      pm_private: bool | None = None,
                                      ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/presences/{session_id}",
            json={
                "game_mode": game_mode,
                "username": username,
                "country_code": country_code,
                "privileges": privileges,
                "latitude": latitude,
                "longitude": longitude,
                "action": action,
                "info_text": info_text,
                "map_md5": map_md5,
                "map_id": map_id,
                "mods": mods,

                "osu_version": osu_version,
                "utc_offset": utc_offset,
                "display_city": display_city,
                "pm_private": pm_private,
            },
        )
        return response

    async def delete_presence(self, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/presences/{session_id}",
        )
        return response

    # queued packets

    async def enqueue_data(self, session_id: UUID, data: list[int]
                           ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}/queued-packets",
            json={"data": data},
        )
        return response

    async def deqeue_all_data(self, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}/queued-packets",
        )
        return response

    # spectators

    async def create_spectator(self, host_session_id: UUID, session_id: UUID,
                               account_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators",
            json={"session_id": session_id,
                  "account_id": account_id},
        )
        return response

    async def delete_spectator(self, host_session_id: UUID, session_id: UUID
                               ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators/{session_id}",
        )
        return response

    async def get_spectators(self, host_session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators",
        )
        return response

    async def get_spectator_host(self, spectator_session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{spectator_session_id}/spectating",
        )
        return response
