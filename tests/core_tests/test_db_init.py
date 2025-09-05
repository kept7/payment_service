import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


@pytest.mark.asyncio
async def test_db_init_engine_and_session_created():
    # Подмена модуля конфигурации до импорта app.core.db.db_init
    fake_settings = MagicMock(
        DB_USER_NAME="user1", DB_USER_PASS="pass1", DB_HOST="host1"
    )
    cfg_module_name = "app.utils.config"
    fake_cfg = ModuleType(cfg_module_name)
    fake_cfg.settings = fake_settings
    sys.modules[cfg_module_name] = fake_cfg

    # Теперь импортируем тестируемый модуль после подмены конфига
    with patch("app.core.db.db_init.create_async_engine") as mock_create_engine, patch(
        "app.core.db.db_init.async_sessionmaker"
    ) as mock_async_sessionmaker, patch("app.core.db.db_init.settings", fake_settings):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker = MagicMock()
        mock_async_sessionmaker.return_value = mock_sessionmaker

        from app.core.db.db_init import DB  # импорт после подмены

        db = DB("somedb")

        mock_create_engine.assert_called_once()
        called_dsn = mock_create_engine.call_args[0][0]
        assert "user1" in called_dsn
        assert "pass1" in called_dsn
        assert "host1" in called_dsn
        assert "somedb" in called_dsn

        assert db.engine is mock_engine
        assert db.session is mock_sessionmaker


@pytest.mark.asyncio
async def test_setup_and_drop_database_call_metadata():
    # Подмена конфигурации и Base модуля до импорта db_init
    fake_settings = MagicMock(DB_USER_NAME="u", DB_USER_PASS="p", DB_HOST="h")
    cfg_module_name = "app.utils.config"
    fake_cfg = ModuleType(cfg_module_name)
    fake_cfg.settings = fake_settings
    sys.modules[cfg_module_name] = fake_cfg

    base_module_name = "app.models.auth_model"
    fake_base_mod = ModuleType(base_module_name)
    fake_base = MagicMock()
    fake_base.metadata = MagicMock()
    fake_base_mod.Base = fake_base
    sys.modules[base_module_name] = fake_base_mod

    # Патчим create_async_engine и async_sessionmaker внутри модуля db_init,
    # и также подменяем settings внутри модуля db_init чтобы точно использовать fake_settings
    with patch("app.core.db.db_init.create_async_engine") as mock_create_engine, patch(
        "app.core.db.db_init.async_sessionmaker"
    ), patch("app.core.db.db_init.settings", fake_settings):
        mock_engine = MagicMock()
        async_ctx = AsyncMock()
        conn = MagicMock()
        conn.run_sync = AsyncMock(return_value=None)
        async_ctx.__aenter__.return_value = conn
        mock_engine.begin.return_value = async_ctx
        mock_create_engine.return_value = mock_engine

        from app.core.db.db_init import DB

        db = DB("dbx")

        await db.setup_database()
        conn.run_sync.assert_awaited_once()
        first_arg = conn.run_sync.await_args[0][0]
        assert callable(first_arg)

        conn.run_sync.reset_mock()
        await db.drop_database()
        conn.run_sync.assert_awaited_once()
        first_arg = conn.run_sync.await_args[0][0]
        assert callable(first_arg)
