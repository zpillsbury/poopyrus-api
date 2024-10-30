import asyncio
from typing import Any, Generator

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    """
    Override Event Loop
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()


@pytest.fixture()
def test_client() -> AsyncClient:
    """
    Create an instance of the client
    """
    return AsyncClient(app=app, base_url="http://test", follow_redirects=True)
