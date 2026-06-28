
<h1 align="center">FACT</h1>

<p align="center">
High-performance asynchronous telemetry for FastAPI.
</p>

<p align="center">

[![PyPI version](https://img.shields.io/pypi/v/fact-telemetry.svg)](https://pypi.org/project/fact-telemetry/)
[![Python Versions](https://img.shields.io/pypi/pyversions/fact-telemetry.svg)](https://pypi.org/project/fact-telemetry/)
[![License](https://img.shields.io/pypi/l/fact-telemetry.svg)](LICENSE)
[![CI](https://github.com/Mohammed-Fayaz-Ahamed/fact/actions/workflows/ci.yml/badge.svg)](https://github.com/Mohammed-Fayaz-Ahamed/fact/actions/workflows/ci.yml)

</p>

---

**FACT (FastAPI Advanced Collection Telemetry)** is a lightweight, asynchronous telemetry framework for FastAPI applications.

FACT captures request telemetry through middleware, validates telemetry records, buffers them in an asynchronous in-memory queue, and persists them to configurable storage backends using batched writes. The framework is designed to minimize request overhead while providing reliable telemetry collection through retry mechanisms, dead-letter queue (DLQ) support, and runtime metrics.

FACT currently supports PostgreSQL and ClickHouse storage backends and provides a configurable architecture suitable for high-throughput, multi-tenant applications.

> **Status:** Alpha Development

---

## Why FACT?

FACT was built to provide a simple and reliable telemetry pipeline for FastAPI applications.

Its design focuses on minimizing request overhead while ensuring telemetry is collected reliably through asynchronous processing and configurable storage backends.

Key design goals include:

* **Asynchronous by design** – Telemetry is processed in the background instead of blocking request handling.
* **Reliable delivery** – Automatic retries with exponential backoff help recover from transient failures.
* **Failure resilience** – Events that cannot be persisted are stored in a Dead Letter Queue (DLQ) for later inspection.
* **Storage flexibility** – Multiple storage backends can be used without changing application code.
* **Operational visibility** – Runtime metrics provide insight into queue health and processing performance.
* **Developer-friendly** – Simple configuration and middleware integration make adoption straightforward.


---

# Quick Start

FACT supports two configuration approaches:

* **Option 1 (Recommended): Environment Variables** – Best for production deployments.
* **Option 2: Programmatic Configuration** – Useful for local development, testing, and experimentation.

---

## Option 1 — Environment Variables (Recommended)

### Project Structure

```text
my-fastapi-app/
├── .env
├── main.py
├── requirements.txt
└── ...
```

### Step 1 — Install FACT

```bash
pip install fact-telemetry
```

### Step 2 — Configure FACT

Create a `.env` file in the project root.

```env
FACT_STORAGE_BACKEND=clickhouse

FACT_CLICKHOUSE_HOST=127.0.0.1
FACT_CLICKHOUSE_PORT=8123
FACT_CLICKHOUSE_USERNAME=default
FACT_CLICKHOUSE_PASSWORD=
FACT_CLICKHOUSE_DATABASE=default

FACT_BATCH_SIZE=5000
FACT_FLUSH_INTERVAL=3.0

FACT_MAX_RETRIES=5
FACT_BASE_RETRY_DELAY=1.0

FACT_DLQ_PATH=failed_batches/telemetry_dlq.jsonl

FACT_LOG_LEVEL=INFO
```

### Step 3 — Enable FACT

Open your `main.py`.

```python
import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI

from fact_core.config import FactConfig
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.storage import TelemetryWriterFactory

config = FactConfig.from_env()

writer = TelemetryWriterFactory.create_writer(config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    writer.start()
    yield
    await writer.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    ClickHouseTelemetryMiddleware,
    writer=writer,
)
```

Your existing endpoints remain unchanged.

```python
@app.get("/")
async def root():
    return {"message": "Hello FACT"}
```

Run your application.

```bash
uvicorn main:app --reload
```

FACT now automatically captures, validates, batches, retries, and persists telemetry for every incoming request.

---

## Option 2 — Programmatic Configuration

This approach is useful for local development, testing, or environments where configuration is managed directly in code.

### Project Structure

```text
my-fastapi-app/
├── main.py
├── requirements.txt
└── ...
```

### Step 1 — Install FACT

```bash
pip install fact-telemetry
```

### Step 2 — Configure FACT

Open your `main.py`.

```python
import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI

from fact_core.config import FactConfig
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.storage import TelemetryWriterFactory

config = FactConfig(
    storage_backend="clickhouse",
    clickhouse_host="127.0.0.1",
    clickhouse_port=8123,
    clickhouse_username="default",
    clickhouse_password="",
    clickhouse_database="default",
    batch_size=5000,
    flush_interval_seconds=3.0,
    max_retries=5,
    base_retry_delay=1.0,
    dlq_path="failed_batches/telemetry_dlq.jsonl",
    log_level="INFO",
)

writer = TelemetryWriterFactory.create_writer(config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    writer.start()
    yield
    await writer.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    ClickHouseTelemetryMiddleware,
    writer=writer,
)
```

Your existing API endpoints do not require any modifications.

```python
@app.get("/")
async def root():
    return {"message": "Hello FACT"}
```

Start the application.

```bash
uvicorn main:app --reload
```

Telemetry will now be collected automatically for every incoming request.

---
## What happens next?

Once FACT is enabled:

1. Every incoming request passes through the telemetry middleware.
2. FACT validates the telemetry record.
3. The record is placed into an asynchronous in-memory queue.
4. Background workers batch telemetry records.
5. Successful batches are written to the configured storage backend.
6. Failed batches are retried automatically.
7. Unrecoverable batches are written to the Dead Letter Queue (DLQ).

---
## Features

- Middleware-based automatic telemetry collection
- Asynchronous in-memory queue
- Configurable batch processing
- PostgreSQL storage backend
- ClickHouse storage backend
- Multi-tenant request support
- Dynamic metadata support
- Payload validation
- Exponential backoff retry mechanism
- Local file-based Dead Letter Queue (DLQ)
- Runtime telemetry metrics
- Centralized configuration using `FactConfig`
- Environment variable support
- Automated test suite
- Benchmark and soak testing utilities

---

## Architecture

```text
                Incoming Request
                       │
                       ▼
        ClickHouseTelemetryMiddleware
                       │
                       ▼
            Payload Validation
                       │
                       ▼
           Async In-Memory Queue
                       │
                       ▼
              Batch Collection
                       │
                       ▼
           Retry with Backoff
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Storage Backend        Dead Letter Queue
             │
             ▼
 PostgreSQL / ClickHouse
```

FACT separates request processing from persistence by using an asynchronous producer-consumer architecture. Incoming requests enqueue telemetry records immediately, while a background worker batches and persists records independently. This minimizes request latency and provides resilience during temporary storage failures.

---

## Documentation

Detailed documentation is available in the `docs/` directory.

- Installation
- Quick Start
- Architecture
- Configuration
- Storage Backends
- Middleware
- Benchmarking
- Roadmap

---

## Project Status

FACT is currently in **Alpha Development**.

Implemented capabilities include:

- Middleware-based telemetry ingestion
- Batch processing engine
- PostgreSQL backend
- ClickHouse backend
- Retry with exponential backoff
- Dead Letter Queue (DLQ)
- Payload validation
- Runtime metrics
- Benchmarking utilities
- Automated tests

---

## License

This project is licensed under the Apache License 2.0.

See the [LICENSE](LICENSE) file for details.
