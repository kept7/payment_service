import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.db.operations.db_operations import DBRepository


@pytest.mark.asyncio
async def test_connection_passes_session():
    mock_session_ctx = AsyncMock()
    mock_session_ctx.rollback = AsyncMock()

    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_ctx)
    mock_session_cm.__aexit__ = AsyncMock(return_value=None)

    session_factory = MagicMock(return_value=mock_session_cm)

    repo = DBRepository(session=session_factory)

    called = {}

    async def target(x, *, session):
        called["session_is_correct"] = session is mock_session_ctx
        called["x"] = x
        return "ok"

    wrapped = repo.connection(target)

    res = await wrapped(123)
    assert res == "ok"
    assert called["x"] == 123
    assert called["session_is_correct"] is True

    session_factory.assert_called_once()
    mock_session_cm.__aenter__.assert_awaited()
    mock_session_cm.__aexit__.assert_awaited()


@pytest.mark.asyncio
async def test_connection_rolls_back_on_exception():
    mock_session_ctx = AsyncMock()
    mock_session_ctx.rollback = AsyncMock()

    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__ = AsyncMock(return_value=mock_session_ctx)
    mock_session_cm.__aexit__ = AsyncMock(return_value=None)

    session_factory = MagicMock(return_value=mock_session_cm)
    repo = DBRepository(session=session_factory)

    async def target_raises(*, session):
        raise ValueError("boom")

    wrapped = repo.connection(target_raises)

    with pytest.raises(ValueError):
        await wrapped()

    mock_session_ctx.rollback.assert_awaited()
    mock_session_cm.__aenter__.assert_awaited()
    mock_session_cm.__aexit__.assert_awaited()
