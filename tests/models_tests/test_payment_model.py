from sqlalchemy import Numeric, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.models.payment_model import PaymentModel


def test_payment_model_columns_and_types_and_defaults():
    mapper = PaymentModel.__mapper__
    cols = {c.key: c for c in mapper.columns}

    expected = [
        "payment_id",
        "card_number",
        "first_name",
        "last_name",
        "second_name",
        "amount",
        "creation_time",
        "status",
    ]
    for name in expected:
        assert name in cols

    assert isinstance(cols["payment_id"].type, UUID)
    assert cols["card_number"].type.length == 4
    assert isinstance(cols["amount"].type, Numeric)
    assert cols["amount"].type.precision == 12
    assert cols["amount"].type.scale == 3
    assert isinstance(cols["creation_time"].type, DateTime)
    assert isinstance(cols["status"].type, Enum)
