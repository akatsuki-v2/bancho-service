from __future__ import annotations

import time
from datetime import datetime
from datetime import timedelta
from typing import Any
from uuid import UUID

from app.api.rest.context import RequestContext
from app.common import logging
from app.common import serial
from app.events.packets import handle_packet_event
from app.models.presences import Presence
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

OSU_STABLE_PROTOCOL_VERSION = 19


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
    start_time = time.time()

    login_data = parse_login_data(await request.body())

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # make sure this user isn't already logged in
    presences = await users_client.get_all_presences(username=login_data["username"])
    if presences is None:
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    # TODO: allow this if the existing session has been active for a while,
    # as a way to prevent ghosting sessions from being left open forever
    if len(presences) > 0:
        response = Response(content=(serial.write_notification_packet("Your account is already logged in.")
                                     + serial.write_account_id_packet(-1)),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    # create user session
    session = await users_client.log_in(login_data["username"],
                                        login_data["password_md5"],
                                        user_agent="osu!")
    if session is None:
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    session_id = session.session_id
    account_id = session.account_id

    # TODO: privileges
    privileges = 2_147_483_647
    def is_restricted(server_privs: int): return False
    def to_client_privileges(server_privs: int): return server_privs & 0xff

    # TODO: endpoint to submit client hashes
    # (osu_path_md5, adapters_str, adapters_md5, uninstall_md5, disk_signature_md5)

    response_buffer = bytearray()
    response_buffer += serial.write_protocol_version_packet(
        version=OSU_STABLE_PROTOCOL_VERSION)
    response_buffer += serial.write_account_id_packet(account_id)
    response_buffer += serial.write_privileges_packet(privileges)

    chats = await chats_client.get_chats()
    if chats is None:
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    for chat in chats:
        if chat.name == "#lobby":
            continue

        members = await chats_client.get_members(chat.chat_id)
        if members is None:
            return Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)

        response_buffer += serial.write_channel_info_packet(
            channel=chat.name,
            topic=chat.topic,
            user_count=len(members),
        )

        # TODO: enqueue to other players that we've joined

    response_buffer += serial.write_channel_info_end_packet()

    # TODO: unhardcode these into an sql table
    # response_buffer += serial.write_main_menu_icon_packet(
    #     icon_url="https://akatsuki.pw/static/images/logos/logo.png",
    #     onclick_url="https://akatsuki.pw",
    # )

    friends = []  # TODO: friends
    silence_end = 0  # TODO: silences

    response_buffer += serial.write_friends_list_packet(friends)
    response_buffer += serial.write_silence_end_packet(silence_end)

    # TODO: geolocation
    country_code = 38
    latitude = 48.23
    longitude = 16.37

    # TODO: global player rankings

    def get_global_rank(account_id: int) -> int:
        return 0

    # create user presence
    presence = await users_client.create_presence(
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
    if presence is None:
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    game_mode: int = presence.game_mode

    # fetch user stats
    stats = await users_client.get_stats(account_id, game_mode)
    if stats is None:
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    # {'account_id': 1, 'game_mode': 0, 'total_score': 0, 'ranked_score': 0,
    #  'performance': 0, 'play_count': 0, 'play_time': 0, 'accuracy': 0.0,
    #  'max_combo': 0, 'total_hits': 0, 'replay_views': 0, 'xh_count': 0,
    #  'x_count': 0, 'sh_count': 0, 's_count': 0, 'a_count': 0, 'status':
    #  'active', 'created_at': '2022-09-18T12:25:04.923023+00:00',
    #  'updated_at': '2022-09-18T12:25:04.923023+00:00'}

    user_global_rank = get_global_rank(account_id)

    user_presence_data = serial.write_user_presence_packet(
        account_id=account_id,
        username=login_data["username"],
        utc_offset=presence.utc_offset,
        country_code=presence.country_code,
        bancho_privileges=to_client_privileges(presence.privileges),
        mode=presence.game_mode,
        latitude=presence.latitude,
        longitude=presence.longitude,
        global_rank=user_global_rank)

    user_stats_data = serial.write_user_stats_packet(
        account_id=account_id,
        action=presence.action,
        info_text=presence.info_text,
        map_md5=presence.map_md5,
        mods=presence.mods,
        mode=presence.game_mode,
        map_id=presence.map_id,
        ranked_score=stats.ranked_score,
        accuracy=stats.accuracy,
        play_count=stats.play_count,
        total_score=stats.total_score,
        global_rank=user_global_rank,
        pp=stats.performance)

    response_buffer += user_presence_data
    response_buffer += user_stats_data

    # TODO: other sessions presences & account stats
    other_presences = await users_client.get_all_presences()
    if other_presences is None:
        return Response(content=serial.write_account_id_packet(-1),
                        headers={"cho-token": "no"},
                        status_code=200)

    for other_presence in other_presences:
        if other_presence.session_id == session_id:
            continue

        if is_restricted(other_presence.privileges):
            continue

        other_stats = await users_client.get_stats(other_presence.account_id,
                                                   other_presence.game_mode)
        if other_stats is None:
            return Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)

        global_rank = get_global_rank(other_presence.account_id)

        # send them to us
        response_buffer += serial.write_user_presence_packet(
            account_id=other_presence.account_id,
            username=other_presence.username,
            utc_offset=other_presence.utc_offset,
            country_code=other_presence.country_code,
            bancho_privileges=to_client_privileges(
                other_presence.privileges),
            mode=other_presence.game_mode,
            latitude=other_presence.latitude,
            longitude=other_presence.longitude,
            global_rank=global_rank)

        response_buffer += serial.write_user_stats_packet(
            account_id=other_presence.account_id,
            action=other_presence.action,
            info_text=other_presence.info_text,
            map_md5=other_presence.map_md5,
            mods=other_presence.mods,
            mode=other_presence.game_mode,
            map_id=other_presence.map_id,
            ranked_score=other_stats.ranked_score,
            accuracy=other_stats.accuracy,
            play_count=other_stats.play_count,
            total_score=other_stats.total_score,
            global_rank=global_rank,
            pp=other_stats.performance)

        # send us to them
        success = await users_client.enqueue_packet(other_presence.session_id,
                                                    data=list(user_presence_data + user_stats_data))
        if not success:
            response = Response(content=serial.write_account_id_packet(-1),
                                headers={"cho-token": "no"},
                                status_code=200)
            return response

    response_buffer += serial.write_notification_packet(
        message="Welcome to Akatsuki v2!")

    end_time = time.time()
    response_buffer += serial.write_notification_packet(
        f"Login took {(end_time - start_time) * 1000:.2f}ms")

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

    session = await users_client.partial_update_session(session_id,
                                                        expires_at=new_session_expiry)
    if session is None:
        # this session could not be found - probably expired
        response = Response(content=(serial.write_notification_packet("Service has restarted")
                                     + serial.write_server_restart_packet(ms=0)),
                            status_code=200)
        return response

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
    queued_packets = await users_client.deqeue_all_packets(session_id)
    if queued_packets is None:
        # TODO: should we send a packet here?
        # response = Response(content=serial.write_account_id_packet(-1),
        #                     headers={"cho-token": "no"},
        #                     status_code=200)
        response = b""
        return response

    for packet in queued_packets:
        response_buffer.extend(packet.data)

    response_data = bytes(response_buffer)

    logging.debug("Sending bancho response", session_id=session_id,
                  response=response_data)

    response = Response(content=response_data, status_code=200)
    return response
