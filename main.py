from datetime import datetime
from typing import Annotated, Any, Optional

import bson
from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

security = HTTPBearer()


class Settings(BaseSettings):
    mongo_uri: str
    static_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

app = FastAPI(
    title="💩 Poopyrus",
    description="We don't take shit.. we track it.",
    version="1.0.0",
    docs_url="/",
)
db: AsyncIOMotorDatabase[Any] = AsyncIOMotorClient(
    settings.mongo_uri, tlsAllowInvalidCertificates=True
)["poopyrus"]

from fastapi.middleware.cors import CORSMiddleware

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


class GenericException(BaseModel):
    detail: str


class Log(BaseModel):
    id: str
    name: str
    type: str
    date: str


class LogCreate(BaseModel):
    name: str
    type: str
    date: datetime


class LogUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    date: Optional[datetime] = None


class LogCreatResult(BaseModel):
    id: str


class LogSuccessResult(BaseModel):
    success: bool


async def validate_access(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> None:
    """
    Validates access tokens.

    Raises a 401 HTTPException if an invalid token is provided.
    """
    if access_token.credentials != settings.static_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )


@app.get(
    "/logs",
    tags=["logs"],
    response_model=list[Log],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": GenericException,
        }
    },
)
async def get_logs(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_check: Annotated[None, Depends(validate_access)],
) -> list[Log]:
    """
    Get potty logs for dogs.
    """
    results = []
    async for doc in db.logs.find():
        results.append(
            Log(
                id=str(doc.get("_id")),
                name=doc.get("name"),
                type=doc.get("type"),
                date=doc.get("date").isoformat(),
            )
        )

    return results


@app.get(
    "/logs/{log_id}",
    tags=["logs"],
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
    token_check: Annotated[None, Depends(validate_access)],
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
        name=doc.get("name"),
        type=doc.get("type"),
        date=doc.get("date").isoformat(),
    )


@app.post(
    "/logs",
    tags=["logs"],
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
    token_check: Annotated[None, Depends(validate_access)],
    new_log: LogCreate,
) -> LogCreatResult:
    """
    Add a potty log for a dog.
    """

    data = new_log.model_dump()
    create_result = await db.logs.insert_one(data)

    return LogCreatResult(id=str(create_result.inserted_id))


@app.delete(
    "/logs/{log_id}",
    tags=["logs"],
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
    token_check: Annotated[None, Depends(validate_access)],
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

    delete_result = await db.logs.delete_one({"_id": log_object_id})
    if not delete_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete log.",
        )

    return LogSuccessResult(success=True)


@app.patch(
    "/logs/{log_id}",
    tags=["logs"],
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
    token_check: Annotated[None, Depends(validate_access)],
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
        {"_id": log_object_id}, {"$set": update_data}
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
