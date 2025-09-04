import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import settings
from app.core.db_sessions import db
from app.routers.auth_router import router as auth_router

app = FastAPI()

# cors перенести
origins = [
    settings.BASE_URL_1,
    settings.BASE_URL_2,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.on_event("startup")
async def on_startup():
    await db.setup_database()


@app.on_event("shutdown")
async def on_shutdown():
    await db.engine.dispose()


#
# async def main():
#      await db.setup_database()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # asyncio.run(main())
    # uvicorn.run("main:app", reload=True)
