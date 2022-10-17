from datetime import datetime
from uuid import UUID

from . import BaseModel


class Member(BaseModel):
    session_id: UUID
    account_id: int
    chat_id: int
    username: str
    privileges: int

    joined_at: datetime
