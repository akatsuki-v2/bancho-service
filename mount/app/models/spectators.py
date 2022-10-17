from datetime import datetime
from uuid import UUID

from . import BaseModel


class Spectator(BaseModel):
    session_id: UUID
    account_id: int
    created_at: datetime
