from typing import Annotated

import httpx
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
)

from app.models import GenericException
from app.settings import settings

from .models import LoginResult

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"],
)


basic_security = HTTPBasic()


@router.get(
    "/login",
    response_model=LoginResult,
    responses={
        401: {"description": "Unauthorized", "model": GenericException},
    },
)
async def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
) -> LoginResult:
    """
    Email Login
    """

    async with httpx.AsyncClient() as client:
        r = await client.post(
            settings.google_auth_sign_in_url,
            params={"key": settings.google_auth_sign_in_key},
            json={
                "email": credentials.username,
                "password": credentials.password,
                "returnSecureToken": True,
            },
        )

        if r.is_success:
            data = r.json()
            access_token: str | None = data.get("idToken")
            expires_in: str | None = data.get("expiresIn")

            if access_token and expires_in:
                return LoginResult(
                    access_token=access_token, expires_in=int(expires_in)
                )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )
