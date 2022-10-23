from __future__ import annotations

from app.api.rest import init_api
from app.common import logging
from app.common import settings

logging.configure_logging(app_env=settings.APP_ENV,
                          log_level=settings.LOG_LEVEL)

api = init_api()
