from sqlalchemy.orm import Mapped, mapped_column

from .init_model import Base, int_pk, str_32, str_64, email_str, hash_str


class AuthModel(Base):
    __tablename__ = "auth_data"

    id: Mapped[int_pk]
    first_name: Mapped[str_32]
    last_name: Mapped[str_64]
    user_email: Mapped[email_str]
    user_password_hash: Mapped[hash_str]
