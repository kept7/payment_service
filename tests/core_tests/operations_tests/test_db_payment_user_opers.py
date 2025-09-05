from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError
from app.core.db.operations.db_paym_user_opers import DBPaymentUserRepository
from app.models.payment_user_model import PaymentUserModel
import uuid


@pytest.fixture
def fake_session():
    sess = MagicMock()
    sess.add = MagicMock()
    sess.refresh = AsyncMock()
    sess.execute = AsyncMock()
    sess.commit = AsyncMock()
    sess.rollback = AsyncMock()
    return sess


@pytest.fixture
def payment_user_repository():
    r = DBPaymentUserRepository(session=MagicMock())

    def connection_decorator(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    r.connection = connection_decorator
    return r


@pytest.mark.asyncio
async def test_create_payment_user_success(payment_user_repository, fake_session):
    user_email = "john@example.com"
    payment_id = uuid.uuid4()

    fake_session.add = MagicMock()
    fake_session.commit = AsyncMock()
    fake_session.refresh = AsyncMock()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_user_repository.connection = connection_with_session

    result = await payment_user_repository.create(user_email, payment_id)

    assert result is not None
    assert isinstance(result, PaymentUserModel)
    assert result.user_email == user_email
    assert result.payment_id == payment_id

    fake_session.add.assert_called()
    fake_session.commit.assert_called()
    fake_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_create_payment_user_integrity_error(
    payment_user_repository, fake_session
):
    user_email = "jane@example.com"
    payment_id = uuid.uuid4()

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

    payment_user_repository.connection = connection_with_session

    result = await payment_user_repository.create(user_email, payment_id)
    assert result is None
    fake_session.rollback.assert_called()


@pytest.mark.asyncio
async def test_get_payment_user(payment_user_repository, fake_session):
    payment_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.one_or_none.return_value = PaymentUserModel(
        user_email="john@example.com", payment_id=payment_id
    )
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_user_repository.connection = connection_with_session

    res = await payment_user_repository.get(payment_id)
    assert isinstance(res, PaymentUserModel)
    assert res.user_email == "john@example.com"


@pytest.mark.asyncio
async def test_get_all_payment_users(payment_user_repository, fake_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    user1 = PaymentUserModel(user_email="user1@example.com", payment_id=uuid.uuid4())
    user2 = PaymentUserModel(user_email="user2@example.com", payment_id=uuid.uuid4())
    mock_scalars.all.return_value = [user1, user2]
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_user_repository.connection = connection_with_session

    res = await payment_user_repository.get_all()
    assert isinstance(res, list)
    assert len(res) == 2
    assert all(isinstance(x, PaymentUserModel) for x in res)


@pytest.mark.asyncio
async def test_delete_payment_user(payment_user_repository, fake_session):
    fake_session.execute = AsyncMock()
    fake_session.commit = AsyncMock()

    payment_id = uuid.uuid4()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_user_repository.connection = connection_with_session

    await payment_user_repository.delete(payment_id)
    fake_session.execute.assert_called()
    fake_session.commit.assert_called()


@pytest.mark.asyncio
async def test_get_by_user_email(payment_user_repository, fake_session):
    user_email = "john@example.com"
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    user1 = PaymentUserModel(user_email=user_email, payment_id=uuid.uuid4())
    user2 = PaymentUserModel(user_email=user_email, payment_id=uuid.uuid4())
    mock_scalars.all.return_value = [user1, user2]
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_user_repository.connection = connection_with_session

    res = await payment_user_repository.get_by_user(user_email)
    assert isinstance(res, list)
    assert len(res) == 2
    assert all(isinstance(x, PaymentUserModel) for x in res)
    assert all(x.user_email == user_email for x in res)
