from uuid import UUID

from app.common.context import Context
from app.models import Status
from app.services.http_client import ServiceResponse

SERVICE_URL = "http://chat-service"


class ChatsClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # chats

    async def create_chat(self, name: str, topic: str,
                          read_privileges: int, write_privileges: int,
                          auto_join: bool, created_by: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/chats",
            json={
                "name": name,
                "topic": topic,
                "read_privileges": read_privileges,
                "write_privileges": write_privileges,
                "auto_join": auto_join,
                "created_by": created_by,
            },
        )
        return response

    async def get_chat(self, chat_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
        )
        return response

    async def get_chats(self,
                        name: str | None = None,
                        topic: str | None = None,
                        read_privileges: int | None = None,
                        write_privileges: int | None = None,
                        auto_join: bool | None = None,
                        status: Status | None = Status.ACTIVE,
                        created_by: int | None = None) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats",
            params={
                "name": name,
                "topic": topic,
                "read_privileges": read_privileges,
                "write_privileges": write_privileges,
                "auto_join": auto_join,
                "status": status,
                "created_by": created_by,
            },
        )
        return response

    async def partial_update_chat(self, chat_id: int,
                                  json: dict  # TODO: model?
                                  ) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
            json=json,
        )
        return response

    async def delete_chat(self, chat_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
        )
        return response

    # members

    async def join_chat(self, chat_id: int, session_id: UUID, account_id: int,
                        username: str, privileges: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="POST",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}/members",
            json={
                "session_id": session_id,
                "account_id": account_id,
                "username": username,
                "privileges": privileges,
            },
        )
        return response

    async def leave_chat(self, chat_id: int, session_id: UUID) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}/members/{session_id}",
        )
        return response

    async def get_members(self, chat_id: int) -> ServiceResponse:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}/members",
        )
        return response
