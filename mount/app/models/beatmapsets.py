from datetime import datetime
from typing import Any

from app.models import BaseModel
from app.models import RankedStatus
from app.models import Status


class Beatmapset(BaseModel):
    beatmapset_id: int
    artist: str
    artist_unicode: str
    covers: dict[str, Any]
    creator: str
    favourite_count: int
    nsfw: bool
    osu_play_count: int
    preview_url: str
    source: str
    title: str
    title_unicode: str
    mapper_id: int  # account id
    mapper_name: str
    video: bool
    download_disabled: bool
    availability_information: str | None
    bpm: float
    can_be_hyped: bool
    discussion_locked: bool
    current_hype: int
    required_hype: int
    is_scoreable: bool
    osu_updated_at: datetime
    legacy_thread_url: str
    current_nominations: int
    required_nominations: int
    ranked_status: RankedStatus
    osu_ranked_at: datetime | None
    storyboard: bool
    osu_submitted_at: datetime
    tags: str
    status: Status
    created_at: datetime
    updated_at: datetime
