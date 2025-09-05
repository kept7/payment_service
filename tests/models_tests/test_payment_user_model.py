import uuid

from decimal import Decimal

from app.models.auth_model import AuthModel
from app.models.payment_model import PaymentModel
from app.models.payment_user_model import PaymentUserModel


def test_payment_user_model_foreign_key_and_columns():
    mapper = PaymentUserModel.__mapper__
    cols = {c.key: c for c in mapper.columns}

    assert "user_email" in cols
    assert "payment_id" in cols

    fk_list = list(cols["payment_id"].foreign_keys)
    assert len(fk_list) == 1
    fk = fk_list[0]
    assert "payment.payment_id" in str(fk.target_fullname)


def test_model_instantiation_without_db():
    a = AuthModel()
    p = PaymentModel()
    pu = PaymentUserModel()

    a.first_name = "John"
    a.last_name = "Doe"
    a.user_email = "x@y.z"
    a.user_password_hash = "hash"

    p.card_number = "1234"
    p.first_name = "JOHN"
    p.last_name = "DOE"
    p.amount = Decimal("1.000")

    pu.user_email = "x@y.z"
    pu.payment_id = uuid.uuid4()

    assert a.first_name == "John"
    assert p.amount == Decimal("1.000")
    assert isinstance(pu.payment_id, uuid.UUID)
