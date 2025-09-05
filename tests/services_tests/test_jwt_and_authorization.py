from datetime import timedelta
import pytest
from fastapi.responses import JSONResponse
from types import SimpleNamespace
from fastapi import HTTPException

from app.services import jwt_handler as jh
from app.services import authorization_handler as ah


def test_create_and_verify_token_roundtrip():
    token = jh.create_access_token(
        "user@example.com", expires_delta=timedelta(minutes=1)
    )
    assert isinstance(token, str)

    payload = jh.verify_jwt_token(token)
    assert payload["sub"] == "user@example.com"
    assert "iat" in payload and "exp" in payload


def test_verify_expired_token_raises():
    token = jh.create_access_token("u", expires_delta=timedelta(minutes=-1))
    with pytest.raises(Exception) as excinfo:
        jh.verify_jwt_token(token)
    assert getattr(excinfo.value, "status_code", None) == 401


def test_verify_invalid_token_raises():
    with pytest.raises(Exception) as excinfo:
        jh.verify_jwt_token("not-a-token")
    assert getattr(excinfo.value, "status_code", None) == 401


def test_set_cookies_returns_jsonresponse_and_cookie_max_age():
    token = jh.create_access_token("a", expires_delta=timedelta(minutes=1))
    resp: JSONResponse = jh.set_cookies(token)
    assert isinstance(resp, JSONResponse)
    headers = {k.lower(): v for k, v in resp.headers.items()}
    assert "set-cookie" in headers


def test_get_token_from_cookie_works_with_mock_request():
    class DummyRequest:
        def __init__(self, cookies):
            self.cookies = cookies

    req = DummyRequest({"access_token": "T"})
    assert jh.get_token_from_cookie(req) == "T"
    assert jh.get_token_from_cookie(req, cookie_name="missing") is None


def _make_req_with_cookie(token_value: str | None):
    class DummyRequest:
        def __init__(self, cookies):
            self.cookies = cookies

    cookies = {"access_token": token_value} if token_value is not None else {}
    return DummyRequest(cookies)


@pytest.mark.asyncio
async def test_get_current_user_raises_when_no_cookie():
    req = _make_req_with_cookie(None)
    with pytest.raises(HTTPException) as exc:
        await ah.get_current_user(req)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    def fake_verify(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    monkeypatch.setattr(ah, "verify_jwt_token", fake_verify)

    req = _make_req_with_cookie("bad")
    with pytest.raises(HTTPException) as exc:
        await ah.get_current_user(req)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_token_without_sub(monkeypatch):
    monkeypatch.setattr(ah, "verify_jwt_token", lambda token: {"no_sub": "x"})
    req = _make_req_with_cookie("t")
    with pytest.raises(HTTPException) as exc:
        await ah.get_current_user(req)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
    monkeypatch.setattr(ah, "verify_jwt_token", lambda token: {"sub": "u@example.com"})
    fake_db = SimpleNamespace()

    async def fake_get(email):
        return None

    fake_db.get = fake_get
    monkeypatch.setattr(ah, "db_auth", fake_db)

    req = _make_req_with_cookie("t")
    with pytest.raises(HTTPException) as exc:
        await ah.get_current_user(req)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    monkeypatch.setattr(ah, "verify_jwt_token", lambda token: {"sub": "u@example.com"})
    fake_user = {"email": "u@example.com", "id": 1}
    fake_db = SimpleNamespace()

    async def fake_get(email):
        assert email == "u@example.com"
        return fake_user

    fake_db.get = fake_get
    monkeypatch.setattr(ah, "db_auth", fake_db)

    req = _make_req_with_cookie("t")
    user = await ah.get_current_user(req)
    assert user == fake_user
