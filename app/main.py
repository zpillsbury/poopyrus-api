import time
from typing import Any, Callable, TypeVar

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    HTTPBearer,
)

from app.routers.logs import logs

from .utilities.log import logger

security = HTTPBearer()
F = TypeVar("F", bound=Callable[..., Any])


app = FastAPI(
    title="💩 Poopyrus",
    description="We don't take shit.. we track it.",
    version="1.0.0",
    docs_url="/",
)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://poo.homy.homes",
        "https://zpillsbury.github.io/poopyrus",
    ],
)


@app.middleware("http")
async def process_time_log_middleware(request: Request, call_next: F) -> Response:
    """
    Add API process time in response headers and log calls
    """
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = str(round(time.time() - start_time, 3))
    response.headers["X-Process-Time"] = process_time

    logger.info(
        "Method=%s Path=%s StatusCode=%s ProcessTime=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response


app.include_router(logs.router)
