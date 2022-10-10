from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.api.rest.context import RequestContext
from app.common import logging
from app.common import serial
from app.events.packets import handle_packet_event
from app.models.queued_packets import QueuedPacket
from app.models.sessions import LoginData
from app.models.sessions import Session
from app.services.chats_client import ChatsClient
from app.services.users_client import UsersClient
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from fastapi import Response

router = APIRouter()


def parse_login_data(data: bytes) -> LoginData:
    """Parse data from the body of a login request."""
    (
        username,
        password_md5,
        remainder,
    ) = data.decode().split("\n", maxsplit=2)

    (
        osu_version,
        utc_offset,
        display_city,
        client_hashes,
        pm_private,
    ) = remainder.split("|", maxsplit=4)

    (
        osu_path_md5,
        adapters_str,
        adapters_md5,
        uninstall_md5,
        disk_signature_md5,
    ) = client_hashes[:-1].split(":", maxsplit=4)

    return {
        "username": username,
        "password_md5": password_md5,
        "osu_version": osu_version,
        "utc_offset": int(utc_offset),
        "display_city": display_city == "1",
        "pm_private": pm_private == "1",
        "osu_path_md5": osu_path_md5,
        "adapters_str": adapters_str,
        "adapters_md5": adapters_md5,
        "uninstall_md5": uninstall_md5,
        "disk_signature_md5": disk_signature_md5,
    }


@router.post("/v1/login")
async def login(request: Request, ctx: RequestContext = Depends()):
    login_data = parse_login_data(await request.body())

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # create user session
    response = await users_client.log_in(login_data["username"],
                                         login_data["password_md5"],
                                         user_agent="osu!")
    if response.status_code not in range(200, 300):
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    session_id = UUID(response.json["data"]["session_id"])
    account_id: int = response.json["data"]["account_id"]

    # TODO: privileges
    privileges = 2_147_483_647
    def is_restricted(server_privs: int): return False
    def to_client_privileges(server_privs: int): return server_privs & 0xff

    # TODO: endpoint to submit client hashes
    # (osu_path_md5, adapters_str, adapters_md5, uninstall_md5, disk_signature_md5)

    response_buffer = bytearray()
    response_buffer += serial.write_protocol_version_packet(19)
    response_buffer += serial.write_account_id_packet(account_id)
    response_buffer += serial.write_privileges_packet(privileges)

    response = await chats_client.get_chats()
    if response.status_code not in range(200, 300):
        logging.error("Failed to fetch chats", session_id=session_id,
                      status_code=response.status_code, response=response.json)
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    chats: list[dict[str, Any]] = response.json["data"]

    for chat in chats:
        if chat["name"] == "#lobby":
            continue

        response = await chats_client.get_members(chat["chat_id"])
        if response.status_code not in range(200, 300):
            logging.error("Failed to fetch chats", session_id=session_id,
                          status_code=response.status_code, response=response.json)
            return Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)

        members: list[dict[str, Any]] = response.json["data"]

        response_buffer += serial.write_channel_info_packet(
            channel=chat["name"],
            topic=chat["topic"],
            user_count=len(members),
        )

        # TODO: enqueue to other players that we've joined

    response_buffer += serial.write_channel_info_end_packet()

    # TODO: unhardcode these into an sql table
    # response_buffer += serial.write_main_menu_icon_packet(
    #     icon_url="https://akatsuki.pw/static/images/logos/logo.png",
    #     onclick_url="https://akatsuki.pw",
    # )

    response_buffer += serial.write_friends_list_packet([])  # TODO: friends
    response_buffer += serial.write_silence_end_packet(0)  # TODO: silences

    # TODO: geolocation
    country_code = 38
    latitude = 48.23
    longitude = 16.37

    # TODO: global player rankings
    def get_global_rank(account_id: int) -> int:
        return 0

    # create user presence
    response = await users_client.create_presence(
        session_id,
        game_mode=0,
        account_id=account_id,
        username=login_data["username"],
        country_code=country_code,
        privileges=privileges,
        latitude=latitude,
        longitude=longitude,
        action=0,
        info_text="",
        map_md5="",
        map_id=0,
        mods=0,
        osu_version=login_data["osu_version"],
        utc_offset=login_data["utc_offset"],
        display_city=login_data["display_city"],
        pm_private=login_data["pm_private"])
    if response.status_code not in range(200, 300):
        logging.error("Failed to create user presence", session_id=session_id,
                      status_code=response.status_code, response=response.json)
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    presence: dict[str, Any] = response.json["data"]
    game_mode: int = presence["game_mode"]

    # fetch user stats
    response = await users_client.get_stats(account_id, game_mode)
    if response.status_code not in range(200, 300):
        logging.error("Failed to get user stats", session_id=session_id,
                      status_code=response.status_code, response=response.json)
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    user_stats: dict[str, Any] = response.json["data"]
    # {'account_id': 1, 'game_mode': 0, 'total_score': 0, 'ranked_score': 0,
    #  'performance': 0, 'play_count': 0, 'play_time': 0, 'accuracy': 0.0,
    #  'max_combo': 0, 'total_hits': 0, 'replay_views': 0, 'xh_count': 0,
    #  'x_count': 0, 'sh_count': 0, 's_count': 0, 'a_count': 0, 'status':
    #  'active', 'created_at': '2022-09-18T12:25:04.923023+00:00',
    #  'updated_at': '2022-09-18T12:25:04.923023+00:00'}

    user_global_rank = get_global_rank(account_id)

    response_buffer += serial.write_user_presence_packet(
        account_id=account_id,
        username=login_data["username"],
        utc_offset=presence["utc_offset"],
        country_code=presence["country_code"],
        bancho_privileges=to_client_privileges(presence["privileges"]),
        mode=presence["game_mode"],
        latitude=presence["latitude"],
        longitude=presence["longitude"],
        global_rank=user_global_rank)

    response_buffer += serial.write_user_stats_packet(
        account_id=account_id,
        action=presence["action"],
        info_text=presence["info_text"],
        map_md5=presence["map_md5"],
        mods=presence["mods"],
        mode=presence["game_mode"],
        map_id=presence["map_id"],
        ranked_score=user_stats["ranked_score"],
        accuracy=user_stats["accuracy"],
        play_count=user_stats["play_count"],
        total_score=user_stats["total_score"],
        global_rank=user_global_rank,
        pp=user_stats["performance"])

    # TODO: other sessions presences & account stats
    response = await users_client.get_all_presences()
    if response.status_code not in range(200, 300):
        logging.error("Failed to get all presences",
                      status_code=response.status_code, response=response.json)
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    other_presences: list[dict[str, Any]] = response.json["data"]

    for other_presence in other_presences:
        if other_presence["session_id"] == session_id:
            continue

        if is_restricted(other_presence["privileges"]):
            continue

        response = await users_client.get_stats(other_presence["account_id"],
                                                other_presence["game_mode"])
        if response.status_code not in range(200, 300):
            logging.error("Failed to get user stats",
                          status_code=response.status_code, response=response.json)
            response = Response(content=serial.write_account_id_packet(-1),
                                headers={"cho-token": "no"},
                                status_code=200)
            return response

        other_stats: dict[str, Any] = response.json["data"]

        global_rank = get_global_rank(other_presence["account_id"])

        response_buffer += serial.write_user_presence_packet(
            account_id=other_presence["account_id"],
            username=other_presence["username"],
            utc_offset=other_presence["utc_offset"],
            country_code=other_presence["country_code"],
            bancho_privileges=to_client_privileges(
                other_presence["privileges"]),
            mode=other_presence["game_mode"],
            latitude=other_presence["latitude"],
            longitude=other_presence["longitude"],
            global_rank=global_rank)

        response_buffer += serial.write_user_stats_packet(
            account_id=other_presence["account_id"],
            action=other_presence["action"],
            info_text=other_presence["info_text"],
            map_md5=other_presence["map_md5"],
            mods=other_presence["mods"],
            mode=other_presence["game_mode"],
            map_id=other_presence["map_id"],
            ranked_score=other_stats["ranked_score"],
            accuracy=other_stats["accuracy"],
            play_count=other_stats["play_count"],
            total_score=other_stats["total_score"],
            global_rank=global_rank,
            pp=other_stats["performance"])

    response_buffer += serial.write_notification_packet(
        message="Welcome to Akatsuki v2!")

    response = Response(content=bytes(response_buffer),
                        headers={"cho-token": str(session_id)},
                        status_code=200)
    return response


