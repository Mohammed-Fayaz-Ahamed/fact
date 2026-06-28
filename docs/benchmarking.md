# Benchmarking

FACT includes a benchmarking utility for evaluating the performance of the telemetry pipeline under configurable workloads.

The benchmark measures middleware performance, asynchronous queue behavior, batching efficiency, and storage backend throughput.

---

# Running the Benchmark

Start the example application.

Example:

```bash
FACT_STORAGE_BACKEND=noop uvicorn examples.main:app --workers 4
```

In another terminal execute:

```bash
python3 scripts/benchmark.py --requests 10000 --concurrency 50
```

---

# Benchmark Parameters

The benchmark supports configurable workloads.

| Option          | Description                           |
| --------------- | ------------------------------------- |
| `--requests`    | Total number of requests to generate  |
| `--concurrency` | Maximum number of concurrent requests |

Example:

```bash
python3 scripts/benchmark.py --requests 5000 --concurrency 100
```

---

# Reported Metrics

The benchmark produces the following measurements.

## Throughput

Requests processed per second.

Higher values indicate better overall performance.

---

## Latency

The benchmark reports:

* Average latency
* Minimum latency
* Maximum latency
* P50 latency
* P95 latency
* P99 latency

Percentile latency provides a more representative view of system performance than averages alone.

---

## Request Results

The benchmark reports:

* Successful HTTP requests
* HTTP server errors
* Transport failures

Transport failures represent communication problems between the benchmark client and the server.

HTTP server errors represent responses returned by the application.

---

## Tenant Distribution

The benchmark simulates requests from multiple tenants.

This validates that the middleware correctly processes multi-tenant workloads during high request volumes.

---

# Expected HTTP 500 Responses

The default benchmark intentionally exercises multiple endpoints.

The workload includes requests to an endpoint that deliberately raises an exception.

As a result, approximately **10% HTTP 500 responses are expected** during the benchmark.

These responses verify that FACT correctly captures telemetry for failed requests.

They should **not** be interpreted as storage failures or framework instability.

---

# Storage Backend Comparison

FACT can benchmark multiple storage backends.

## NoOp

```bash
FACT_STORAGE_BACKEND=noop uvicorn examples.main:app --workers 4
```

Measures framework overhead without database writes.

---

## PostgreSQL

```bash
FACT_STORAGE_BACKEND=postgres uvicorn examples.main:app --workers 4
```

Measures telemetry persistence using PostgreSQL.

---

## ClickHouse

```bash
FACT_STORAGE_BACKEND=clickhouse uvicorn examples.main:app --workers 4
```

Measures telemetry persistence using ClickHouse.

Running the same benchmark against each backend allows direct performance comparison.

---

# Interpreting Results

When comparing benchmark results, consider:

* Throughput
* Average latency
* P95 latency
* P99 latency
* Transport failure rate

A low transport failure rate and stable latency under increasing concurrency indicate a healthy telemetry pipeline.

---

# Best Practices

* Execute benchmarks on an otherwise idle system.
* Use the same workload when comparing storage backends.
* Repeat benchmark runs multiple times and compare average results.
* Increase concurrency gradually to identify scalability limits.
* Use the NoOp backend to measure framework overhead independently of storage performance.
