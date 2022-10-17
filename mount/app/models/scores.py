from datetime import datetime
from typing import Literal

from app.models import BaseModel
from app.models import Status


class Score(BaseModel):
    score_id: int
    beatmap_md5: str
    account_id: int
    username: str
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
