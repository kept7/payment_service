import uvicorn

from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)