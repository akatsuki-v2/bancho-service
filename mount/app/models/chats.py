from datetime import datetime

from app.models import BaseModel
from app.models import Status


class Chat(BaseModel):
    chat_id: int
    name: str
    topic: str
    read_privileges: int
    write_privileges: int
    auto_join: bool
    instance: bool

    status: Status
    updated_at: datetime
    created_at: datetime
    created_by: int
