import pytest
from httpx import AsyncClient

from app.settings import settings

pytestmark = pytest.mark.asyncio
AUTH_HEADER = {"Authorization": f"Bearer {settings.static_token}"}


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

    # Valid Create
    r = await test_client.post(
        "/v1/logs",
        json={"name": "string", "type": "string", "date": "2024-10-30T13:52:23.666Z"},
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    results = r.json()
    assert results.get("id")


async def test_get_logs(test_client: AsyncClient) -> None:
    """
    Test Fetching logs
    """
    # Get all Logs
    r = await test_client.get("/v1/logs", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Get single logs
    log_id = results[0].get("id")
    r = await test_client.get(f"/v1/logs/{log_id}", headers=AUTH_HEADER)

    assert r.status_code == 200

    # Unknown Log ID
    r = await test_client.get("/v1/logs/652d729bb8da04810695a943", headers=AUTH_HEADER)
    assert r.status_code == 404

    # Invalid Log ID format
    r = await test_client.get("/v1/logs/invalid", headers=AUTH_HEADER)
    assert r.status_code == 400


async def test_update_logs(test_client: AsyncClient) -> None:
    """
    Test updating a logs
    """
    # Get all Logs
    r = await test_client.get("/v1/logs", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Update a Log
    log_id = results[0].get("id")
    r = await test_client.patch(
        f"/v1/logs/{log_id}",
        json={
            "name": "string",
            "type": "string",
            "date": "2024-10-30T14:36:26.315Z",
            "note": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Updated log with same value
    log_id = results[0].get("id")
    r = await test_client.patch(
        f"/v1/logs/{log_id}",
        json={
            "name": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 400

    # Unknown Log ID
    r = await test_client.patch(
        "/v1/logs/652d729bb8da04810695a943",
        json={
            "name": "string",
            "type": "string",
            "date": "2024-10-30T14:36:26.315Z",
            "note": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404

    # Invalid Log ID
    r = await test_client.patch(
        "/v1/logs/652d729bb8",
        json={
            "name": "string",
            "type": "string",
            "date": "2024-10-30T14:36:26.315Z",
            "note": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 400


async def test_delete_log(test_client: AsyncClient) -> None:
    """
    Test deleting a logs
    """
    # Get all Logs
    r = await test_client.get("/v1/logs", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Delete a Log
    log_id = results[0].get("id")
    r = await test_client.delete(
        f"/v1/logs/{log_id}",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Unknown Log ID
    r = await test_client.delete(
        "/v1/logs/652d729bb8da04810695a943",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404

    # Invalid Log ID
    r = await test_client.delete(
        "/v1/logs/652d729bb8da0",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 400
