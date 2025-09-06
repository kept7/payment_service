import pytest
from app.services.hash_handler import get_hash, is_hash_eq


def test_get_hash_and_verify_success():
    h = get_hash("password123")
    assert isinstance(h, str)
    assert is_hash_eq("password123", h) is True


def test_get_hash_invalid_type_raises():
    with pytest.raises(TypeError):
        get_hash(123)


def test_is_hash_eq_invalid_types_raises():
    with pytest.raises(TypeError):
        is_hash_eq(123, "somehash")
    with pytest.raises(TypeError):
        is_hash_eq("a", 123)


def test_is_hash_eq_mismatch_and_corrupt_hash_returns_false():
    h = get_hash("password123")
    assert is_hash_eq("wrong-password", h) is False
    assert is_hash_eq("password123", h + "corrupt") is False
