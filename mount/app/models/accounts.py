from datetime import datetime
from typing import TypedDict

from . import Status


class Account(TypedDict):
    account_id: int
    username: str
    safe_username: str  # NOTE: generated column
    email_address: str
    country: str

    status: Status
    created_at: datetime
    updated_at: datetime
