from pydantic import BaseModel


class LoginResult(BaseModel):
    access_token: str
    expires_in: int
