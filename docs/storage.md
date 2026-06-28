# Storage Backends

FACT separates telemetry collection from telemetry persistence through a storage abstraction.

The middleware never writes directly to a database. Instead, telemetry records are processed by a background batch worker and written through a configurable storage backend.

This design allows FACT to support multiple storage engines without changing the middleware implementation.

---

# Storage Architecture

```text
HTTP Request
      │
      ▼
Telemetry Middleware
      │
      ▼
Async Queue
      │
      ▼
Batch Worker
      │
      ▼
TelemetryWriterFactory
      │
      ├──────────────┬──────────────┐
      ▼              ▼              ▼
 NoOp Writer   PostgreSQL Writer   ClickHouse Writer
```

The `TelemetryWriterFactory` creates the appropriate writer based on the configured storage backend.

---

# Supported Backends

## NoOp

The NoOp writer accepts telemetry records but intentionally discards them.

No database operations are performed.

### Recommended Use Cases

* Unit testing
* Middleware benchmarking
* Performance profiling
* Framework development

Configuration:

```python
config = FactConfig(
    storage_backend="noop",
)
```

---

## PostgreSQL

The PostgreSQL writer stores telemetry records in a relational database using batched inserts.

### Characteristics

* Transactional writes
* Relational schema
* Suitable for operational telemetry
* Simple deployment

Configuration:

```python
config = FactConfig(
    storage_backend="postgres",
    postgres_dsn="postgresql://user:password@localhost:5432/postgres",
)
```

---

## ClickHouse

The ClickHouse writer stores telemetry records in a column-oriented database optimized for analytical workloads.

### Characteristics

* High ingestion throughput
* Efficient analytical queries
* Optimized for large telemetry datasets
* Batch-oriented inserts

Configuration:

```python
config = FactConfig(
    storage_backend="clickhouse",
)
```

---

# Storage Selection

FACT selects the storage backend using:

```python
config.storage_backend
```

Supported values:

* `noop`
* `postgres`
* `clickhouse`

---

# Batch Processing

Regardless of the selected backend, telemetry records are processed using the same batching pipeline.

Batch processing is controlled through:

* `batch_size`
* `flush_interval_seconds`

This ensures consistent behavior across all storage implementations.

---

# Retry Behavior

If a storage write fails:

1. FACT retries the operation using exponential backoff.
2. The retry count is configurable.
3. Permanently failed batches are written to the Dead Letter Queue (DLQ).

This behavior is shared by all storage backends.

---

# Extending FACT

New storage backends can be added by implementing the `BaseTelemetryWriter` interface.

A custom writer is responsible for:

* Accepting telemetry batches.
* Persisting records to the target system.
* Implementing storage-specific write logic.

The batching, retry mechanism, metrics, and Dead Letter Queue are provided by the framework and do not need to be reimplemented.

---

# Choosing a Backend

| Backend    | Recommended For                                |
| ---------- | ---------------------------------------------- |
| NoOp       | Testing and performance benchmarking           |
| PostgreSQL | Operational telemetry and moderate workloads   |
| ClickHouse | High-volume telemetry and analytical workloads |

The appropriate backend depends on the application's workload, operational requirements, and analytics needs.
