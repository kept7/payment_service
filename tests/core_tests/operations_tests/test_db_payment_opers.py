import uuid
import pytest

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError

from app.core.db.operations.db_payment_opers import DBPaymentRepository
from app.models.payment_model import PaymentModel
from app.schemas.payment_schema import PaymentSchema


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
def payment_repository():
    r = DBPaymentRepository(session=MagicMock())

    def connection_decorator(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    r.connection = connection_decorator
    return r


@pytest.mark.asyncio
async def test_create_payment_success(payment_repository, fake_session):
    payment_data = PaymentSchema(
        card_number="3456",
        first_name="JOHN",
        last_name="DOE",
        second_name=None,
        amount=100.00,
        status="Создан",
    )

    fake_session.add = MagicMock()
    fake_session.commit = AsyncMock()
    fake_session.refresh = AsyncMock()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_repository.connection = connection_with_session

    result = await payment_repository.create(payment_data)

    assert result is not None
    assert isinstance(result, PaymentModel)

    fake_session.add.assert_called()
    fake_session.commit.assert_called()
    fake_session.refresh.assert_called()


@pytest.mark.asyncio
async def test_create_payment_integrity_error(payment_repository, fake_session):
    payment_data = PaymentSchema(
        card_number="2456",
        first_name="JANE",
        last_name="SMITH",
        second_name=None,
        amount=200.00,
        status="Создан",
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

    payment_repository.connection = connection_with_session

    result = await payment_repository.create(payment_data)
    assert result is None
    fake_session.rollback.assert_called()


@pytest.mark.asyncio
async def test_get_payment(payment_repository, fake_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.one_or_none.return_value = PaymentModel(
        payment_id=uuid.uuid4(),
        card_number="3456",
        first_name="JOHN",
        last_name="DOE",
        second_name=None,
        amount=100.00,
        status="Создан",
    )
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_repository.connection = connection_with_session

    res = await payment_repository.get(mock_scalars.one_or_none.return_value.payment_id)
    assert isinstance(res, PaymentModel)
    assert res.card_number == "3456"


@pytest.mark.asyncio
async def test_get_all_payments(payment_repository, fake_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    payment1 = PaymentModel(
        payment_id=uuid.uuid4(),
        card_number="3456",
        first_name="JOHN",
        last_name="DOE",
        second_name=None,
        amount=100.00,
        status="Создан",
    )
    payment2 = PaymentModel(
        payment_id=uuid.uuid4(),
        card_number="7654",
        first_name="JANE",
        last_name="SMITH",
        second_name=None,
        amount=200.00,
        status="Создан",
    )
    mock_scalars.all.return_value = [payment1, payment2]
    mock_result.scalars.return_value = mock_scalars
    fake_session.execute = AsyncMock(return_value=mock_result)

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_repository.connection = connection_with_session

    res = await payment_repository.get_all()
    assert isinstance(res, list)
    assert len(res) == 2
    assert all(isinstance(x, PaymentModel) for x in res)


@pytest.mark.asyncio
async def test_update_payment(payment_repository, fake_session):
    fake_session.execute = AsyncMock()
    fake_session.commit = AsyncMock()

    payment_id = uuid.uuid4()
    new_status = "Обработан"

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_repository.connection = connection_with_session

    await payment_repository.update(payment_id, new_status)
    fake_session.execute.assert_called()
    fake_session.commit.assert_called()


@pytest.mark.asyncio
async def test_delete_payment(payment_repository, fake_session):
    fake_session.execute = AsyncMock()
    fake_session.commit = AsyncMock()

    payment_id = uuid.uuid4()

    def connection_with_session(fn):
        async def wrapper(*args, **kwargs):
            return await fn(*args, fake_session, **kwargs)

        return wrapper

    payment_repository.connection = connection_with_session

    await payment_repository.delete(payment_id)
    fake_session.execute.assert_called()
    fake_session.commit.assert_called()
