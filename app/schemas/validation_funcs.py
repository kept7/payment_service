import re

from typing import Optional, Literal


SchemaName = Literal["Payment", "User"]
LATIN_RE = re.compile(r"^[A-Za-z-]+$")


def must_be_four_digit_int(val: int | str) -> str:
    s = str(val)
    if not isinstance(s, str) or not s.isdigit():
        raise ValueError("Incorrect Card Number")

    return s


def must_be_valid_name(val: Optional[str], schema_name: SchemaName) -> Optional[str]:
    if val is None:
        return val

    if not val:
        raise ValueError("Field must be a non-empty")

    if schema_name == "User":
        if not any(ch.isalpha() for ch in val):
            raise ValueError("Field must contain at least one letter")
        return val

    if not LATIN_RE.match(val):
        raise ValueError(
            "Field contains invalid characters — only latin letters and '-' allowed"
        )

    if not any(ch.isalpha() for ch in val):
        raise ValueError("Field must contain at least one letter")

    if not all(ch.isupper() for ch in val if ch.isalpha()):
        raise ValueError("All letters in field must be uppercase")

    return val
