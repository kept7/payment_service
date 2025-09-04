import uuid as _uuid

from typing import Annotated, Optional

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column

from sqlalchemy.dialects.postgresql import UUID


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
int_fk = Annotated[int, mapped_column(Integer, ForeignKey("user.id"), nullable=False)]
str_32 = Annotated[str, mapped_column(String(32), nullable=False)]
str_64 = Annotated[str, mapped_column(String(64), nullable=False)]
optional_str = Annotated[Optional[str], mapped_column(String(64), nullable=True)]
uuid_pk = Annotated[
    _uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
]


class Base(DeclarativeBase): ...
