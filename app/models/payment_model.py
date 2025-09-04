from typing import Literal, Annotated

from sqlalchemy import Enum, mapped_column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .init_model import Base


PaymentStatus = Literal["Создан", "Оплачен", "Отменён", "Завершён"]
payment_status = Annotated[
    PaymentStatus,
    mapped_column(
        Enum("Создан", "Оплачен", "Отменён", "Завершён", name="payment_status_enum"),
        nullable=False,
    ),
]


class PaymentModel(Base):
    __tablename__ = "payment"

    payment_id: "UUID"
    card_number: str
    amount: str
    creation_time: "TimeStamp"
    status: Mapped[payment_status]
