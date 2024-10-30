from datetime import datetime, timezone
from typing import Annotated

import bson
from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.auth import validate_access
from app.models import GenericException
from app.utilities.clients import db

from .models import (
    Pet,
    PetCreate,
    PetCreatResult,
    PetSuccessResult,
    PetUpdate,
)

router = APIRouter(
    prefix="/v1/pets",
    tags=["pets"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        }
    },
)

security = HTTPBearer()


@router.get("", response_model=list[Pet])
async def get_pets(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> list[Pet]:
    """
    Get pets data.
    """
    results = []
    async for doc in db.pets.find():

        updated_at = doc.get("updated_at")
    if updated_at:
        updated_at = updated_at.isoformat()

        results.append(
            Pet(
                id=str(doc.get("_id")),
                user_id=doc.get("user_id"),
                name=doc.get("name"),
                type=doc.get("type"),
                updated_at=updated_at,
                created_at=doc.get("created_at").isoformat(),
            )
        )

    return results


@router.get(
    "/{pet_id}",
    response_model=Pet,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid pet id format.",
            "model": GenericException,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Pet not found.",
            "model": GenericException,
        },
    },
)
async def get_pet(
    pet_id: str,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> Pet:
    """
    Get one pets data
    """
    try:
        pet_object_id = ObjectId(pet_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pet id format."
        )

    doc = await db.pets.find_one({"_id": pet_object_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found."
        )

    updated_at = doc.get("updated_at")
    if updated_at:
        updated_at = updated_at.isoformat()

    return Pet(
        id=str(doc.get("_id")),
        user_id=doc.get("user_id"),
        name=doc.get("name"),
        type=doc.get("type"),
        updated_at=updated_at,
        created_at=doc.get("created_at").isoformat(),
    )


@router.post(
    "",
    response_model=PetCreatResult,
)
async def add_pet(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
    new_pet: PetCreate,
) -> PetCreatResult:
    """
    Add a pet.
    """

    data = (
        new_pet.model_dump()
        | {"user_id": user_id}
        | {"created_at": datetime.now(timezone.utc)}
    )
    create_result = await db.pets.insert_one(data)

    return PetCreatResult(id=str(create_result.inserted_id))


@router.delete(
    "/{pet_id}",
    response_model=PetSuccessResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid pet id format.",
            "model": GenericException,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to delete pet",
            "model": GenericException,
        },
    },
)
async def delete_pet(
    pet_id: str,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> PetSuccessResult:
    """
    Delete a pet.
    """

    try:
        pet_object_id = ObjectId(pet_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pet id format."
        )

    delete_result = await db.pets.delete_one({"_id": pet_object_id, "user_id": user_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pet.",
        )

    return PetSuccessResult(success=True)


@router.patch(
    "/{pet_id}",
    response_model=PetSuccessResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid pet id format, No changes provided",
            "model": GenericException,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Pet not found.",
            "model": GenericException,
        },
    },
)
async def update_pet(
    pet_id: str,
    pet_update: PetUpdate,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> PetSuccessResult:
    """
    Update a pets data.
    """

    try:
        pet_object_id = ObjectId(pet_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pet id format."
        )

    update_data = pet_update.model_dump(exclude_unset=True) | {
        "updated_at": datetime.now(timezone.utc)
    }
    update_result = await db.pets.update_one(
        {"_id": pet_object_id, "user_id": user_id}, {"$set": update_data}
    )

    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found."
        )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No changes provided",
        )

    return PetSuccessResult(success=True)
