from typing import Awaitable
from typing import Callable
from uuid import UUID

from app.common import logging
from app.common import serial
from app.common.context import Context
from app.services.chats_client import ChatsClient
from app.services.users_client import UsersClient

PACKET_HANDLERS = {}

PacketHandler = Callable[[Context, UUID, bytes], Awaitable[bytes]]


def get_packet_handler(packet_id: int) -> PacketHandler | None:
    return PACKET_HANDLERS.get(packet_id)


async def handle_packet_event(ctx: Context, session_id: UUID, packet_id: int,
                              packet_data: bytes) -> bytes:
    packet_handler = get_packet_handler(packet_id)
    packet_name = serial.client_packet_id_to_name(packet_id)

    if packet_handler is None:
        logging.warning("Unhandled packet", type=packet_name)
        return b""

    logging.info("Handling packet", type=packet_name,
                 length=len(packet_data))

    response_data = await packet_handler(ctx, session_id, packet_data)

    # XXX: temp dev thing
    response_data += serial.write_notification_packet(f"Handled {packet_name}")

    return response_data


def packet_handler(packet_id: int) -> Callable[[PacketHandler], PacketHandler]:
    def decorator(func: PacketHandler) -> PacketHandler:
        PACKET_HANDLERS[packet_id] = func
        return func
    return decorator


@packet_handler(serial.ClientPackets.PING)
async def handle_ping(ctx: Context, session_id: UUID,  packet_data: bytes
                      ) -> bytes:
    # NOTE: this makes osu! send it's next request immediately
    # could be useful for something like a 'low delay mode'?
    # return serial.write_pong_packet()

    return b""


@packet_handler(serial.ClientPackets.LOGOUT)
async def handle_logout(ctx: Context, session_id: UUID, packet_data: bytes
                        ) -> bytes:
    # (?) clear user packet queue

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # delete user presence
    response = await users_client.delete_presence(session_id)
    if response.status_code not in range(200, 300):
        logging.error("Failed to delete user presence",
                      session_id=session_id,
                      status=response.status_code,
                      response=response.json)
        return b""

    # delete user session
    response = await users_client.log_out(session_id)
    if response.status_code not in range(200, 300):
        logging.error("Failed to delete user session",
                      session_id=session_id,
                      status=response.status_code,
                      response=response.json)
        return b""

    # remove user from all chats they're in
    response = await chats_client.get_chats()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get chats",
                      session_id=session_id,
                      status=response.status_code,
                      response=response.json)
        return b""

    chats = response.json
    for chat in chats:
        response = await chats_client.leave_chat(chat["id"], session_id)
        if response.status_code not in range(200, 300):
            logging.error("Failed to leave chat",
                          session_id=session_id,
                          status=response.status_code,
                          response=response.json)
            return b""

    # inform all other players that the user has logged out
    # TODO: should we be fetching the osu-specific sessions here?
    # should sessions be refactored so that we have osu-specific ones?
    response = await users_client.get_all_presences()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get all presences",
                      session_id=session_id,
                      status=response.status_code,
                      response=response.json)
        return b""

    presences = response.json
    for presence in presences:
        if presence["session_id"] == session_id:
            continue

        packet_data = serial.write_user_logout_packet(presence["user_id"])
        response = await users_client.enqueue_data(presence["session_id"],
                                                   list(packet_data))
        if response.status_code not in range(200, 300):
            logging.error("Failed to send logout packet",
                          session_id=session_id,
                          status=response.status_code,
                          response=response.json)
            return b""

    return b""
