import time

from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint


async def add_process_time_header_to_response(request: Request,
                                              call_next: RequestResponseEndpoint):
    start_time = time.perf_counter_ns()
    response = await call_next(request)
    process_time = (time.perf_counter_ns() - start_time) / 1e6
    response.headers["X-Process-Time"] = str(process_time)  # ms
    return response


async def add_http_client_to_request(request: Request,
                                     call_next: RequestResponseEndpoint):
    request.state.http_client = request.app.state.http_client
    response = await call_next(request)
    return response
