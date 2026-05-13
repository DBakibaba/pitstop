from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db,seed_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message":"Pitstop API is running "}