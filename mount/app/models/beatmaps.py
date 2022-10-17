from datetime import datetime
from typing import Literal

from . import BaseModel
from . import RankedStatus
from . import Status


class Beatmap(BaseModel):
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
