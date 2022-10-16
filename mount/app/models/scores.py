from datetime import datetime
from typing import Literal
from typing import TypedDict

from . import Status


class Score(TypedDict):
    score_id: int
    beatmap_md5: str
    account_id: int
    mode: Literal['osu', 'taiko', 'fruits', 'mania']
    mods: int
    score: int
    performance: float
    accuracy: float
    max_combo: int
    count_50s: int
    count_100s: int
    count_300s: int
    count_gekis: int
    count_katus: int
    count_misses: int
    grade: Literal['XH', 'X', 'SH', 'S', 'A', 'B', 'C', 'D', 'F', 'N']
    passed: bool
    perfect: bool
    seconds_elapsed: int
    anticheat_flags: int
    client_checksum: str
    status: Status
    created_at: datetime
    updated_at: datetime
