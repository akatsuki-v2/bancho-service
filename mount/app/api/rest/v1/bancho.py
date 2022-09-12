from __future__ import annotations

from typing import TypedDict

from app.api.rest.context import RequestContext
from app.api.rest.gateway import forward_request
from app.common import serial
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

    response = await forward_request(ctx,
                                     method="POST",
                                     url="http://users-service/v1/sessions",
                                     json={"username": login_data["username"],
                                           "password": login_data["password_md5"],
                                           "user_agent": "osu!"})

    if response.status_code != 200:
        response = Response(content=serial.write_account_id_packet(-1),
                            headers={"cho-token": "no"},
                            status_code=200)
        return response

    # log in response format
    # {'status': 'success',
    #  'data': {'session_id': '3357e71b-6507-46c4-9251-441e58b741c4',
    #           'account_id': 1,
    #           'user_agent': 'osu!',
    #           'expires_at': '2022-09-12T01:14:48.897433',
    #           'created_at': '2022-09-12T00:14:48.897433',
    #           'updated_at': '2022-09-12T00:14:48.897433'}}

    session_id: str = response.json["data"]["session_id"]
    account_id: int = response.json["data"]["account_id"]

    # TODO: endpoint to submit osu!-specific login data
    # (osu_version, utc_offset, display_city, pm_private, etc.)

    # TODO: endpoint to submit client hashes
    # (osu_path_md5, adapters_str, adapters_md5, uninstall_md5, disk_signature_md5)

    response_buffer = bytearray()
    response_buffer += serial.write_protocol_version_packet(19)
    response_buffer += serial.write_account_id_packet(account_id)
    response_buffer += serial.write_privileges_packet(0)  # TODO

    # TODO: realify
    response_buffer += serial.write_channel_info_packet(channel="#osu",
                                                        topic="yay",
                                                        player_count=1)

    response_buffer += serial.write_channel_info_end_packet()

    # TODO: why doesn't this work?
    response_buffer += serial.write_main_menu_icon_packet(
        icon_url="https://akatsuki.pw/static/images/logos/logo.png",
        onclick_url="https://akatsuki.pw",
    )
    response_buffer += serial.write_friends_list_packet([])  # TODO

    # TODO: realize
    response_buffer += serial.write_user_presence_packet(
        account_id,
        username=login_data["username"],
        utc_offset=login_data["utc_offset"],
        country_code=38,  # canada?
        bancho_privileges=32,
        mode=0,
        latitude=43.0,
        longitude=-79.0,
        global_rank=32)
    response_buffer += serial.write_user_stats_packet(
        account_id,
        action=3,  # TODO: enum
        info_text="yay",
        map_md5="",
        mods=0,
        mode=0,
        map_id=0,
        ranked_score=12345,
        accuracy=0.67,
        plays=123,
        total_score=65423,
        global_rank=32,
        pp=6969)

    # TODO: other sessions presences & account stats

    response = Response(content=bytes(response_buffer),
                        headers={"cho-token": session_id},
                        status_code=200)
    return response


@router.post("/v1/bancho")
async def bancho(request: Request):
    return b""
