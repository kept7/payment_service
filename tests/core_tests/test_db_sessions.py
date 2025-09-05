import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock
import pytest


def test_db_sessions_initializes_repositories(monkeypatch):
    cfg_mod = ModuleType("app.utils.config")
    cfg_mod.settings = MagicMock(DB_NAME="the_db")
    sys.modules["app.utils.config"] = cfg_mod

    db_init_mod = ModuleType("app.core.db.db_init")

    class FakeDB:
        def __init__(self, db_name):
            self.session = "SESSION_OBJ"
            self.db_name = db_name

    db_init_mod.DB = FakeDB
    sys.modules["app.core.db.db_init"] = db_init_mod

    auth_mod = ModuleType("app.core.db.operations.db_auth_opers")
    payment_mod = ModuleType("app.core.db.operations.db_payment_opers")
    paym_user_mod = ModuleType("app.core.db.operations.db_paym_user_opers")

    fake_auth_repo = MagicMock()
    fake_payment_repo = MagicMock()
    fake_payment_user_repo = MagicMock()

    auth_mod.DBAuthRepository = lambda session: fake_auth_repo
    payment_mod.DBPaymentRepository = lambda session: fake_payment_repo
    paym_user_mod.DBPaymentUserRepository = lambda session: fake_payment_user_repo

    sys.modules["app.core.db.operations.db_auth_opers"] = auth_mod
    sys.modules["app.core.db.operations.db_payment_opers"] = payment_mod
    sys.modules["app.core.db.operations.db_paym_user_opers"] = paym_user_mod

    sys.modules.pop("app.core.db.db_sessions", None)

    mod = importlib.import_module("app.core.db.db_sessions")

    assert isinstance(mod.db, FakeDB)
    assert mod.db.db_name == "the_db"

    assert mod.db_auth is fake_auth_repo
    assert mod.db_payment is fake_payment_repo
    assert mod.db_payment_user is fake_payment_user_repo
