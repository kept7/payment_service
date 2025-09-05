from functools import wraps
from typing import Callable, Coroutine, Any, TypeVar

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


R = TypeVar("R")


class DBRepository:
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
