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
    Log,
    LogCreate,
    LogCreatResult,
    LogSuccessResult,
    LogUpdate,
)

router = APIRouter(
    prefix="/v1/logs",
    tags=["logs"],
)

security = HTTPBearer()


@router.get(
    "",
    response_model=list[Log],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        }
    },
)
async def get_logs(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> list[Log]:
    """
    Get potty logs for dogs.
    """
    results = []
    async for doc in db.logs.find():
        results.append(
            Log(
                id=str(doc.get("_id")),
                user_id=doc.get("user_id"),
                name=doc.get("name"),
                type=doc.get("type"),
                date=doc.get("date").isoformat(),
                note=doc.get("note"),
            )
        )

    return results


@router.get(
    "/{log_id}",
    response_model=Log,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid log id format.",
            "model": GenericException,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Log not found.",
            "model": GenericException,
        },
    },
)
async def get_log(
    log_id: str,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> Log:
    """
    Get a potty log for a dog.
    """
    try:
        log_object_id = ObjectId(log_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid log id format."
        )

    doc = await db.logs.find_one({"_id": log_object_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found."
        )

    return Log(
        id=str(doc.get("_id")),
        user_id=doc.get("user_id"),
        name=doc.get("name"),
        type=doc.get("type"),
        date=doc.get("date").isoformat(),
        note=doc.get("note"),
    )


@router.post(
    "",
    response_model=LogCreatResult,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        }
    },
)
async def add_log(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
    new_log: LogCreate,
) -> LogCreatResult:
    """
    Add a potty log for a dog.
    """

    data = new_log.model_dump() | {"user_id": user_id}
    create_result = await db.logs.insert_one(data)

    return LogCreatResult(id=str(create_result.inserted_id))


@router.delete(
    "/{log_id}",
    response_model=LogSuccessResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid log id format.",
            "model": GenericException,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to delete log",
            "model": GenericException,
        },
    },
)
async def delete_log(
    log_id: str,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> LogSuccessResult:
    """
    Delete a potty log for a dog.
    """

    try:
        log_object_id = ObjectId(log_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid log id format."
        )

    delete_result = await db.logs.delete_one({"_id": log_object_id, "user_id": user_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete log.",
        )

    return LogSuccessResult(success=True)


@router.patch(
    "/{log_id}",
    response_model=LogSuccessResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid log id format, No changes provided",
            "model": GenericException,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Log not found.",
            "model": GenericException,
        },
    },
)
async def update_log(
    log_id: str,
    log_update: LogUpdate,
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_id: Annotated[None | str, Depends(validate_access)],
) -> LogSuccessResult:
    """
    Update a potty log for a dog.
    """

    try:
        log_object_id = ObjectId(log_id)
    except bson.errors.InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid log id format."
        )

    update_data = log_update.model_dump(exclude_unset=True)
    update_result = await db.logs.update_one(
        {"_id": log_object_id, "user_id": user_id}, {"$set": update_data}
    )

    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Log not found."
        )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No changes provided",
        )

    return LogSuccessResult(success=True)