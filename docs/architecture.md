# Architecture

FACT is built around an asynchronous producer-consumer architecture that separates HTTP request processing from telemetry persistence.

The primary design goals are:

* Minimize request latency.
* Decouple request handling from storage operations.
* Support multiple storage backends.
* Provide reliable telemetry persistence through retries and a Dead Letter Queue (DLQ).

---

# Request Flow

```text
                HTTP Request
                      │
                      ▼
        ClickHouseTelemetryMiddleware
                      │
                      ▼
          Telemetry Payload Creation
                      │
                      ▼
             Payload Validation
                      │
                      ▼
           Async In-Memory Queue
                      │
                      ▼
        Background Batch Worker
                      │
                      ▼
          Retry with Backoff Logic
             │                  │
             │ Success          │ Failure
             ▼                  ▼
     Storage Backend      Dead Letter Queue
             │
             ▼
      PostgreSQL / ClickHouse
```

---

# Core Components

## Middleware

The middleware automatically captures telemetry for every incoming request.

Collected information includes:

* Timestamp
* Request ID
* Tenant ID
* HTTP method
* Request path
* Response status
* Request duration
* Request size
* Response size
* Client IP
* Exception details
* Custom metadata

Application endpoints do not need to manually generate telemetry records.

---

## Payload Validation

Before a telemetry record enters the processing pipeline, FACT validates the payload to ensure that required fields are present and correctly structured.

Invalid payloads are rejected before entering the queue.

---

## Async Queue

Validated telemetry records are placed into an asynchronous in-memory queue.

This keeps request processing independent from storage performance and minimizes the latency experienced by the client.

---

## Batch Processing

A background worker continuously reads records from the queue.

Records are written in batches based on:

* Batch size
* Flush interval

Batching significantly reduces storage overhead compared to individual writes.

---

## Retry Mechanism

If a storage write fails, FACT retries the operation using exponential backoff.

This improves resilience against temporary storage outages.

---

## Dead Letter Queue (DLQ)

If all retry attempts fail, the batch is written to the Dead Letter Queue.

The DLQ preserves telemetry records for later inspection or replay instead of silently discarding them.

---

## Storage Backends

FACT currently supports:

* PostgreSQL
* ClickHouse
* NoOp (testing)

Additional storage backends can be implemented by extending the telemetry writer abstraction.

---

# Runtime Metrics

FACT maintains internal runtime metrics including:

* Received records
* Written records
* Failed records
* Retry count
* Batch flush count
* Current queue size
* Peak queue size
* Dead Letter Queue count

These metrics provide visibility into the health of the telemetry pipeline.

---

# Design Principles

FACT is designed around the following principles:

* Asynchronous processing
* Storage abstraction
* Reliability over silent failure
* Minimal request overhead
* Configurable behavior
* Backend independence
* Testability
