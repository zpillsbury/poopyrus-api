from pydantic import BaseModel


class GenericException(BaseModel):
    detail: str


class LoginResult(BaseModel):
    access_token: str
    expires_in: int
