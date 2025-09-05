import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.payment_schema import PaymentSchema


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (1234, "1234"),
        ("5678", "5678"),
    ],
)
def test_card_number_accepts_int_and_str(input_val, expected):
    obj = PaymentSchema(
        card_number=input_val,
        last_name="ABC",
        first_name="DEF",
        amount=Decimal("1.000"),
    )
    assert obj.card_number == expected


@pytest.mark.parametrize("bad_val", ["12a4", "abcd", "", "12 34"])
def test_card_number_rejects_invalid(bad_val):
    with pytest.raises(ValidationError):
        PaymentSchema(
            card_number=bad_val,
            last_name="ABC",
            first_name="DEF",
            amount=Decimal("1.000"),
        )


def test_names_accept_valid_payment_names():
    obj = PaymentSchema(
        card_number="0000",
        last_name="SMITH",
        first_name="JOHN",
        second_name="DOE",
        amount=Decimal("10.5"),
    )
    assert obj.last_name == "SMITH"
    assert obj.first_name == "JOHN"
    assert obj.second_name == "DOE"


@pytest.mark.parametrize("bad_name", ["Имя", "Smith", "1234", "", "----"])
def test_names_reject_invalid_payment_names(bad_name):
    with pytest.raises(ValidationError):
        PaymentSchema(
            card_number="0000",
            last_name=bad_name,
            first_name="JOHN",
            amount=Decimal("1.000"),
        )


@pytest.mark.parametrize("val", ["0", "0.000", Decimal("0"), Decimal("0.000")])
def test_amount_must_be_greater_than_zero(val):
    with pytest.raises(ValidationError):
        PaymentSchema(
            card_number="0000",
            last_name="ABC",
            first_name="DEF",
            amount=val,
        )


def test_amount_accepts_valid_decimal_and_precision():
    obj = PaymentSchema(
        card_number="0000",
        last_name="ABC",
        first_name="DEF",
        amount=Decimal("123456789.123"),
    )
    assert obj.amount == Decimal("123456789.123")


def test_amount_rejects_too_many_decimal_places():
    with pytest.raises(ValidationError):
        PaymentSchema(
            card_number="0000",
            last_name="ABC",
            first_name="DEF",
            amount=Decimal("1.0005"),
        )
