from threading import Lock
from typing import Dict


class TelemetryMetrics:
    """Thread-safe runtime metrics registry for FACT."""

    def __init__(self):
        self._lock = Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.received_records = 0
            self.written_records = 0
            self.failed_records = 0
            self.retry_count = 0
            self.dlq_count = 0
            self.batches_flushed = 0
            self.current_queue_size = 0
            self.peak_queue_size = 0

    def increment(self, field: str, amount: int = 1):
        with self._lock:
            setattr(
                self,
                field,
                getattr(self, field) + amount,
            )

    def set_queue_size(self, size: int):
        with self._lock:
            self.current_queue_size = size

            if size > self.peak_queue_size:
                self.peak_queue_size = size

    def snapshot(self) -> Dict[str, int]:
        with self._lock:
            return {
                "received_records": self.received_records,
                "written_records": self.written_records,
                "failed_records": self.failed_records,
                "retry_count": self.retry_count,
                "dlq_count": self.dlq_count,
                "batches_flushed": self.batches_flushed,
                "current_queue_size": self.current_queue_size,
                "peak_queue_size": self.peak_queue_size,
            }


metrics = TelemetryMetrics()