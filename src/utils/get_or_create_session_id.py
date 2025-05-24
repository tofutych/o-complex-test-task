from datetime import timedelta
from uuid import uuid4

from fastapi import (
    Cookie,
    Response,
)

from src.core import settings


async def get_or_create_session_id(
    response: Response,
    user_session_id: str | None = Cookie(None, alias=settings.USER_SESSION_COOKIE_NAME),  # pyright: ignore [reportCallInDefaultInitializer]
) -> str:
    if user_session_id is None:
        user_session_id = str(uuid4())
        response.set_cookie(
            key=settings.USER_SESSION_COOKIE_NAME,
            value=user_session_id,
            httponly=True,
            max_age=int(timedelta(days=365).total_seconds()),
            samesite="lax",
        )
    return user_session_id
