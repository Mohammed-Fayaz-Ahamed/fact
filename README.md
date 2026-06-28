# FACT
[![PyPI version](https://img.shields.io/pypi/v/fact-telemetry.svg)](https://pypi.org/project/fact-telemetry/)
[![Python Versions](https://img.shields.io/pypi/pyversions/fact-telemetry.svg)](https://pypi.org/project/fact-telemetry/)
[![License](https://img.shields.io/pypi/l/fact-telemetry.svg)](LICENSE)
[![CI](https://github.com/Mohammed-Fayaz-Ahamed/fact/actions/workflows/ci.yml/badge.svg)](https://github.com/Mohammed-Fayaz-Ahamed/fact/actions/workflows/ci.yml)


**FACT (FastAPI Advanced Collection Telemetry)** is a lightweight, asynchronous telemetry framework for FastAPI applications.

FACT captures request telemetry through middleware, validates telemetry records, buffers them in an asynchronous in-memory queue, and persists them to configurable storage backends using batched writes. The framework is designed to minimize request overhead while providing reliable telemetry collection through retry mechanisms, dead-letter queue (DLQ) support, and runtime metrics.

FACT currently supports PostgreSQL and ClickHouse storage backends and provides a configurable architecture suitable for high-throughput, multi-tenant applications.

> **Status:** Alpha Development

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
