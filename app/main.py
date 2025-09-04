# import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import settings


app = FastAPI()

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

# async def main():
#     await db.setup_database()

if __name__ == "__main__":
    # asyncio.run(main())
    uvicorn.run("main:app", reload=True)