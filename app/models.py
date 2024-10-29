from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GenericException(BaseModel):
    detail: str


class Log(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    date: str
    note: Optional[str] = None


class LogCreate(BaseModel):
    name: str
    type: str
    date: datetime


class LogUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    date: Optional[datetime] = None
    note: Optional[str] = None


class LogCreatResult(BaseModel):
    id: str


class LogSuccessResult(BaseModel):
    success: bool


class LoginResult(BaseModel):
    access_token: str
    expires_in: int
