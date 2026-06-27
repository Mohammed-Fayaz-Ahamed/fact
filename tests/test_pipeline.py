import asyncio
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from fact_core.middleware import ClickHouseTelemetryMiddleware
from fact_core.storage import BaseTelemetryWriter

class MockTelemetryWriter(BaseTelemetryWriter):
    """A thread-safe mock storage writer to trap telemetry entries in memory for assertions."""
    def __init__(self):
        self.queue = asyncio.Queue()
        self.flushed_records = []
        self.is_running = False
        self._worker_task = None

    def start(self):
        self.is_running = True
        self._worker_task = asyncio.create_task(self._mock_batch_executor())

    async def stop(self):
        self.is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        # Flush any remaining items in the queue
        while not self.queue.empty():
            item = self.queue.get_nowait()
            self.flushed_records.append(item)
            self.queue.task_done()

    async def enqueue(self, item):
        await self.queue.put(item)

    async def _mock_batch_executor(self):
        while self.is_running:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=0.01)
                self._flush_to_db([item])
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue

    def _flush_to_db(self, batch: list):
        """Satisfies contract and appends to memory list."""
        for item in batch:
            self.flushed_records.append(item)


@pytest.mark.asyncio
async def test_telemetry_pipeline_end_to_end():
    # 1. Initialize and explicitly start our mock telemetry sink
    mock_writer = MockTelemetryWriter()
    mock_writer.start()
    
    try:
        # 2. Build our sandbox app and register the middleware directly
        app = FastAPI()
        app.add_middleware(ClickHouseTelemetryMiddleware, writer=mock_writer)
        
        @app.get("/test-endpoint")
        async def target_route():
            return {"status": "ok"}

        # 3. Issue the HTTP request through the ASGI transport layer
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/test-endpoint", headers={"x-request-id": "test-12345"})
            assert response.status_code == 200

    finally:
        # 4. Explicitly stop and flush the worker to guarantee all items drain down
        await mock_writer.stop()

    # 5. Run assertions on captured telemetry logs
    assert len(mock_writer.flushed_records) == 1
    log_entry = mock_writer.flushed_records[0]
    
    assert log_entry["path"] == "/test-endpoint"
    assert log_entry["status_code"] == 200
    assert log_entry["method"] == "GET"
    assert log_entry["request_id"] == "test-12345"
    assert "duration_ms" in log_entry