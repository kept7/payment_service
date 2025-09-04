from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationError
from pydantic.types import EmailStr


class UserSchema(BaseModel):
    user_email: EmailStr
    user_password: str

class UserRegSchema(UserSchema):
    last_name: str = Field(min_length=1, max_length=64)
    first_name: str = Field(min_length=1, max_length=32)
    second_name: Optional[str] = Field(None, max_length=64)

    @field_validator('last_name', 'first_name', 'second_name')
    def must_be_valid_name(cls, val: Optional[str]) -> Optional[str]:
        if val is None:
            return val

        if not val:
            raise ValueError('Field must be a non-empty string')

        letters = [ch for ch in val if ch.isalpha()]
        if not letters:
            raise ValueError('Field must contain at least one letter')

        for ch in val:
            if not (ch.isalpha() or ch in {'-'}):
                raise ValueError('Field contains invalid characters')

        return val

class AuthUserSchema(UserSchema):
    ...