@router.post("/v1/bancho")
async def bancho(request: Request,
                 session_id: UUID = Header(..., alias='osu-token'),
                 ctx: RequestContext = Depends()):
    users_client = UsersClient(ctx)

    new_session_expiry = datetime.utcnow() + timedelta(minutes=5)
    response = await users_client.partial_update_session(session_id,
                                                         expires_at=new_session_expiry)
    if response.status_code not in range(200, 300):
        # this session could not be found - probably expired
        response = Response(content=(serial.write_notification_packet("Service has restarted")
                                     + serial.write_server_restart_packet(ms=0)),
                            status_code=200)
        return response

    session: Session = response.json["data"]

    response_buffer = bytearray()

    # TODO: async for chunk in request.stream()
    with memoryview(await request.body()) as raw_data:
        data_reader = serial.Reader(raw_data)

        while not data_reader.stream_consumed:
            packet_id = data_reader.read_uint16()
            _ = data_reader.read_uint8()  # reserved byte
            packet_length = data_reader.read_uint32()

            packet_data = data_reader.read_bytes(packet_length)

            packet_response = await handle_packet_event(ctx, session,
                                                        packet_id, packet_data)
            response_buffer += packet_response

    # fetch any data from the player's packet queue
    response = await users_client.deqeue_all_data(session_id)
    if response.status_code not in range(200, 300):
        logging.error("Failed to dequeue all data", session_id=session_id,
                      status_code=response.status_code, response=response.json)
        # TODO: should we send a packet here?
        # response = Response(content=serial.write_account_id_packet(-1),
        #                     headers={"cho-token": "no"},
        #                     status_code=200)
        response = b""
        return response

    queued_packets: list[QueuedPacket] = response.json["data"]
    for packet in queued_packets:
        response_buffer.extend(packet["data"])

    response_data = bytes(response_buffer)

    logging.debug("Sending bancho response", session_id=session_id,
                  response=response_data)

    response = Response(content=response_data, status_code=200)
    return response
