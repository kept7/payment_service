from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.db.operations.db_auth_opers import DBAuthRepository
from app.models.auth_model import AuthModel
from app.schemas.auth_schema import UserSchema


@pytest.fixture
def fake_session():
    sess = MagicMock()
    sess.add = MagicMock()
    sess.refresh = MagicMock()
    sess.execute = AsyncMock()
    sess.commit = AsyncMock()
    sess.rollback = AsyncMock()
    return sess


@pytest.fixture
def repo():
    r = DBAuthRepository(session=MagicMock())

    def connection_decorator(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    r.connection = connection_decorator
    return r


@pytest.mark.asyncio
async def test_create_success(repo, fake_session):
    user_in = UserSchema(
        first_name="John",
        last_name="Doe",
        user_email="john@example.com",
        user_password="hashedpw",
    )

    fake_session.add = MagicMock()
    fake_session.commit = AsyncMock()
    fake_session.refresh = AsyncMock()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    repo.connection = connection_with_session

    result = await repo.create(user_in)

    assert result is not None
    assert isinstance(result, AuthModel)

    fake_session.add.assert_called()
    fake_session.commit.assert_called()
    fake_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_create_integrity_error(repo, fake_session):
    user_in = UserSchema(
        first_name="Jane",
        last_name="Smith",
        user_email="jane@example.com",
        user_password="pass",
    )

    fake_session.add = MagicMock()

    async def commit_raises():
        raise IntegrityError(statement="stmt", params={}, orig=None)

    fake_session.commit = AsyncMock(side_effect=commit_raises)
    fake_session.rollback = AsyncMock()
    fake_session.refresh = MagicMock()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    repo.connection = connection_with_session

    result = await repo.create(user_in)
    assert result is None
    fake_session.rollback.assert_called()


@pytest.mark.asyncio
async def test_get_returns_user(repo, fake_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.one_or_none.return_value = AuthModel(
        first_name="A", last_name="B", user_email="a@b.com", user_password_hash="h"
    )
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    repo.connection = connection_with_session

    res = await repo.get("a@b.com")
    assert isinstance(res, AuthModel)
    assert res.user_email == "a@b.com"


@pytest.mark.asyncio
async def test_get_all(repo, fake_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    user1 = AuthModel(
        first_name="X", last_name="Y", user_email="x@y.com", user_password_hash="h"
    )
    user2 = AuthModel(
        first_name="M", last_name="N", user_email="m@n.com", user_password_hash="h2"
    )
    mock_scalars.all.return_value = [user1, user2]
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    repo.connection = connection_with_session

    res = await repo.get_all()
    assert isinstance(res, list)
    assert len(res) == 2
    assert all(isinstance(x, AuthModel) for x in res)


@pytest.mark.asyncio
async def test_update_and_delete_call_execute_and_commit(repo, fake_session):
    fake_session.execute = AsyncMock()
    fake_session.commit = AsyncMock()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    repo.connection = connection_with_session

    await repo.update("u@u.com", "newhash")
    fake_session.execute.assert_called()
    fake_session.commit.assert_called()

    fake_session.execute.reset_mock()
    fake_session.commit.reset_mock()

    await repo.delete("u@u.com")
    fake_session.execute.assert_called()
    fake_session.commit.assert_called()
