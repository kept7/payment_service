import pytest
from pydantic import ValidationError

from app.schemas.auth_schema import AuthSchema, UserSchema


def test_authschema_valid():
    obj = AuthSchema(user_email="user@example.com", user_password="abcd")
    assert obj.user_email == "user@example.com"
    assert obj.user_password == "abcd"


@pytest.mark.parametrize(
    "email,password",
    [
        ("not-an-email", "abcd"),
        ("user@example.com", "123"),
    ],
)
def test_authschema_invalid(email, password):
    with pytest.raises(ValidationError):
        AuthSchema(user_email=email, user_password=password)


def test_userschema_valid_names():
    obj = UserSchema(
        user_email="u@example.com",
        user_password="passw",
        first_name="John",
        last_name="Doe",
    )
    assert obj.first_name == "John"
    assert obj.last_name == "Doe"


@pytest.mark.parametrize(
    "first,last",
    [
        ("", "Doe"),
        ("John", ""),
        ("1234", "Doe"),
    ],
)
def test_userschema_invalid_name_fields(first, last):
    with pytest.raises(ValidationError):
        UserSchema(
            user_email="u@example.com",
            user_password="passw",
            first_name=first,
            last_name=last,
        )
