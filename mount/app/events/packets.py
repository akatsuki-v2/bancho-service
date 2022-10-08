import random
from typing import Awaitable
from typing import Callable

from app.common import logging
from app.common import serial
from app.common.context import Context
from app.models.presences import Presence
from app.models.sessions import Session
from app.models.stats import Stats
from app.services.chats_client import ChatsClient
from app.services.users_client import UsersClient

PACKET_HANDLERS = {}

PacketHandler = Callable[[Context, Session, bytes], Awaitable[bytes]]


def get_packet_handler(packet_id: int) -> PacketHandler | None:
    return PACKET_HANDLERS.get(packet_id)


async def handle_packet_event(ctx: Context, session: Session, packet_id: int,
                              packet_data: bytes) -> bytes:
    packet_handler = get_packet_handler(packet_id)
    packet_name = serial.client_packet_id_to_name(packet_id)

    if packet_handler is None:
        if packet_id != serial.ClientPackets.LOGOUT:
            rand_string = " " * random.randrange(0, 10)
            response_data = serial.write_notification_packet(
                f"[N] {packet_name} ({packet_id}){rand_string}")
        else:
            response_data = b""

        logging.warning("Unhandled packet", type=packet_name)
        return response_data

    logging.info("Handling packet", type=packet_name,
                 length=len(packet_data))

    response_data = await packet_handler(ctx, session, packet_data)

    if packet_id != serial.ClientPackets.LOGOUT:
        rand_string = " " * random.randrange(0, 10)
        response_data += serial.write_notification_packet(
            f"[Y] {packet_name} ({packet_id}){rand_string}")

    return response_data


def packet_handler(packet_id: int) -> Callable[[PacketHandler], PacketHandler]:
    def decorator(func: PacketHandler) -> PacketHandler:
        PACKET_HANDLERS[packet_id] = func
        return func
    return decorator


@packet_handler(serial.ClientPackets.PING)
async def handle_ping(ctx: Context, session: Session,  packet_data: bytes
                      ) -> bytes:
    # NOTE: this makes osu! send it's next request immediately
    # could be useful for something like a 'low delay mode'?
    # return serial.write_pong_packet()

    return b""


@packet_handler(serial.ClientPackets.LOGOUT)
async def handle_logout(ctx: Context, session: Session, packet_data: bytes
                        ) -> bytes:
    # (?) clear user packet queue

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # delete user presence
    response = await users_client.delete_presence(session["session_id"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to delete user presence",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    # delete user session
    response = await users_client.log_out(session["session_id"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to delete user session",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    # remove user from all chats they're in
    response = await chats_client.get_chats()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get chats",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    chats = response.json["data"]
    for chat in chats:
        response = await chats_client.leave_chat(chat["chat_id"],
                                                 session["session_id"])
        if response.status_code not in range(200, 300):
            logging.error("Failed to leave chat",
                          session_id=session["session_id"],
                          status=response.status_code,
                          response=response.json)
            return b""

    # inform all other players that the user has logged out
    # TODO: should we be fetching the osu-specific sessions here?
    # should sessions be refactored so that we have osu-specific ones?
    response = await users_client.get_all_presences()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get all presences",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    presences = response.json["data"]
    for presence in presences:
        if presence["session_id"] == session["session_id"]:
            continue

        logout_data = serial.write_user_logout_packet(presence["user_id"])
        response = await users_client.enqueue_data(presence["session_id"],
                                                   data=list(logout_data))
        if response.status_code not in range(200, 300):
            logging.error("Failed to send logout packet",
                          session_id=session["session_id"],
                          status=response.status_code,
                          response=response.json)
            return b""

    return b""


@packet_handler(serial.ClientPackets.REQUEST_SELF_STATS)
async def handle_request_game_mode_stats(ctx: Context, session: Session,
                                         packet_data: bytes) -> bytes:
    users_client = UsersClient(ctx)

    response = await users_client.get_presence(session["session_id"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to get user presence",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    presence: Presence = response.json["data"]

    response = await users_client.get_stats(session["account_id"],
                                            presence["game_mode"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to get user stats",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    response = await users_client.get_stats(session["account_id"],
                                            presence["game_mode"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to get user stats",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    stats: Stats = response.json["data"]

    return serial.write_user_stats_packet(
        account_id=session["account_id"],
        action=presence["action"],
        info_text=presence["info_text"],
        map_md5=presence["map_md5"],
        mods=presence["mods"],
        mode=presence["game_mode"],
        map_id=presence["map_id"],
        ranked_score=stats["ranked_score"],
        accuracy=stats["accuracy"],
        play_count=stats["play_count"],
        total_score=stats["total_score"],
        global_rank=0,  # TODO
        pp=stats["performance"],
    )


@packet_handler(serial.ClientPackets.REQUEST_ALL_USER_STATS)
async def handle_request_all_user_stats_request(ctx: Context, session: Session,
                                                packet_data: bytes) -> bytes:
    users_client = UsersClient(ctx)

    response = await users_client.get_all_presences()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get all presences",
                      session_id=session["session_id"],
                      status=response.status_code,
                      response=response.json)
        return b""

    response_buffer = bytearray()

    presences: list[Presence] = response.json["data"]
    for presence in presences:
        if presence["session_id"] == session["session_id"]:
            continue

        response = await users_client.get_stats(presence["account_id"],
                                                presence["game_mode"])
        if response.status_code not in range(200, 300):
            logging.error("Failed to get user stats",
                          session_id=session["session_id"],
                          status=response.status_code,
                          response=response.json)
            return b""

        stats: Stats = response.json["data"]

        response_buffer += serial.write_user_stats_packet(
            account_id=stats["account_id"],
            action=presence["action"],
            info_text=presence["info_text"],
            map_md5=presence["map_md5"],
            mods=presence["mods"],
            mode=presence["game_mode"],
            map_id=presence["map_id"],
            ranked_score=stats["ranked_score"],
            accuracy=stats["accuracy"],
            play_count=stats["play_count"],
            total_score=stats["total_score"],
            global_rank=0,  # TODO
            pp=stats["performance"],
        )

    return bytes(response_buffer)
