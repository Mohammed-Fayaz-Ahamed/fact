# Configuration

FACT uses the `FactConfig` class to centralize all runtime configuration.

Configuration values can be supplied programmatically or loaded from environment variables using `FactConfig.from_env()`.

---

# Creating a Configuration

Configuration can be created directly:

```python
from fact_core.config import FactConfig

config = FactConfig(
    storage_backend="clickhouse",
)
```

or loaded from environment variables:

```python
config = FactConfig.from_env()
```

---

# Configuration Reference

| Property                 | Description                                               | Default                              |
| ------------------------ | --------------------------------------------------------- | ------------------------------------ |
| `storage_backend`        | Storage backend to use (`noop`, `postgres`, `clickhouse`) | `clickhouse`                         |
| `batch_size`             | Maximum records written in a single batch                 | Backend specific                     |
| `flush_interval_seconds` | Maximum delay before flushing a partial batch             | `3.0`                                |
| `max_retries`            | Maximum storage retry attempts                            | `5`                                  |
| `base_retry_delay`       | Initial retry delay in seconds                            | `1`                                  |
| `dlq_path`               | Dead Letter Queue file location                           | `failed_batches/telemetry_dlq.jsonl` |
| `postgres_dsn`           | PostgreSQL connection string                              | —                                    |
| `clickhouse_host`        | ClickHouse server hostname                                | `127.0.0.1`                          |
| `clickhouse_port`        | ClickHouse HTTP port                                      | `8123`                               |
| `clickhouse_username`    | ClickHouse username                                       | `default`                            |
| `clickhouse_password`    | ClickHouse password                                       | Empty                                |
| `clickhouse_database`    | ClickHouse database                                       | `default`                            |

---

# Environment Variables

FACT supports loading configuration from environment variables.

Example:

```bash
export FACT_STORAGE_BACKEND=clickhouse
export FACT_BATCH_SIZE=5000
export FACT_FLUSH_INTERVAL_SECONDS=3
export FACT_MAX_RETRIES=5
export FACT_BASE_RETRY_DELAY=1

export FACT_POSTGRES_DSN=postgresql://user:password@localhost:5432/postgres

export FACT_CLICKHOUSE_HOST=127.0.0.1
export FACT_CLICKHOUSE_PORT=8123
export FACT_CLICKHOUSE_USERNAME=default
export FACT_CLICKHOUSE_PASSWORD=
export FACT_CLICKHOUSE_DATABASE=default
```

---

# Storage Backend Selection

The storage backend is selected using:

```python
config.storage_backend
```

Supported values are:

* `noop`
* `postgres`
* `clickhouse`

---

# Example Configurations

## NoOp

```python
config = FactConfig(
    storage_backend="noop",
)
```

Recommended for:

* Unit testing
* Middleware benchmarking
* Performance profiling

---

## PostgreSQL

```python
config = FactConfig(
    storage_backend="postgres",
    postgres_dsn="postgresql://user:password@localhost:5432/postgres",
)
```

Recommended for:

* Operational telemetry
* Smaller deployments
* Relational storage requirements

---

## ClickHouse

```python
config = FactConfig(
    storage_backend="clickhouse",
)
```

Recommended for:

* High-throughput telemetry
* Analytics workloads
* Large-scale deployments

---

# Best Practices

* Keep retry settings at their defaults unless required.
* Use larger batch sizes for ClickHouse deployments.
* Use smaller batch sizes for PostgreSQL deployments.
* Store credentials using environment variables rather than hardcoding them.
* Use the NoOp backend for benchmark comparisons that exclude storage overhead.
