# Middleware

FACT collects telemetry through the `ClickHouseTelemetryMiddleware`.

Once registered, the middleware automatically captures telemetry for every incoming HTTP request.

No changes to existing route handlers are required.

---

# Registering the Middleware

```python
from fastapi import FastAPI

from fact_core.config import FactConfig
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.storage import TelemetryWriterFactory

config = FactConfig.from_env()

writer = TelemetryWriterFactory.create_writer(config)

app = FastAPI()

app.add_middleware(
    ClickHouseTelemetryMiddleware,
    writer=writer,
)
```

---

# Automatically Captured Fields

FACT automatically captures the following information for every request.

| Field             | Description                                  |
| ----------------- | -------------------------------------------- |
| Timestamp         | UTC timestamp when the request completed     |
| Request ID        | Request identifier from the incoming headers |
| Tenant ID         | Tenant identifier from the incoming headers  |
| HTTP Method       | GET, POST, PUT, DELETE, etc.                 |
| Request Path      | Request URL path                             |
| Status Code       | HTTP response status                         |
| Duration          | Request processing time                      |
| Request Size      | Incoming payload size                        |
| Response Size     | Outgoing response size                       |
| Client IP         | Remote client IP address                     |
| Exception Message | Exception message for failed requests        |
| Metadata          | Custom application metadata                  |

---

# Multi-Tenant Support

FACT supports multi-tenant applications by reading the tenant identifier from the request headers.

Example:

```http
X-Tenant-ID: alpha-corp
```

If no tenant identifier is provided, the configured default value is used.

---

# Request Correlation

FACT supports request tracing using a request identifier.

Example:

```http
X-Request-ID: req-123456789
```

This identifier is included in every telemetry record and can be used to correlate application logs with telemetry events.

---

# Custom Metadata

Applications can attach additional telemetry information using `request.state.fact_metadata`.

Example:

```python
@app.get("/checkout")
async def checkout(request: Request):

    request.state.fact_metadata = {
        "user_tier": "premium",
        "experiment": "variant_a",
        "cart_items": "3"
    }

    return {"status": "success"}
```

The metadata is automatically merged into the telemetry payload before it is written to the configured storage backend.

---

# Validation

Before entering the asynchronous queue, every telemetry payload is validated.

Validation helps detect malformed telemetry records before they reach the storage backend.

---

# Performance

The middleware does not perform database writes during request processing.

Instead, telemetry records are placed into an asynchronous queue and processed by a background worker.

This minimizes request latency while maintaining reliable telemetry collection.

