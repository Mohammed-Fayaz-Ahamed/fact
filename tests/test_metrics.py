import pytest

from fact_core.config import FactConfig
from fact_core.metrics import metrics
from fact_core.storage import BaseBatchWriter


class MockBatchWriter(BaseBatchWriter):
    def __init__(self):
        super().__init__(FactConfig(storage_backend="noop"))

    def _flush_to_db(self, batch):
        # Simulate a successful write without touching a database
        pass


@pytest.mark.asyncio
async def test_metrics_tracking():
    metrics.reset()

    writer = MockBatchWriter()

    await writer.enqueue({"request_id": "1"})
    await writer.enqueue({"request_id": "2"})

    snapshot = metrics.snapshot()

    assert snapshot["received_records"] == 2
    assert snapshot["current_queue_size"] == 2
    assert snapshot["peak_queue_size"] == 2

    batch = [
        {"request_id": "1"},
        {"request_id": "2"},
    ]

    await writer._write_with_retry(batch)

    snapshot = metrics.snapshot()

    assert snapshot["written_records"] == 2
    assert snapshot["batches_flushed"] == 1
    assert snapshot["retry_count"] == 0
    assert snapshot["failed_records"] == 0
    assert snapshot["dlq_count"] == 0