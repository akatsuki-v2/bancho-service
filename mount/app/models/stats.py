from datetime import datetime
from typing import TypedDict

from . import Status


class Stats(TypedDict):
    account_id: int
    game_mode: int
    total_score: int
    ranked_score: int
    performance: int
    play_count: int
    play_time: int
    accuracy: float
    max_combo: int
    total_hits: int
    replay_views: int
    xh_count: int
    x_count: int
    sh_count: int
    s_count: int
    a_count: int

    status: Status
    created_at: datetime
    updated_at: datetime
