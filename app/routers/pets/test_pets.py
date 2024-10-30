import pytest
from httpx import AsyncClient

from app.settings import settings

pytestmark = pytest.mark.asyncio
AUTH_HEADER = {"Authorization": f"Bearer {settings.static_token}"}


async def test_create_pet(test_client: AsyncClient) -> None:
    """
    Test Creating a pet
    """
    # No Bearer Token
    r = await test_client.post(
        "/v1/pets",
        json={"name": "string", "type": "string"},
    )
    assert r.status_code == 403

    # Invalid Bearer Token
    r = await test_client.post(
        "/v1/pets",
        json={"name": "string", "type": "string"},
        headers={"Authorization": "Bearer BAD_TOKEN"},
    )
    assert r.status_code == 401

    # Valid Create
    r = await test_client.post(
        "/v1/pets",
        json={"name": "string", "type": "string"},
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    results = r.json()
    assert results.get("id")


async def test_get_pets(test_client: AsyncClient) -> None:
    """
    Test Fetching pets
    """
    # Get all Pets
    r = await test_client.get("/v1/pets", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Get single pets
    pet_id = results[0].get("id")
    r = await test_client.get(f"/v1/pets/{pet_id}", headers=AUTH_HEADER)

    assert r.status_code == 200

    # Unknown Pet ID
    r = await test_client.get("/v1/pets/652d729bb8da04810695a943", headers=AUTH_HEADER)
    assert r.status_code == 404

    # Invalid Pet ID format
    r = await test_client.get("/v1/pets/invalid", headers=AUTH_HEADER)
    assert r.status_code == 400


async def test_update_pets(test_client: AsyncClient) -> None:
    """
    Test updating a pets
    """
    # Get all Pets
    r = await test_client.get("/v1/pets", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Update a Pet
    pet_id = results[0].get("id")
    r = await test_client.patch(
        f"/v1/pets/{pet_id}",
        json={
            "name": "string",
            "type": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Unknown Pet ID
    r = await test_client.patch(
        "/v1/pets/652d729bb8da04810695a943",
        json={
            "name": "string",
            "type": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404

    # Invalid Pet ID
    r = await test_client.patch(
        "/v1/pets/652d729bb8",
        json={
            "name": "string",
            "type": "string",
        },
        headers=AUTH_HEADER,
    )
    assert r.status_code == 400


async def test_delete_pet(test_client: AsyncClient) -> None:
    """
    Test deleting a pets
    """
    # Get all Pets
    r = await test_client.get("/v1/pets", headers=AUTH_HEADER)
    assert r.status_code == 200
    results = r.json()
    assert results

    # Delete a Pet
    pet_id = results[0].get("id")
    r = await test_client.delete(
        f"/v1/pets/{pet_id}",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 200

    # Unknown Pet ID
    r = await test_client.delete(
        "/v1/pets/652d729bb8da04810695a943",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 404

    # Invalid Pet ID
    r = await test_client.delete(
        "/v1/pets/652d729bb8da0",
        headers=AUTH_HEADER,
    )
    assert r.status_code == 400
