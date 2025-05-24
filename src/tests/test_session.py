from datetime import timedelta
from typing import Annotated
from uuid import UUID

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.core import settings
from src.utils import get_or_create_session_id

app = FastAPI()


@app.get("/get-session")
async def get_session_endpoint(
    session_id: Annotated[str, Depends(get_or_create_session_id)],
):
    return {"session_id": session_id}


def test_creates_session_id_if_none_exists():
    local_client = TestClient(app)
    response = local_client.get("/get-session")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    new_session_id = data["session_id"]

    try:
        UUID(new_session_id, version=4)
    except ValueError:
        pytest.fail(f"Generated session_id '{new_session_id}' is not a valid UUIDv4")

    assert settings.USER_SESSION_COOKIE_NAME in response.cookies
    assert response.cookies[settings.USER_SESSION_COOKIE_NAME] == new_session_id

    assert "set-cookie" in response.headers
    set_cookie_header = response.headers["set-cookie"]

    assert f"{settings.USER_SESSION_COOKIE_NAME}={new_session_id}" in set_cookie_header
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header
    assert f"Max-Age={int(timedelta(days=365).total_seconds())}" in set_cookie_header
    assert "Path=/" in set_cookie_header


def test_reuses_session_id_if_exists():
    local_client = TestClient(app)

    initial_response = local_client.get("/get-session")
    assert initial_response.status_code == 200
    initial_data = initial_response.json()
    assert "session_id" in initial_data
    initial_session_id = initial_data["session_id"]

    assert "set-cookie" in initial_response.headers, (
        "Set-Cookie header is missing in the initial response!"
    )

    assert settings.USER_SESSION_COOKIE_NAME in initial_response.cookies, (
        f"Cookie '{settings.USER_SESSION_COOKIE_NAME}' not found in initial_response.cookies"
    )
    assert (
        initial_response.cookies[settings.USER_SESSION_COOKIE_NAME]
        == initial_session_id
    )

    response_with_cookie = local_client.get("/get-session")
    assert response_with_cookie.status_code == 200
    data = response_with_cookie.json()
    assert "session_id" in data
    reused_session_id = data["session_id"]

    assert reused_session_id == initial_session_id
    assert "set-cookie" not in response_with_cookie.headers, (
        "A new Set-Cookie header was unexpectedly found in the second response!"
    )
