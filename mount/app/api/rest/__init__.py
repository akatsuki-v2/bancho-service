from __future__ import annotations

from app.api.rest import middlewares
from app.services import http_client
from fastapi import FastAPI
from shared_modules import logger
from starlette.middleware.base import BaseHTTPMiddleware


def init_http_client(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_http_client() -> None:
        logger.info("Starting up HTTP client")
        service_http_client = http_client.ServiceHTTPClient()
        api.state.http_client = service_http_client
        logger.info("HTTP client started up")

    @api.on_event("shutdown")
    async def shutdown_http_client() -> None:
        logger.info("Shutting down HTTP client")
        await api.state.http_client.aclose()
        del api.state.http_client
        logger.info("HTTP client shut down")


def init_middlewares(api: FastAPI) -> None:
    middleware_stack = [
        middlewares.add_process_time_header_to_response,
        middlewares.add_http_client_to_request,
        middlewares.set_request_id_context,
    ]

    # NOTE: starlette reverses the order of the middleware stack
    # more info: https://github.com/encode/starlette/issues/479
    for middleware in reversed(middleware_stack):
        api.add_middleware(BaseHTTPMiddleware, dispatch=middleware)


def init_routes(api: FastAPI) -> None:
    from .v1 import router as v1_router

    api.include_router(v1_router)


def init_api():
    api = FastAPI()

    init_http_client(api)
    init_middlewares(api)
    init_routes(api)

    return api
