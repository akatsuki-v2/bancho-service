from __future__ import annotations

import time

from app.common import logging
from app.services import http_client
from fastapi import FastAPI
from fastapi import Request


def init_http_client(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_http_client() -> None:
        logging.info("Starting up HTTP client")
        service_http_client = http_client.ServiceHTTPClient()
        api.state.http_client = service_http_client
        logging.info("HTTP client started up")

    @api.on_event("shutdown")
    async def shutdown_http_client() -> None:
        logging.info("Shutting down HTTP client")
        await api.state.http_client.aclose()
        del api.state.http_client
        logging.info("HTTP client shut down")


def init_middlewares(api: FastAPI) -> None:
    # NOTE: these run bottom to top

    @api.middleware("http")
    async def add_http_client_to_request(request: Request, call_next):
        request.state.http_client = request.app.state.http_client
        response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = (time.perf_counter_ns() - start_time) / 1e6
        response.headers["X-Process-Time"] = str(process_time)  # ms
        return response


def init_routes(api: FastAPI) -> None:
    from .v1 import router as v1_router

    api.include_router(v1_router)


def init_api():
    api = FastAPI()

    init_http_client(api)
    init_middlewares(api)
    init_routes(api)

    return api
