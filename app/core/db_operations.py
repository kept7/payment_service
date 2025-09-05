from functools import wraps
from typing import Callable, Coroutine, Any, TypeVar, Sequence

from pydantic import EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.auth_schema import UserSchema
from app.models.auth_model import AuthModel


R = TypeVar("R")


class DBAuthRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    async def create(
        self,
        user_data: UserSchema,
    ) -> bool:
        @self.connection
        async def inner_create(
            inner_user_data: UserSchema,
            session: AsyncSession,
        ):
            new_user = AuthModel(
                first_name=inner_user_data.first_name,
                last_name=inner_user_data.last_name,
                user_email=inner_user_data.user_email,
                user_password_hash=inner_user_data.user_password,
            )

            try:
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
            except IntegrityError:
                await session.rollback()
                return None
            except Exception:
                await session.rollback()
                raise

        return bool(await inner_create(user_data))

    async def get(self, user_email: EmailStr) -> AuthModel | None:
        @self.connection
        async def inner_get(inner_user_email: EmailStr, session: AsyncSession):
            query = select(AuthModel).filter_by(user_email=inner_user_email)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(user_email)

    async def update(
        self,
        user_email: EmailStr,
        user_password_hash: str,
    ) -> None:
        @self.connection
        async def inner_update(
            inner_user_email: EmailStr,
            inner_user_pass_hash: str,
            session: AsyncSession,
        ):
            stmt = (
                update(AuthModel)
                .values(user_password_hash=inner_user_pass_hash)
                .filter_by(user_email=inner_user_email)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_update(user_email, user_password_hash)

    async def delete(
        self,
        user_email: EmailStr,
    ) -> None:
        @self.connection
        async def inner_delete(inner_user_email: EmailStr, session: AsyncSession):
            stmt = delete(AuthModel).filter_by(user_email=inner_user_email)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(user_email)

    async def get_all(self) -> Sequence[AuthModel]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(AuthModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()


class DBPaymentRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    async def create(self): ...

    async def get(self): ...

    async def update(self): ...

    async def delete(self): ...
