import asyncio
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fact_core.storage import TelemetryWriterFactory
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.config import FactConfig

config = FactConfig.from_env()

writer = TelemetryWriterFactory.create_writer(config)
@asynccontextmanager
async def lifespan(app: FastAPI):
    writer.start()
    yield
    await writer.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(ClickHouseTelemetryMiddleware, writer=writer)

@app.get("/")
async def root():
    return {
        "message": (
            f"FACT telemetry processing active running on: "
            f"{config.storage_backend.upper()}"
        )
    }

@app.get("/slow")
async def slow_route():
    await asyncio.sleep(0.4)
    return {"status": "delayed"}

@app.get("/error")
async def error_route():
    raise ValueError("Simulated backend database error connection loss.")


@app.get("/checkout")
async def checkout_endpoint(request: Request, items: int = 1):
    # Attaching runtime metadata tracking variables directly to request state
    request.state.fact_metadata = {
        "user_tier": "premium",
        "cart_items": str(items),
        "experiment_group": "variant_b"
    }
    return {"status": "success", "processed_items": items}