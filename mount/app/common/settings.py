from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# asgi + app
APP_ENV = os.environ["APP_ENV"]
APP_COMPONENT = os.environ["APP_COMPONENT"]
APP_HOST = os.environ["APP_HOST"]
APP_PORT = int(os.environ["APP_PORT"])
LOG_LEVEL = int(os.environ["LOG_LEVEL"])

# database
READ_DB_DRIVER = os.environ["READ_DB_DRIVER"]
READ_DB_USER = os.environ["READ_DB_USER"]
READ_DB_PASS = os.environ["READ_DB_PASS"]
READ_DB_HOST = os.environ["READ_DB_HOST"]
READ_DB_PORT = int(os.environ["READ_DB_PORT"])
READ_DB_NAME = os.environ["READ_DB_NAME"]

WRITE_DB_DRIVER = os.environ["WRITE_DB_DRIVER"]
WRITE_DB_USER = os.environ["WRITE_DB_USER"]
WRITE_DB_PASS = os.environ["WRITE_DB_PASS"]
WRITE_DB_HOST = os.environ["WRITE_DB_HOST"]
WRITE_DB_PORT = int(os.environ["WRITE_DB_PORT"])
WRITE_DB_NAME = os.environ["WRITE_DB_NAME"]

MIN_DB_POOL_SIZE = int(os.environ["MIN_DB_POOL_SIZE"])
MAX_DB_POOL_SIZE = int(os.environ["MAX_DB_POOL_SIZE"])
DB_USE_SSL = os.environ["DB_USE_SSL"].lower() == "true"

# redis
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])

# rabbitmq
AMQP_HOST = os.environ["AMQP_HOST"]
AMQP_PORT = int(os.environ["AMQP_PORT"])
AMQP_USER = os.environ["AMQP_USER"]
AMQP_PASS = os.environ["AMQP_PASS"]