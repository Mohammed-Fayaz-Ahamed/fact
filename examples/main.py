import os
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fact_core.storage import TelemetryWriterFactory
from fact_core.middleware import ClickHouseTelemetryMiddleware

ENGINE_TYPE = os.getenv("FACT_STORAGE_BACKEND", "clickhouse")

CONFIG_MAP = {
    "host": "127.0.0.1",
    "port": 8123,
    "batch_size": 5000 if ENGINE_TYPE == "clickhouse" else 100,
    "flush_interval_seconds": 3.0,
    "dsn": "postgresql://postgres:postgres@localhost:5432/postgres"
}
writer = TelemetryWriterFactory.create_writer(ENGINE_TYPE, CONFIG_MAP)
@asynccontextmanager
async def lifespan(app: FastAPI):
    writer.start()
    yield
    await writer.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(ClickHouseTelemetryMiddleware, writer=writer)

@app.get("/")
async def root():
    return {"message": f"FACT telemetry processing active running on: {ENGINE_TYPE.upper()}"}


@app.get("/slow")
async def slow_route():
    await asyncio.sleep(0.4)
    return {"status": "delayed"}

@app.get("/error")
async def error_route():
    raise ValueError("Simulated backend database error connection loss.")