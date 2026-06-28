# Quick Start

This guide demonstrates how to integrate FACT into a FastAPI application in just a few steps.

---

## 1. Import FACT Components

```python
from fastapi import FastAPI

from fact_core.config import FactConfig
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.storage import TelemetryWriterFactory
```

---

## 2. Create a Configuration

FACT uses `FactConfig` as the central configuration object.

```python
config = FactConfig.from_env()
```

Configuration can be provided programmatically or through environment variables.

---

## 3. Create the Telemetry Writer

```python
writer = TelemetryWriterFactory.create_writer(config)
```

The writer manages asynchronous batching, retries, dead-letter queue handling, and persistence.

---

## 4. Start and Stop the Background Worker

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    writer.start()
    yield
    await writer.stop()
```

---

## 5. Register the Middleware

```python
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    ClickHouseTelemetryMiddleware,
    writer=writer,
)
```

Once registered, telemetry is collected automatically for every incoming request.

---

## 6. Run the Application

```bash
uvicorn examples.main:app --workers 4
```

---

## 7. Verify the Installation

Open your browser or use curl:

```bash
curl http://127.0.0.1:8000/
```

A successful response confirms that FACT is running.

---

## What Happens Automatically?

For every request, FACT performs the following steps:

1. Captures request telemetry.
2. Validates the telemetry payload.
3. Places the record into an asynchronous queue.
4. Groups records into batches.
5. Persists batches to the configured storage backend.
6. Retries failed writes using exponential backoff.
7. Writes permanently failed batches to the Dead Letter Queue (DLQ).

No changes to your application endpoints are required.

---

## Next Steps

Continue with the following guides:

* Architecture
* Configuration
* Middleware
* Storage Backends
* Benchmarking
