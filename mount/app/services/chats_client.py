from uuid import UUID

from app.common.context import Context
from app.models import Status
from app.models.chats import Chat
from app.models.members import Member
from shared_modules import logger

SERVICE_URL = "http://chat-service"


class ChatsClient:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    # chats

    async def create_chat(self, name: str, topic: str,
                          read_privileges: int, write_privileges: int,
                          auto_join: bool, created_by: int) -> Chat | None:
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
        if response.status_code not in range(200, 300):
            logger.error("Failed to create chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Chat(**response.json['data'])

    async def get_chat(self, chat_id: int) -> Chat | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to get chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Chat(**response.json['data'])

    async def get_chats(self,
                        name: str | None = None,
                        topic: str | None = None,
                        read_privileges: int | None = None,
                        write_privileges: int | None = None,
                        auto_join: bool | None = None,
                        instance: bool | None = None,
                        status: Status | None = Status.ACTIVE,
                        created_by: int | None = None) -> list[Chat] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats",
            params={
                "name": name,
                "topic": topic,
                "read_privileges": read_privileges,
                "write_privileges": write_privileges,
                "auto_join": auto_join,
                "instance": instance,
                "status": status,
                "created_by": created_by,
            },
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to get chats",
                         status=response.status_code,
                         response=response.json)
            return None

        return [Chat(**rec) for rec in response.json['data']]

    async def partial_update_chat(self, chat_id: int,
                                  name: str | None = None,
                                  topic: str | None = None,
                                  read_privileges: int | None = None,
                                  write_privileges: int | None = None,
                                  auto_join: bool | None = None,
                                  status: Status | None = None,
                                  ) -> Chat | None:
        response = await self.ctx.http_client.service_call(
            method="PATCH",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
            json={
                "name": name,
                "topic": topic,
                "read_privileges": read_privileges,
                "write_privileges": write_privileges,
                "auto_join": auto_join,
                "status": status,
            },
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to update chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Chat(**response.json['data'])

    async def delete_chat(self, chat_id: int) -> Chat | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}",
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to delete chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Chat(**response.json['data'])

    # members

    async def join_chat(self, chat_id: int, session_id: UUID, account_id: int,
                        username: str, privileges: int) -> Member | None:
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
        if response.status_code not in range(200, 300):
            logger.error("Failed to join chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Member(**response.json['data'])

    async def leave_chat(self, chat_id: int, session_id: UUID) -> Member | None:
        response = await self.ctx.http_client.service_call(
            method="DELETE",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}/members/{session_id}",
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to leave chat",
                         status=response.status_code,
                         response=response.json)
            return None

        return Member(**response.json['data'])

    async def get_members(self, chat_id: int) -> list[Member] | None:
        response = await self.ctx.http_client.service_call(
            method="GET",
            url=f"{SERVICE_URL}/v1/chats/{chat_id}/members",
        )
        if response.status_code not in range(200, 300):
            logger.error("Failed to get chat members",
                         status=response.status_code,
                         response=response.json)
            return None

        return [Member(**rec) for rec in response.json['data']]  # TODO
