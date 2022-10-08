from datetime import datetime
from typing import TypedDict
from uuid import UUID


class LoginData(TypedDict):
    username: str
    password_md5: str
    osu_version: str
    utc_offset: int
    display_city: bool
    pm_private: bool
    osu_path_md5: str
    adapters_str: str
    adapters_md5: str
    uninstall_md5: str
    disk_signature_md5: str


class Session(TypedDict):
    session_id: UUID
    account_id: int
    user_agent: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
