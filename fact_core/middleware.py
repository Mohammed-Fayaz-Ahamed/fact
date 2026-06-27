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
        
        try:
            # Pass the request down the FastAPI pipeline to the path operation
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            # Capture the raw exception message if the API endpoint fails
            exception_msg = str(e)
            raise e
        finally:
            # Calculate duration in milliseconds (precise to fractional points)
            duration = (time.perf_counter() - start_time) * 1000
            
            # Construct a structured log entry matching our storage schema
            log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
                "request_id": request.headers.get("x-request-id", "none"),
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": duration,
                "client_ip": request.client.host if request.client else "127.0.0.1",
                "exception_message": exception_msg
            }
            
            # Non-blocking handoff to the storage engine's memory buffer queue
            await self.writer.enqueue(log_entry)