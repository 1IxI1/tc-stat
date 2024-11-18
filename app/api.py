from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from app.database import get_toggles, init_db


class Record(BaseModel):
    method: str
    toggled_at: int
    success: bool
    latency_ms: int
    data_lag_sec: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/toggles/")
async def get_all_toggles():
    return await get_toggles()

async def api_worker():
    config = uvicorn.Config("app.api:app", host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
