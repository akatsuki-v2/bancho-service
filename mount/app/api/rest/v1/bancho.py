from __future__ import annotations

from typing import Any
from typing import TypedDict

from app.api.rest.context import RequestContext
from app.common import logging
from app.common import serial
from app.services.users_client import UsersClient
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi import Response
router = APIRouter()


class LoginData(TypedDict):
    username: str
    password_md5: str
    osu_version: str
    utc_offset: int
    display_city: bool
    pm_private: bool
    osu_path_md5: str
    adapters_str: str
    adapters_md5: str
    uninstall_md5: str
    disk_signature_md5: str


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

    # create user session
    response = await users_client.log_in(login_data["username"],
                                         login_data["password_md5"],
                                         user_agent="osu!")
    if response.status_code != 200:
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    session_id: str = response.json["data"]["session_id"]
    account_id: int = response.json["data"]["account_id"]

    # TODO: endpoint to submit client hashes
    # (osu_path_md5, adapters_str, adapters_md5, uninstall_md5, disk_signature_md5)

    response_buffer = bytearray()
    response_buffer += serial.write_protocol_version_packet(19)
    response_buffer += serial.write_account_id_packet(account_id)
    response_buffer += serial.write_privileges_packet(0)  # TODO

    # TODO: fetch from chat-service
    channels = [
        {"name": "#announce", "topic": "Announcements", "user_count": 1},
        {"name": "#osu", "topic": "osu! general discussion", "user_count": 1},
        {"name": "#lobby", "topic": "The waiting room", "user_count": 1},
    ]

    for channel in channels:
        response_buffer += serial.write_channel_info_packet(
            channel=channel["name"],
            topic=channel["topic"],
            user_count=channel["user_count"],
        )

    response_buffer += serial.write_channel_info_end_packet()

    # TODO: unhardcode
    response_buffer += serial.write_main_menu_icon_packet(
        icon_url="https://akatsuki.pw/static/images/logos/logo.png",
        onclick_url="https://akatsuki.pw",
    )
    response_buffer += serial.write_friends_list_packet([])  # TODO

    # TODO: geolocation lookup by ip

    def is_restricted(privileges: int) -> bool:  # TODO
        return False

    def to_client_privileges(server_privileges: int) -> int:  # TODO
        return server_privileges

    def get_global_rank(account_id: int) -> int:  # TODO
        return 0

    # create user presence
    response = await users_client.create_presence(
        session_id,
        game_mode=0,
        account_id=account_id,
        username=login_data["username"],
        country_code=38,
        privileges=0,
        latitude=0.0,
        longitude=0.0,
        action=0,
        info_text="",
        map_md5="",
        map_id=0,
        mods=0,
        osu_version=login_data["osu_version"],
        utc_offset=login_data["utc_offset"],
        display_city=login_data["display_city"],
        pm_private=login_data["pm_private"])

    if response.status_code != 200:
        logging.error("Failed to create user presence", session_id=session_id,
                      status_code=response.status_code, response=response.json)
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    user_presence: dict[str, Any] = response.json["data"]
    game_mode: int = user_presence["game_mode"]

    # fetch user stats
    response = await users_client.get_stats(account_id, game_mode)
    if response.status_code != 200:
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

    # TODO: not exactly sure how we should handle this?
    # should we have a `ranking-service` that handles ranking?
    user_global_rank = get_global_rank(account_id)

    response_buffer += serial.write_user_presence_packet(
        account_id=account_id,
        username=user_presence["username"],
        utc_offset=user_presence["utc_offset"],
        country_code=user_presence["country_code"],
        bancho_privileges=to_client_privileges(user_presence["privileges"]),
        mode=user_presence["game_mode"],
        latitude=user_presence["latitude"],
        longitude=user_presence["longitude"],
        global_rank=user_global_rank)

    response_buffer += serial.write_user_stats_packet(
        account_id=account_id,
        action=user_presence["action"],
        info_text=user_presence["info_text"],
        map_md5=user_presence["map_md5"],
        mods=user_presence["mods"],
        mode=user_presence["game_mode"],
        map_id=user_presence["map_id"],
        ranked_score=user_stats["ranked_score"],
        accuracy=user_stats["accuracy"],
        play_count=user_stats["play_count"],
        total_score=user_stats["total_score"],
        global_rank=user_global_rank,
        pp=user_stats["performance"])

    # TODO: other sessions presences & account stats
    response = await users_client.get_all_presences()
    if response.status_code != 200:
        logging.error("Failed to get all presences",
                      status_code=response.status_code, response=response.json)
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    other_presences: list[dict[str, Any]] = response.json["data"]

    for other_presence in other_presences:
        if not is_restricted(other_presence["privileges"]):
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

    response = Response(content=bytes(response_buffer),
                        headers={"cho-token": session_id},
                        status_code=200)
    return response


@router.post("/v1/bancho")
async def bancho(request: Request):
    return b""
