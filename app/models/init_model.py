import datetime
import uuid as _uuid

from typing import Annotated, Optional, Literal
from decimal import Decimal

from sqlalchemy import Integer, String, Enum, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.sql import func

from sqlalchemy.dialects.postgresql import UUID


int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
str_4 = Annotated[str, mapped_column(String(4), nullable=False)]
str_32 = Annotated[str, mapped_column(String(32), nullable=False)]
str_64 = Annotated[str, mapped_column(String(64), nullable=False)]
optional_str = Annotated[Optional[str], mapped_column(String(64), nullable=True)]
email_str = Annotated[
    str, mapped_column(String(255), unique=True, nullable=False, index=True)
]
hash_str = Annotated[str, mapped_column(String(128), nullable=False)]
uuid_pk = Annotated[
    _uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
]
dec = Annotated[Decimal, mapped_column(Numeric(12, 3), nullable=False)]
timestamp = Annotated[
    datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]

PaymentStatus = Literal["Создан", "Оплачен", "Отменён", "Завершён"]
payment_status = Annotated[
    PaymentStatus,
    mapped_column(
        Enum("Создан", "Оплачен", "Отменён", "Завершён", name="payment_status_enum"),
        nullable=False,
    ),
]


class Base(DeclarativeBase): ...
