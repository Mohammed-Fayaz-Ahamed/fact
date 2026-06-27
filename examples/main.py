import os
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fact_core.storage import PostgresBatchWriter
from fact_core.middleware import ClickHouseTelemetryMiddleware

# Update this connection string to match your local PostgreSQL configuration
POSTGRES_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

# Initialize the batching engine (Flush every 10 records or 3 seconds)
writer = PostgresBatchWriter(dsn=POSTGRES_DSN, batch_size=10, flush_interval_seconds=3.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the async background queue worker when FastAPI launches
    writer.start()
    yield
    # Safely flush remaining memory items to the database on application shutdown
    await writer.stop()

app = FastAPI(lifespan=lifespan)

# Register FACT as a global application middleware
app.add_middleware(ClickHouseTelemetryMiddleware, writer=writer)

@app.get("/")
async def root():
    return {"message": "FACT telemetry logging is active!"}

@app.get("/slow")
async def slow_route():
    # Simulate an endpoint with high execution or database latency
    await asyncio.sleep(0.4)
    return {"status": "delayed"}

@app.get("/error")
async def error_route():
    # Simulate an unexpected critical runtime failure
    raise ValueError("Simulated backend database error connection loss.")
