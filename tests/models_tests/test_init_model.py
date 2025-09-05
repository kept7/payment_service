import inspect

from sqlalchemy import Integer, String, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.models.init_model import (
    int_pk,
    str_4,
    str_32,
    str_64,
    email_str_unique,
    email_str,
    hash_str,
    uuid_pk,
    dec,
    timestamp,
    payment_status,
    Base,
)


def get_mapped_type(mapped_annotation):
    meta = getattr(mapped_annotation, "__metadata__", None)
    if not meta:
        return None
    mcol = meta[0]
    col = None
    if hasattr(mcol, "column"):
        col = getattr(mcol, "column")
    elif hasattr(mcol, "_col"):
        col = getattr(mcol, "_col")

    if col is not None:
        return getattr(col, "type", None)

    return getattr(mcol, "type", None)


def test_base_is_declarative_base():
    assert inspect.isclass(Base)
    assert hasattr(Base, "metadata")


def test_int_pk_annotation_has_integer_primary_key():
    col_type = get_mapped_type(int_pk)
    assert isinstance(col_type, Integer)


def test_string_annotations_have_expected_lengths():
    ct = get_mapped_type(str_4)
    assert isinstance(ct, String)
    assert ct.length == 4

    ct = get_mapped_type(str_32)
    assert isinstance(ct, String)
    assert ct.length == 32

    ct = get_mapped_type(str_64)
    assert isinstance(ct, String)
    assert ct.length == 64


def test_email_and_hash_annotations():
    ct = get_mapped_type(email_str_unique)
    assert isinstance(ct, String)
    assert ct.length == 255

    ct = get_mapped_type(email_str)
    assert isinstance(ct, String)
    assert ct.length == 255

    ct = get_mapped_type(hash_str)
    assert isinstance(ct, String)
    assert ct.length == 128


def test_uuid_pk_and_decimal_and_timestamp_and_enum_types():
    ct = get_mapped_type(uuid_pk)
    assert isinstance(ct, UUID)

    ct = get_mapped_type(dec)
    assert isinstance(ct, Numeric)
    assert ct.precision == 12
    assert ct.scale == 3

    ct = get_mapped_type(timestamp)
    assert isinstance(ct, DateTime)

    ct = get_mapped_type(payment_status)
    assert isinstance(ct, Enum)
