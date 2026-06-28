
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
