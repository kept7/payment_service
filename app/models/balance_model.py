from sqlalchemy.orm import Mapped

from app.models.init_model import Base, int_pk, email_str, dec


class BalanceSchema(Base):
    __tablename__ = "Balance"

    id: Mapped[int_pk]
    user_email: Mapped[email_str]
    balance: Mapped[dec]
