from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationError


class PaymentSchema(BaseModel):
    card_number: str = Field(min_length=4, max_length=4)
    last_name: str = Field(min_length=1, max_length=64)
    first_name: str = Field(min_length=1, max_length=32)
    second_name: Optional[str] = Field(None, max_length=64)

    @field_validator('card_number', mode='before')
    def must_be_four_digit_int(cls, val) -> str:
        s = str(val)
        if not isinstance(s, str) or not s.isdigit():
            raise ValueError('Incorrect Card Number')

        return s

    @field_validator('last_name', 'first_name', 'second_name')
    def must_be_valid_name(cls, val: Optional[str]) -> Optional[str]:
        if val is None:
            return val

        if not val:
            raise ValueError('Field must be a non-empty')

        letters = [ch for ch in val if ch.isalpha()]
        if not letters:
            raise ValueError('Field must contain at least one letter')

        if not all(ch.isupper() for ch in letters):
            raise ValueError('All letters in field must be uppercase')

        for ch in val:
            if not (ch.isalpha() or ch in {'-'}):
                raise ValueError('Field contains invalid characters')

        return val