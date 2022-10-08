from enum import IntEnum
from typing import TypedDict
from uuid import UUID


class Action(IntEnum):
    IDLE = 0
    AFK = 1
    PLAYING = 2
    EDITING = 3
    MODDING = 4
    MULTIPLAYER = 5
    WATCHING = 6
    UNKNOWN = 7
    TESTING = 8
    SUBMITTING = 9
    PAUSED = 10
    LOBBY = 11
    MULTIPLAYING = 12
    OSU_DIRECT = 13


class Presence(TypedDict):
    session_id: UUID
    game_mode: int
    country_code: str
    privileges: int
    latitude: float
    longitude: float
    action: Action
    info_text: str
    map_md5: str
    map_id: int
    mods: int

    osu_version: str
    utc_offset: int
    display_city: bool
    pm_private: bool
