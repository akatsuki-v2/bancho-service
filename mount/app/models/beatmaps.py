from datetime import datetime
from enum import IntEnum
from typing import Literal
from typing import TypedDict

from . import Status


class RankedStatus(IntEnum):
    GRAVEYARD = -2
    WORK_IN_PROGRESS = -1
    PENDING = 0
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4


class Beatmap(TypedDict):
    beatmap_id: int
    md5_hash: str
    set_id: int
    convert: bool
    mode: Literal['osu', 'taiko', 'fruits', 'mania']
    od: float
    ar: float
    cs: float
    hp: float
    bpm: float
    hit_length: int
    total_length: int
    count_circles: int
    count_sliders: int
    count_spinners: int
    difficulty_rating: float
    is_scoreable: bool
    pass_count: int
    play_count: int
    version: str
    created_by: int
    ranked_status: RankedStatus
    status: Status
    created_at: datetime
    updated_at: datetime
