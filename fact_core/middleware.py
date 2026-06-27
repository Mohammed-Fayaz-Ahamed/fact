import time
import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fact_core.storage import BaseTelemetryWriter

class ClickHouseTelemetryMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, writer: BaseTelemetryWriter):
        super().__init__(app)
        self.writer = writer

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        exception_msg = ""
        status_code = 500
        
        # 1. Extract multi-tenant routing key from headers
        tenant_id = request.headers.get("x-tenant-id", "default-tenant")
        print(f"DEBUG MIDDLEWARE: Extracted Header -> {tenant_id}")
        # 2. Calculate incoming request size from Content-Length header
        try:
            req_bytes = int(request.headers.get("content-length", 0))
        except ValueError:
            req_bytes = 0

        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # 3. Calculate outgoing response size
            try:
                res_bytes = int(response.headers.get("content-length", 0))
            except ValueError:
                res_bytes = 0
                
            return response
        except Exception as e:
            exception_msg = str(e)
            res_bytes = 0
            raise e
        finally:
            duration = (time.perf_counter() - start_time) * 1000
            
            # Automatically capture URL query string params as strings
            query_metadata = {k: str(v) for k, v in request.query_params.items()}
            
            # Capture any endpoint state added manually in scope via request.state (if any exists)
            state_metadata = {}
            if "state" in request.scope:
                # Safely pull values set by routes like request.state.fact_metadata = {...}
                state_metadata = request.scope["state"].get("fact_metadata", {})
            
            # Merge context securely (state overrides common query strings if keys overlap)
            combined_metadata = {**query_metadata, **state_metadata}
            # -------------------------------------

            # 4. Construct Evolved Log Entry
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
                "request_id": request.headers.get("x-request-id", "none"),
                "tenant_id": tenant_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration,
                "request_bytes": req_bytes,
                "response_bytes": res_bytes,
                "client_ip": request.client.host if request.client else "127.0.0.1",
                "exception_message": exception_msg,
                "metadata": combined_metadata  # <-- ADDED TO INGESTION PAYLOAD
            }
            
            await self.writer.enqueue(log_entry)