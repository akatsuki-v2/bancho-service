from datetime import datetime
from uuid import UUID

from app.common import logging
from app.common.context import Context
from app.models.accounts import Account
from app.models.presences import Presence
from app.models.queued_packets import QueuedPacket
from app.models.sessions import Session
from app.models.spectators import Spectator
from app.models.stats import Stats

SERVICE_URL = "http://users-service"


class UsersClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # accounts

    async def sign_up(self, username: str, password_md5: str,
                      email_address: str, country: str) -> Account | None:
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
        if response.status_code not in range(200, 300):
            logging.error("Failed to sign up",
                          status=response.status_code,
                          response=response.json)
            return None

        return Account(**response.json['data'])

    async def get_accounts(self) -> list[Account] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get accounts",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Account(**rec) for rec in response.json['data']]

    async def get_account(self, account_id: int) -> Account | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get account",
                          status=response.status_code,
                          response=response.json)
            return None

        return Account(**response.json['data'])

    async def partial_update_account(self, account_id: int,
                                     json: dict  # TODO: model?
                                     ) -> Account | None:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
            json=json,
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to update account",
                          status=response.status_code,
                          response=response.json)
            return None

        return Account(**response.json['data'])

    async def delete_account(self, account_id: int) -> Account | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to delete account",
                          status=response.status_code,
                          response=response.json)
            return None

        return Account(**response.json['data'])

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
                           a_count: int) -> Stats | None:
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
        if response.status_code not in range(200, 300):
            logging.error("Failed to create stats",
                          status=response.status_code,
                          response=response.json)
            return None

        return Stats(**response.json['data'])

    async def get_stats(self, account_id: int, game_mode: int) -> Stats | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get stats",
                          status=response.status_code,
                          response=response.json)
            return None

        return Stats(**response.json['data'])

    async def get_all_account_stats(self, account_id: int) -> list[Stats] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get all account stats",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Stats(**rec) for rec in response.json['data']]

    async def partial_update_stats(self, account_id: int, game_mode: int,
                                   json: dict  # TODO: model?
                                   ) -> Stats | None:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
            json=json,
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to update stats",
                          status=response.status_code,
                          response=response.json)
            return None

        return Stats(**response.json['data'])

    async def delete_stats(self, account_id: int, game_mode: int) -> Stats | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/accounts/{account_id}/stats/{game_mode}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to delete stats",
                          status=response.status_code,
                          response=response.json)
            return None

    # sessions

    async def log_in(self, identifier: str, passphrase: str,
                     user_agent: str) -> Session | None:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions",
            json={
                "identifier": identifier,
                "passphrase": passphrase,
                "user_agent": user_agent,
            },
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to log in",
                          status=response.status_code,
                          response=response.json)
            return None

        return Session(**response.json['data'])

    async def log_out(self, session_id: UUID) -> Session | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to log out",
                          status=response.status_code,
                          response=response.json)
            return None

        return Session(**response.json['data'])

    async def get_session(self, session_id: UUID) -> Session | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get session",
                          status=response.status_code,
                          response=response.json)
            return None

        return Session(**response.json['data'])

    async def get_all_sessions(self, account_id: int | None = None,
                               user_agent: str | None = None) -> list[Session] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions",
            params={
                "account_id": account_id,
                "user_agent": user_agent,
            },
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get all sessions",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Session(**rec) for rec in response.json['data']]

    async def partial_update_session(self, session_id: UUID,
                                     expires_at: datetime | None,
                                     ) -> Session | None:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}",
            json={
                "expires_at": expires_at.isoformat() if expires_at else None,
            }
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to update session",
                          status=response.status_code,
                          response=response.json)
            return None

        return Session(**response.json['data'])

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
                              ) -> Presence | None:
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
        if response.status_code not in range(200, 300):
            logging.error("Failed to create presence",
                          status=response.status_code,
                          response=response.json)
            return None

        return Presence(**response.json['data'])

    async def get_presence(self, session_id: UUID) -> Presence | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/presences/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get presence",
                          status=response.status_code,
                          response=response.json)
            return None

        return Presence(**response.json['data'])

    async def get_all_presences(self, game_mode: int | None = None,
                                account_id: int | None = None,
                                username: str | None = None,
                                country_code: str | None = None,
                                # privileges: int | None = None,

                                osu_version: str | None = None,
                                utc_offset: int | None = None,
                                display_city: bool | None = None,
                                pm_private: bool | None = None,
                                ) -> list[Presence] | None:
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
        if response.status_code not in range(200, 300):
            logging.error("Failed to get all presences",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Presence(**rec) for rec in response.json['data']]

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
                                      ) -> Presence | None:
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
        if response.status_code not in range(200, 300):
            logging.error("Failed to update presence",
                          status=response.status_code,
                          response=response.json)
            return None

        return Presence(**response.json['data'])

    async def delete_presence(self, session_id: UUID) -> Presence | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/presences/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to delete presence",
                          status=response.status_code,
                          response=response.json)
            return None

        return Presence(**response.json['data'])

    # queued packets

    # TODO: this returning bool is inconsistent
    # we should probably have a ServiceError class to differentiate from
    # returning nothing
    async def enqueue_packet(self, session_id: UUID, data: list[int]
                             ) -> bool:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}/queued-packets",
            json={"data": data},
        )
        return response.status_code in range(200, 300)

    async def deqeue_all_packets(self, session_id: UUID) -> list[QueuedPacket] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{session_id}/queued-packets",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to dequeue all packets",
                          status=response.status_code,
                          response=response.json)
            return None

        return [QueuedPacket(**rec) for rec in response.json['data']]

    # spectators

    async def create_spectator(self, host_session_id: UUID, session_id: UUID,
                               account_id: int) -> Spectator | None:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators",
            json={"session_id": session_id,
                  "account_id": account_id},
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to create spectator",
                          status=response.status_code,
                          response=response.json)
            return None

        return Spectator(**response.json['data'])

    async def delete_spectator(self, host_session_id: UUID, session_id: UUID
                               ) -> Spectator | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to delete spectator",
                          status=response.status_code,
                          response=response.json)
            return None

        return Spectator(**response.json['data'])

    async def get_spectators(self, host_session_id: UUID) -> list[Spectator] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{host_session_id}/spectators",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get spectators",
                          status=response.status_code,
                          response=response.json)
            return None

        return [Spectator(**rec) for rec in response.json['data']]

    async def get_spectator_host(self, spectator_session_id: UUID) -> UUID | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/sessions/{spectator_session_id}/spectating",
        )
        if response.status_code not in range(200, 300):
            logging.error("Failed to get spectator host",
                          status=response.status_code,
                          response=response.json)
            return None

        return UUID(response.json['data'])
