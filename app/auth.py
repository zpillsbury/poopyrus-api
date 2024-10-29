from typing import Annotated

from anyio.to_thread import run_sync
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

security = HTTPBearer()


async def validate_access(
    access_token: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str | None:
    """
    Validates access tokens.

    Raises a 401 HTTPException if an invalid token is provided.
    """
    try:
        user_result = await run_sync(auth.verify_id_token, access_token.credentials)
        if user_result:
            user_id: str | None = user_result.get("user_id")

            return user_id

    except Exception as e:
        print(e)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
