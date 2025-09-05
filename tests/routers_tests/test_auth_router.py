import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from unittest.mock import AsyncMock, patch

from app.routers.auth_router import router
from app.schemas.auth_schema import UserSchema

app = FastAPI()
app.include_router(router)


@pytest.fixture
def any_user_dict():
    return {
        "user_email": "user@example.com",
        "user_password": "secret123",
        "first_name": "Ivan",
        "last_name": "Ivanov",
    }


@pytest.mark.asyncio
async def test_registration_success(any_user_dict):
    user_in = UserSchema(**any_user_dict)

    mock_db = AsyncMock()
    mock_db.get.return_value = None
    mock_db.create.return_value = user_in

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/registration", json=any_user_dict)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"ok": True, "msg": "User was created"}
    mock_db.get.assert_awaited_once_with(user_in.user_email)
    mock_db.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_registration_conflict(any_user_dict):
    mock_db = AsyncMock()
    mock_db.get.return_value = UserSchema(**any_user_dict)

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/registration", json=any_user_dict)

    assert resp.status_code == status.HTTP_409_CONFLICT
    assert resp.json()["detail"] == "User already exist"
    mock_db.get.assert_awaited_once_with(any_user_dict["user_email"])


@pytest.mark.asyncio
async def test_registration_create_failure(any_user_dict):
    mock_db = AsyncMock()
    mock_db.get.return_value = None
    mock_db.create.return_value = None

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/registration", json=any_user_dict)

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to create user" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_authentication_success(any_user_dict):
    auth_in = {
        "user_email": any_user_dict["user_email"],
        "user_password": any_user_dict["user_password"],
    }

    class FakeUser:
        def __init__(self, email, pw_hash):
            self.user_email = email
            self.user_password_hash = pw_hash

    mock_db = AsyncMock()
    fake_db_user = FakeUser(auth_in["user_email"], "hashed_pw")
    mock_db.get.return_value = fake_db_user

    fake_token = "tok"
    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db), patch(
        "app.routers.auth_router.is_hash_eq", return_value=True
    ) as mock_is_eq, patch(
        "app.routers.auth_router.create_access_token", return_value=fake_token
    ) as mock_create_token, patch(
        "app.routers.auth_router.set_cookies",
        return_value=JSONResponse(content={"ok": True}),
    ) as mock_set_cookies:

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/authentication", json=auth_in)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"ok": True}
    mock_db.get.assert_awaited_once_with(auth_in["user_email"])
    mock_is_eq.assert_called_once_with(
        auth_in["user_password"], fake_db_user.user_password_hash
    )
    mock_create_token.assert_called_once_with(subj=auth_in["user_email"])
    mock_set_cookies.assert_called_once_with(fake_token)


@pytest.mark.asyncio
async def test_authentication_wrong_email(any_user_dict):
    auth_in = {
        "user_email": any_user_dict["user_email"],
        "user_password": any_user_dict["user_password"],
    }

    mock_db = AsyncMock()
    mock_db.get.return_value = None

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/authentication", json=auth_in)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "Incorrect credentials"


@pytest.mark.asyncio
async def test_authentication_wrong_password(any_user_dict):
    auth_in = {
        "user_email": any_user_dict["user_email"],
        "user_password": any_user_dict["user_password"],
    }

    class FakeUser:
        def __init__(self, email, pw_hash):
            self.user_email = email
            self.user_password_hash = pw_hash

    mock_db = AsyncMock()
    mock_db.get.return_value = FakeUser(auth_in["user_email"], "hashed_pw")

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.db_auth", mock_db), patch(
        "app.routers.auth_router.is_hash_eq", return_value=False
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/auth/authentication", json=auth_in)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "Incorrect credentials"


@pytest.mark.asyncio
async def test_get_users_success():
    su_user = type("U", (), {"user_email": "admin@example.com"})
    mock_get_current = AsyncMock(return_value=su_user)

    fake_users = [{"user_email": "a@b", "first_name": "A", "last_name": "B"}]
    mock_db = AsyncMock()
    mock_db.get_all.return_value = fake_users

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.get_current_user", mock_get_current), patch(
        "app.routers.auth_router.db_auth", mock_db
    ), patch("app.routers.auth_router.settings") as mock_settings:
        mock_settings.SU = "admin@example.com"

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/auth/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_users_permission_denied():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "not_admin@example.com"})
    )
    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.get_current_user", mock_current), patch(
        "app.routers.auth_router.settings"
    ) as mock_settings:
        mock_settings.SU = "admin@example.com"

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/auth/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_password_success():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db = AsyncMock()
    mock_db.update.return_value = None

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.get_current_user", mock_current), patch(
        "app.routers.auth_router.db_auth", mock_db
    ), patch(
        "app.routers.auth_router.get_hash", return_value="new_hash"
    ) as mock_get_hash:

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(
                "/auth/user@example.com", json={"new_user_password": "newpass"}
            )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_password_failure_raises_http_exception():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db = AsyncMock()
    mock_db.update.side_effect = Exception("boom")

    transport = ASGITransport(app=app)
    with patch("app.routers.auth_router.get_current_user", mock_current), patch(
        "app.routers.auth_router.db_auth", mock_db
    ), patch("app.routers.auth_router.get_hash", return_value="new_hash"):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(
                "/auth/user@example.com", json={"new_user_password": "newpass"}
            )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]
