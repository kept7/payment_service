from typing import Sequence
import uuid as _uuid

from pydantic import EmailStr
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db.operations.db_operations import DBRepository
from app.models.payment_user_model import PaymentUserModel


class DBPaymentUserRepository(DBRepository):
    async def create(
        self, user_email: EmailStr, payment_id: _uuid.UUID
    ) -> PaymentUserModel:
        @self.connection
        async def inner_create(
            inner_user_email: EmailStr,
            inner_payment_id: _uuid.UUID,
            session: AsyncSession,
        ):
            new_record = PaymentUserModel(
                user_email=inner_user_email,
                payment_id=inner_payment_id,
            )

            try:
                session.add(new_record)
                await session.commit()
                await session.refresh(new_record)
                return new_record
            except IntegrityError:
                await session.rollback()
                return None
            except Exception:
                await session.rollback()
                raise

        return await inner_create(user_email, payment_id)

    async def get(
        self,
        payment_id: _uuid.UUID,
    ) -> PaymentUserModel | None:
        @self.connection
        async def inner_get(
            inner_payment_id: _uuid.UUID,
            session: AsyncSession,
        ):
            query = select(PaymentUserModel).filter_by(payment_id=inner_payment_id)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(payment_id)

    async def update(self): ...

    async def delete(
        self,
        payment_id: _uuid.UUID,
    ) -> None:
        @self.connection
        async def inner_delete(
            inner_payment_id: _uuid.UUID,
            session: AsyncSession,
        ):
            stmt = delete(PaymentUserModel).filter_by(payment_id=inner_payment_id)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(payment_id)

    async def get_all(self) -> Sequence[PaymentUserModel]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(PaymentUserModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()

    async def get_by_user(self, user_email: EmailStr) -> Sequence[PaymentUserModel]:
        @self.connection
        async def inner_get_by_user(
            inner_user_email: EmailStr,
            session: AsyncSession,
        ):
            query = select(PaymentUserModel).filter_by(user_email=inner_user_email)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_by_user(user_email)
