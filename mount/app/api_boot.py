from __future__ import annotations

from app.api.rest import init_api
from app.common import logging
from app.common import settings
logging.init_logging(log_level=settings.LOG_LEVEL)

api = init_api()
