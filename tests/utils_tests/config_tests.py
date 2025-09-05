import pytest
from pydantic import ValidationError

from app.utils.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("DB_USER_NAME", "u")
    monkeypatch.setenv("DB_USER_PASS", "p")
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_NAME", "name")
    monkeypatch.setenv("BASE_URL_1", "http://a")
    monkeypatch.setenv("BASE_URL_2", "http://b")
    monkeypatch.setenv("JWT_SECRET", "s")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    monkeypatch.setenv("SU", "admin")

    s = Settings()
    assert s.HOST == "127.0.0.1"
    assert s.PORT == 8000
    assert isinstance(s.DB_USER_NAME, str)
    assert isinstance(s.DB_USER_PASS, str)
    assert isinstance(s.DB_HOST, str)
    assert s.BASE_URL_1 == "http://a"
    assert s.BASE_URL_2 == "http://b"
    assert isinstance(s.JWT_SECRET, str)
    assert isinstance(s.JWT_ALGORITHM, str)
    assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES > 0.5
    assert isinstance(s.SU, str)


def test_missing_required_env_raises(monkeypatch):
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ValidationError):
        Settings()
