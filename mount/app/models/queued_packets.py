from datetime import datetime
from typing import TypedDict


class QueuedPacket(TypedDict):
    data: list[int]
    created_at: datetime
