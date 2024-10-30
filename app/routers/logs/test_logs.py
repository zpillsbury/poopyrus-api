import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio
AUTH_HEADER = {"Authorization": "Bearer GOOD_TOKEN"}


async def test_create_log(test_client: AsyncClient) -> None:
    """
    Test Creating a log
    """
    # No Bearer Token
    r = await test_client.post(
        "/v1/logs",
        json={"name": "string", "type": "string", "date": "2024-10-30T13:52:23.666Z"},
    )
    assert r.status_code == 403

    # Invalid Bearer Token
    r = await test_client.post(
        "/v1/logs",
        json={"name": "string", "type": "string", "date": "2024-10-30T13:52:23.666Z"},
        headers={"Authorization": "Bearer BAD_TOKEN"},
    )
    assert r.status_code == 401
