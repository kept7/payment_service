from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationError

from .validation_funcs import must_be_four_digit_int, must_be_valid_name


class PaymentSchema(BaseModel):
    card_number: str = Field(min_length=4, max_length=4)
    last_name: str = Field(min_length=1, max_length=64)
    first_name: str = Field(min_length=1, max_length=32)
    second_name: Optional[str] = Field(None, max_length=64)

    @field_validator("card_number", mode="before")
    def must_be_four_digit_int_wrapper(cls, val) -> str:
        return must_be_four_digit_int(val)

    @field_validator("last_name", "first_name", "second_name")
    def must_be_valid_name_wrapper(cls, val: Optional[str]) -> Optional[str]:
        return must_be_valid_name(val, "Payment")
