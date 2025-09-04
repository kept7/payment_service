from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationError
from pydantic.types import EmailStr

from .validation_funcs import must_be_valid_name


class UserSchema(BaseModel):
    user_email: EmailStr
    user_password: str = Field(min_length=4)


class UserRegSchema(UserSchema):
    last_name: str = Field(min_length=1, max_length=64)
    first_name: str = Field(min_length=1, max_length=32)
    second_name: Optional[str] = Field(None, max_length=64)

    @field_validator("last_name", "first_name", "second_name")
    def must_be_valid_name_wrapper(cls, val: Optional[str]) -> Optional[str]:
        return must_be_valid_name(val, "User")


class AuthUserSchema(UserSchema): ...
