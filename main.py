import os
from datetime import datetime
from typing import Any, Optional

import bson
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI(
    title="💩 Poopyrus",
    description="We don't take shit.. we track it.",
    version="1.0.0",
    docs_url="/",
)
db: AsyncIOMotorDatabase[Any] = AsyncIOMotorClient(
    MONGO_URI, tlsAllowInvalidCertificates=True
)["poopyrus"]


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


@app.get("/logs", tags=["logs"], response_model=list[Log])
async def get_logs() -> list[Log]:
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Log not found.",
            "model": GenericException,
        },
    },
)
async def get_log(log_id: str) -> Log:
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
)
async def add_log(new_log: LogCreate) -> LogCreatResult:
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
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to delete log",
            "model": GenericException,
        },
    },
)
async def delete_log(log_id: str) -> LogSuccessResult:
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
        status.HTTP_404_NOT_FOUND: {
            "description": "Log not found.",
            "model": GenericException,
        },
    },
)
async def update_log(log_id: str, log_update: LogUpdate) -> LogSuccessResult:
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
