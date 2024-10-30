from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Pet(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class PetCreate(BaseModel):
    name: str
    type: str


class PetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class PetCreatResult(BaseModel):
    id: str


class PetSuccessResult(BaseModel):
    success: bool
