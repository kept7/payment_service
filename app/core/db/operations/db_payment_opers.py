from typing import Sequence
import uuid as _uuid

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.operations.db_operations import DBRepository
from app.models.init_model import PaymentStatus
from app.models.payment_model import PaymentModel
from app.schemas.payment_schema import PaymentSchema


class DBPaymentRepository(DBRepository):
    async def create(self, payment_data: PaymentSchema) -> PaymentModel | None:
        @self.connection
        async def inner_create(
            inner_payment_data: PaymentSchema, session: AsyncSession
        ):
            new_payment = PaymentModel(
                card_number=inner_payment_data.card_number,
                first_name=inner_payment_data.first_name,
                last_name=inner_payment_data.last_name,
                second_name=inner_payment_data.second_name,
                amount=inner_payment_data.amount,
                status="Создан",
            )

            try:
                session.add(new_payment)
                await session.commit()
                await session.refresh(new_payment)
                return new_payment
            except IntegrityError:
                await session.rollback()
                return None
            except Exception:
                await session.rollback()
                raise

        return await inner_create(payment_data)

    async def get(self, payment_id: _uuid.UUID) -> PaymentModel | None:
        @self.connection
        async def inner_get(
            inner_payment_id: _uuid.UUID,
            session: AsyncSession,
        ):
            query = select(PaymentModel).filter_by(payment_id=inner_payment_id)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(payment_id)

    async def update(
        self,
        payment_id: _uuid.UUID,
        status: PaymentStatus,
    ) -> None:
        @self.connection
        async def inner_update(
            inner_payment_id: _uuid.UUID,
            inner_status: PaymentStatus,
            session: AsyncSession,
        ):
            stmt = (
                update(PaymentModel)
                .values(status=inner_status)
                .filter_by(payment_id=inner_payment_id)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_update(payment_id, status)

    async def delete(
        self,
        payment_id: _uuid.UUID,
    ) -> None:
        @self.connection
        async def inner_delete(inner_payment_id: _uuid.UUID, session: AsyncSession):
            stmt = delete(PaymentModel).filter_by(payment_id=inner_payment_id)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(payment_id)

    async def get_all(self) -> Sequence[PaymentModel]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(PaymentModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()

    async def get_by_status(
        self, payment_id: _uuid.UUID, status: PaymentStatus
    ) -> Sequence[PaymentModel]:
        @self.connection
        async def inner_get_by_status(
            inner_payment_id: _uuid.UUID,
            inner_status: PaymentStatus,
            session: AsyncSession,
        ):
            query = select(PaymentModel).filter_by(
                payment_id=inner_payment_id, status=inner_status
            )
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get_by_status(payment_id, status)

    async def get_by_amount(
        self, payment_id: _uuid.UUID, amount: PaymentModel.amount
    ) -> Sequence[PaymentModel]:
        @self.connection
        async def inner_get_by_amount(
            inner_payment_id: _uuid.UUID,
            inner_amount: PaymentModel.creation_time,
            session: AsyncSession,
        ):
            query = select(PaymentModel).filter(
                PaymentModel.payment_id == inner_payment_id,
                PaymentModel.amount < inner_amount,
            )
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get_by_amount(payment_id, amount)
