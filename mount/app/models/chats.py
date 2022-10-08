from datetime import datetime
from typing import TypedDict

from app.models import Status


class Chat(TypedDict):
    chat_id: int
    name: str
    topic: str
    read_privileges: int
    write_privileges: int
    auto_join: bool

    status: Status
    updated_at: datetime
    created_at: datetime
    created_by: int
