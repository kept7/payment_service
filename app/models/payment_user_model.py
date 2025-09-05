from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey
from app.models.init_model import Base, uuid_pk, email_str


class PaymentUserModel(Base):
    __tablename__ = "payment_user"

    user_email: Mapped[email_str]
    payment_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("payment.payment_id", ondelete="CASCADE"), nullable=False, index=True
    )
