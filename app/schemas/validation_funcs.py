from typing import Optional, Literal


SchemaName = Literal["Payment", "User"]


def must_be_four_digit_int(val) -> str:
    s = str(val)
    if not isinstance(s, str) or not s.isdigit():
        raise ValueError("Incorrect Card Number")

    return s


def must_be_valid_name(val: Optional[str], schema_name: SchemaName) -> Optional[str]:
    if val is None:
        return val

    if not val:
        raise ValueError("Field must be a non-empty")

    letters = [ch for ch in val if ch.isalpha()]
    if not letters:
        raise ValueError("Field must contain at least one letter")

    if schema_name == "Payment":
        if not all(ch.isupper() for ch in letters):
            raise ValueError("All letters in field must be uppercase")

    for ch in val:
        if not (ch.isalpha() or ch in {"-"}):
            raise ValueError("Field contains invalid characters")

    return val
