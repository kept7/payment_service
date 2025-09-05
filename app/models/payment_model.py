from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .init_model import (
    Base,
    str_4,
    dec,
    str_32,
    str_64,
    optional_str,
    uuid_pk,
    payment_status,
    timestamp,
)


class PaymentModel(Base):
    __tablename__ = "payment"

    payment_id: Mapped[uuid_pk]
    card_number: Mapped[str_4]
    first_name: Mapped[str_32]
    last_name: Mapped[str_64]
    second_name: Mapped[optional_str]
    amount: Mapped[dec]
    creation_time: Mapped[timestamp]
    status: Mapped[payment_status]
