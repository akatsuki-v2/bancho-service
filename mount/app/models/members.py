from datetime import datetime
from typing import TypedDict
from uuid import UUID


class Member(TypedDict):
    session_id: UUID
    account_id: int
    chat_id: int
    username: str
    privileges: int

    joined_at: datetime
