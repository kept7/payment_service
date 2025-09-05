import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, status
from unittest.mock import AsyncMock, patch

from app.routers.payment_router import router  # измените путь, если иначе
from app.models.init_model import PaymentStatus

app = FastAPI()
app.include_router(router)


@pytest.fixture
def fake_payment_obj():
    class P:
        def __init__(self, pid):
            self.payment_id = pid
            self.status = "Создан"  # default
            self.amount = 1.23

    return P(uuid.uuid4())


@pytest.mark.asyncio
async def test_create_payment_success(fake_payment_obj):
    payment_payload = {"payment_id": str(fake_payment_obj.payment_id), "amount": 1.23}

    mock_db_payment = AsyncMock()
    mock_db_payment.create.return_value = fake_payment_obj

    mock_db_payment_user = AsyncMock()
    mock_db_payment_user.create.return_value = True

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ), patch("app.routers.payment_router.get_current_user", mock_current):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/payment/", json=payment_payload)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_payment_fail_create(payment_payload=None):
    # db_payment.create -> None => 400
    mock_db_payment = AsyncMock()
    mock_db_payment.create.return_value = None

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/payment/", json={"amount": 1.23})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_payment_fail_user_relation(fake_payment_obj):
    mock_db_payment = AsyncMock()
    mock_db_payment.create.return_value = fake_payment_obj
    mock_db_payment.delete.return_value = None

    mock_db_payment_user = AsyncMock()
    mock_db_payment_user.create.return_value = False

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ), patch("app.routers.payment_router.get_current_user", mock_current):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/payment/", json={"amount": 1.23})

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_payments_success():
    su_user = type("U", (), {"user_email": "admin@example.com"})
    mock_get_current = AsyncMock(return_value=su_user)

    fake_list = [{"payment_id": "1"}, {"payment_id": "2"}]
    mock_db_payment = AsyncMock()
    mock_db_payment.get_all.return_value = fake_list

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_get_current), patch(
        "app.routers.payment_router.db_payment", mock_db_payment
    ), patch("app.routers.payment_router.settings") as mock_settings:
        mock_settings.SU = "admin@example.com"

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_payments_permission_denied():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "not_admin@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.settings"
    ) as mock_settings:
        mock_settings.SU = "admin@example.com"

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_payment_by_id_found(fake_payment_obj):
    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = fake_payment_obj

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/payment/id/{fake_payment_obj.payment_id}")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_payment_by_id_not_found():
    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = None

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/payment/id/{uuid.uuid4()}")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_empty():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    mock_db_payment_user.get_by_user.return_value = []

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/email/user@example.com/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_some(fake_payment_obj):
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    # возвращаем список записей с payment_id атрибутом
    rec = type("R", (), {"payment_id": fake_payment_obj.payment_id})
    mock_db_payment_user.get_by_user.return_value = [rec]

    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = fake_payment_obj

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ), patch("app.routers.payment_router.db_payment", mock_db_payment):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/email/user@example.com/all")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_by_status_no_payments():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    mock_db_payment_user.get_by_user.return_value = []

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/payment/email/user@example.com/Создан")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_by_status_some(fake_payment_obj):
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    rec = type("R", (), {"payment_id": fake_payment_obj.payment_id})
    mock_db_payment_user.get_by_user.return_value = [rec]

    mock_db_payment = AsyncMock()
    mock_db_payment.get_by_status.return_value = fake_payment_obj

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ), patch("app.routers.payment_router.db_payment", mock_db_payment):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get(f"/payment/email/user@example.com/Создан")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_by_amount_no_payments():
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    mock_db_payment_user.get_by_user.return_value = []

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/email/user@example.com/1.23")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_payments_by_amount_some(fake_payment_obj):
    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )
    mock_db_payment_user = AsyncMock()
    rec = type("R", (), {"payment_id": fake_payment_obj.payment_id})
    mock_db_payment_user.get_by_user.return_value = [rec]

    mock_db_payment = AsyncMock()
    mock_db_payment.get_by_amount.return_value = fake_payment_obj

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.get_current_user", mock_current), patch(
        "app.routers.payment_router.db_payment_user", mock_db_payment_user
    ), patch("app.routers.payment_router.db_payment", mock_db_payment):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/payment/email/user@example.com/1.23")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_payment_status_not_found():
    pid = uuid.uuid4()
    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = None

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(f"/payment/{pid}?status=CREATED")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_payment_status_complete_state(fake_payment_obj):
    mock_db_payment = AsyncMock()
    fake_payment_obj.status = "Оплачен"
    mock_db_payment.get.return_value = fake_payment_obj

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(
                f"/payment/{fake_payment_obj.payment_id}?status=CREATED"
            )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_payment_status_success(fake_payment_obj):
    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = fake_payment_obj
    mock_db_payment.update.return_value = None

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(
                f"/payment/{fake_payment_obj.payment_id}?status=CREATED"
            )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_payment_status_update_raises(fake_payment_obj):
    mock_db_payment = AsyncMock()
    mock_db_payment.get.return_value = fake_payment_obj
    mock_db_payment.update.side_effect = Exception("boom")

    mock_current = AsyncMock(
        return_value=type("U", (), {"user_email": "user@example.com"})
    )

    transport = ASGITransport(app=app)
    with patch("app.routers.payment_router.db_payment", mock_db_payment), patch(
        "app.routers.payment_router.get_current_user", mock_current
    ):

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.put(
                f"/payment/{fake_payment_obj.payment_id}?status=CREATED"
            )

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in resp.json()["detail"]
