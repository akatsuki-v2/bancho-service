from datetime import datetime

from . import BaseModel


class QueuedPacket(BaseModel):
    data: list[int]
    created_at: datetime
