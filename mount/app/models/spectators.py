from datetime import datetime
from typing import TypedDict
from uuid import UUID


class Spectator(TypedDict):
    session_id: UUID
    account_id: int
    created_at: datetime
