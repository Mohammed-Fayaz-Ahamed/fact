import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import psycopg
import json
import os
from datetime import timezone, datetime
from fact_core.config import FactConfig
from fact_core.metrics import metrics

logger = logging.getLogger("fact")



class BaseTelemetryWriter(ABC):
    """Abstract interface to decouple FastAPI middleware from underlying storage drivers.
    Responsible only for retry logic, DLQ logic, and the storage contract.
    """
    def __init__(self, config: FactConfig):
        self.config = config

    @abstractmethod
    async def enqueue(self, item: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def _flush_to_db(self, batch: List[Dict[str, Any]]) -> None:
        pass

    async def _write_with_retry(self, batch: List[Dict[str, Any]]):
        """
        Attempt to write a telemetry batch with exponential backoff.
        Failed batches are written to the DLQ.
        """
        for attempt in range(self.config.max_retries):
            try:
                await asyncio.to_thread(self._flush_to_db, batch)

                metrics.increment("written_records", len(batch))
                metrics.increment("batches_flushed")

                return

            except Exception as e:
                metrics.increment("retry_count")
                logger.warning(
                    "Storage write failed (attempt %d/%d): %s",
                    attempt + 1,
                    self.config.max_retries,
                    e,
                )

                if attempt == self.config.max_retries - 1:
                    self._write_to_dlq(batch, str(e))
                    return

                await asyncio.sleep(
                    self.config.base_retry_delay * (2 ** attempt)
                )

    def _write_to_dlq(
        self,
        batch: List[Dict[str, Any]],
        error: str,
    ):
        """
        Persist permanently failed telemetry batches.
        """

        os.makedirs(os.path.dirname(self.config.dlq_path), exist_ok=True)
        metrics.increment("failed_records", len(batch))
        metrics.increment("dlq_count", len(batch))
        
        record = {
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "error": error,
            "batch": batch,
        }

        with open(self.config.dlq_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str))
            f.write("\n")

        logger.error("Telemetry batch written to DLQ.")


class BaseBatchWriter(BaseTelemetryWriter):
    """Base providing all shared queue management, batching, start/stop, and executor logic."""

    def __init__(
        self,
        config: FactConfig,
    ):
        self.batch_size = config.batch_size
        self.flush_interval_seconds = config.flush_interval_seconds
        super().__init__(config)

        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None
        self.is_running = False

    def start(self):
        """Starts the background worker task loop."""
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._batch_executor())
            logger.info("%s worker engine started.", self.__class__.__name__)

    async def stop(self):
        """Gracefully flushes remaining items in the queue and shuts down the worker."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        # Pull remaining items left behind in the memory buffer
        remaining_items = []
        while not self.queue.empty():
            remaining_items.append(await self.queue.get())
            self.queue.task_done()

        if remaining_items:
            await self._write_with_retry(remaining_items)

    async def enqueue(self, item: Dict[str, Any]):
        """Non-blocking injection into the memory queue."""
        await self.queue.put(item)
        
        metrics.increment("received_records")
        metrics.set_queue_size(self.queue.qsize())

    async def _batch_executor(self):
        """Continuous polling monitor that builds batches based on sizes or time deltas."""
        loop = asyncio.get_running_loop()
        while self.is_running:
            batch: List[Dict[str, Any]] = []
            start_time = loop.time()

            while len(batch) < self.batch_size:
                time_remaining = self.flush_interval_seconds - (loop.time() - start_time)

                if time_remaining <= 0:
                    break

                try:
                    item = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=max(0.1, time_remaining)
                    )

                    batch.append(item)

                    self.queue.task_done()
                    metrics.set_queue_size(self.queue.qsize())
                except asyncio.TimeoutError:
                    break

            if batch:
                await self._write_with_retry(batch)


class PostgresBatchWriter(BaseBatchWriter):
    """PostgreSQL-specific implementation. Contains only DB-specific init and flush logic."""

    def __init__(self, config: FactConfig):
        super().__init__(config=config)
        self.dsn = config.postgres_dsn

    def _flush_to_db(self, batch: List[Dict[str, Any]]):
        """Executes a thread-safe bulk transactional write into PostgreSQL."""
        data_rows = [
            (
                item["timestamp"], item["request_id"], item["method"],
                item["path"], item["status_code"], item["duration_ms"],
                item["client_ip"], item["exception_message"], item.get("metadata", {})
            )
            for item in batch
        ]

        # Open a distinct short-lived thread connection from your DSN configuration pool
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.executemany("""
                    INSERT INTO api_logs (timestamp, request_id, method, path, status_code, duration_ms, client_ip, exception_message, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data_rows)


import clickhouse_connect


class ClickHouseBatchWriter(BaseBatchWriter):
    """ClickHouse-specific implementation. Contains only DB-specific init and flush logic."""

    def __init__(self, config: FactConfig):
        super().__init__(config=config)
        self.host = config.clickhouse_host
        self.port = config.clickhouse_port
        self.username = config.clickhouse_username
        self.password = config.clickhouse_password
        self.database = config.clickhouse_database

    def _flush_to_db(self, batch: List[Dict[str, Any]]):
        """Inserts columnar micro-batches directly into the local ClickHouse instance."""
        # ClickHouse driver accepts data as matrix structures (list of tuples/lists)
        data_rows = [
            [
                item["timestamp"], item["request_id"], item["tenant_id"], item["method"],
                item["path"], item["status_code"], item["duration_ms"],
                item["client_ip"], item["exception_message"], item.get("metadata", {})
            ]
            for item in batch
        ]

        client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database
        )

        client.insert(
            table='api_logs',
            data=data_rows,
            column_names=['timestamp', 'request_id', 'tenant_id', 'method', 'path', 'status_code', 'duration_ms', 'client_ip', 'exception_message', 'metadata']
        )
        client.close()


class NoOpWriter(BaseBatchWriter):
    """Performance testing writer that discards telemetry."""

    def __init__(self, config: FactConfig):
        super().__init__(config)

    def _flush_to_db(self, batch):
        pass


class TelemetryWriterFactory:
    """Centralized initializer engine to return backend drivers via target configurations."""

    @staticmethod
    def create_writer(config: FactConfig) -> BaseTelemetryWriter:
        engine_type = config.storage_backend.lower().strip()
        if engine_type == "noop":
            return NoOpWriter(config)
        elif engine_type == "postgres" or engine_type == "postgresql":
            return PostgresBatchWriter(config)

        elif engine_type == "clickhouse":
            return ClickHouseBatchWriter(config)

        else:
            raise ValueError(f"Unsupported telemetry storage engine backend target: '{engine_type}'")