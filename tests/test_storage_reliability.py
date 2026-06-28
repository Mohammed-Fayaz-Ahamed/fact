import json
import pytest
from pathlib import Path

from fact_core.storage import BaseTelemetryWriter
from fact_core.config import FactConfig

class MockReliableWriter(BaseTelemetryWriter):
    def __init__(self, config: FactConfig, fail_times=0):
        super().__init__(config)
        self.fail_times = fail_times
        self.attempts = 0

    async def enqueue(self, item):
        pass

    def _flush_to_db(self, batch):
        self.attempts += 1

        if self.attempts <= self.fail_times:
            raise Exception("Simulated database failure")


@pytest.mark.asyncio
async def test_retry_succeeds_before_max_retries(tmp_path):
    config = FactConfig(
        dlq_path=str(tmp_path / "telemetry_dlq.jsonl"),
        base_retry_delay=0,
    )

    writer = MockReliableWriter(config=config, fail_times=2)

    batch = [{"request_id": "abc"}]
    await writer._write_with_retry(batch)

    dlq = Path(config.dlq_path)
    

    assert writer.attempts == 3
    assert not dlq.exists()


@pytest.mark.asyncio
async def test_failed_batch_written_to_dlq(tmp_path):
    config = FactConfig(
        dlq_path=str(tmp_path / "telemetry_dlq.jsonl"),
        base_retry_delay=0,
    )

    writer = MockReliableWriter(
        config=config,
        fail_times=config.max_retries,
    )

    batch = [{"request_id": "abc"}]
    await writer._write_with_retry(batch)

    dlq = Path(config.dlq_path)

    assert writer.attempts == config.max_retries
    assert dlq.exists()

    with open(dlq, "r", encoding="utf-8") as f:
        record = json.loads(f.readline())

    assert record["batch"] == batch
    assert "error" in record