import json
import pytest
from pathlib import Path

from fact_core.storage import BaseTelemetryWriter, MAX_RETRIES


class MockReliableWriter(BaseTelemetryWriter):
    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.attempts = 0

    async def enqueue(self, item):
        pass

    def _flush_to_db(self, batch):
        self.attempts += 1

        if self.attempts <= self.fail_times:
            raise Exception("Simulated database failure")


@pytest.mark.asyncio
async def test_retry_succeeds_before_max_retries(tmp_path, monkeypatch):
    dlq = tmp_path / "telemetry_dlq.jsonl"

    monkeypatch.setattr("fact_core.storage.DLQ_FILE", str(dlq))

    writer = MockReliableWriter(fail_times=2)

    batch = [{"request_id": "abc"}]
    monkeypatch.setattr("fact_core.storage.BASE_RETRY_DELAY", 0)
    await writer._write_with_retry(batch)

    assert writer.attempts == 3
    assert not dlq.exists()


@pytest.mark.asyncio
async def test_failed_batch_written_to_dlq(tmp_path, monkeypatch):
    dlq = tmp_path / "telemetry_dlq.jsonl"

    monkeypatch.setattr("fact_core.storage.DLQ_FILE", str(dlq))

    writer = MockReliableWriter(fail_times=MAX_RETRIES)

    batch = [{"request_id": "abc"}]
    monkeypatch.setattr("fact_core.storage.BASE_RETRY_DELAY", 0)
    await writer._write_with_retry(batch)

    assert writer.attempts == MAX_RETRIES
    assert dlq.exists()

    with open(dlq, "r", encoding="utf-8") as f:
        record = json.loads(f.readline())

    assert record["batch"] == batch
    assert "error" in record