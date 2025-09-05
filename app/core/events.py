from app.core.db.db_sessions import db


async def on_startup():
    await db.setup_database()


async def on_shutdown():
    await db.engine.dispose()
