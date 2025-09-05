import pytest

from app.schemas.validation_funcs import (
    must_be_valid_name,
    must_be_four_digit_int,
)


@pytest.mark.parametrize(
    "input_val,expected",
    [
        (1234, "1234"),
        ("5678", "5678"),
    ],
)
def test_must_be_four_digit_int_valid(input_val, expected):
    assert must_be_four_digit_int(input_val) == expected


@pytest.mark.parametrize(
    "input_val",
    [
        "12a4",
        12.34,
        "",
        "abcd",
    ],
)
def test_must_be_four_digit_int_invalid(input_val):
    with pytest.raises(ValueError):
        must_be_four_digit_int(input_val)


def test_must_be_valid_name_none():
    assert must_be_valid_name(None, "User") is None


def test_must_be_valid_name_user_accepts_nonlatin_and_must_contain_letter():
    assert must_be_valid_name("Иван", "User") == "Иван"
    assert must_be_valid_name("123A", "User") == "123A"


@pytest.mark.parametrize("bad_val", ["", "1234", "----"])
def test_must_be_valid_name_user_rejects_empty_or_no_letters(bad_val):
    with pytest.raises(ValueError):
        must_be_valid_name(bad_val, "User")


def test_must_be_valid_name_payment_rules_accepts_upper_latin():
    assert must_be_valid_name("ABC-DEF", "Payment") == "ABC-DEF"


@pytest.mark.parametrize(
    "bad_val",
    [
        "abc-def",
        "Имя",
        "1234",
        "",
    ],
)
def test_must_be_valid_name_payment_rejects_invalid(bad_val):
    with pytest.raises(ValueError):
        must_be_valid_name(bad_val, "Payment")
