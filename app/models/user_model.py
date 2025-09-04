from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .init_model import Base, int_pk, int_fk, str_32, str_64, optional_str, uuid_pk


class AuthModel(Base):
    __tablename__ = "auth_data"

    id: Mapped[uuid_pk]
    first_name: Mapped[str_32]
    last_name: Mapped[str_64]
    user_email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
