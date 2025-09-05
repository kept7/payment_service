from app.models.auth_model import AuthModel


def test_auth_model_columns_exist_and_types():
    mapper = AuthModel.__mapper__
    cols = {c.key: c for c in mapper.columns}

    for name in ("id", "first_name", "last_name", "user_email", "user_password_hash"):
        assert name in cols

    assert cols["id"].primary_key is True
    assert cols["first_name"].type.length == 32
    assert cols["last_name"].type.length == 64
    assert cols["user_email"].type.length == 255
    assert cols["user_password_hash"].type.length == 128
