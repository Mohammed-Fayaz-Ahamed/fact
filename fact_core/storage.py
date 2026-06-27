import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import psycopg

logger = logging.getLogger("fact")

class BaseTelemetryWriter(ABC):
    """Abstract interface to decouple FastAPI middleware from underlying storage drivers."""
    @abstractmethod
    async def enqueue(self, item: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def _flush_to_db(self, batch: List[Dict[str, Any]]) -> None:
        pass


class PostgresBatchWriter(BaseTelemetryWriter):
    def __init__(
        self, 
        dsn: str, 
        batch_size: int = 100, 
        flush_interval_seconds: float = 3.0
    ):
        self.dsn = dsn
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task = None
        self.is_running = False

    def start(self):
        """Starts the background worker task loop."""
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._batch_executor())
            logger.info("FACT Postgres Batch Writer worker engine started.")

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
            self._flush_to_db(remaining_items)
            logger.info(f"FACT Shutdown complete. Flushed final {len(remaining_items)} remaining log entries.")

    async def enqueue(self, item: Dict[str, Any]):
        """Non-blocking injection into the memory queue."""
        await self.queue.put(item)

    async def _batch_executor(self):
        """Continuous polling monitor that builds batches based on sizes or time deltas."""
        while self.is_running:
            batch: List[Dict[str, Any]] = []
            start_time = asyncio.get_event_loop().time()

            while len(batch) < self.batch_size:
                time_remaining = self.flush_interval_seconds - (asyncio.get_event_loop().time() - start_time)
                
                if time_remaining <= 0:
                    break

                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=max(0.1, time_remaining))
                    batch.append(item)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    break

            if batch:
                try:
                    # Offload blocking database network I/O execution to an isolated thread pool
                    await asyncio.to_thread(self._flush_to_db, batch)
                except Exception as e:
                    logger.error(f"FACT Engine error trying to write telemetry to Postgres: {e}")

    def _flush_to_db(self, batch: List[Dict[str, Any]]):
        """Executes a thread-safe bulk transactional write into PostgreSQL."""
        data_rows = [
            (
                item["timestamp"], item["request_id"], item["method"], 
                item["path"], item["status_code"], item["duration_ms"], 
                item["client_ip"], item["exception_message"]
            )
            for item in batch
        ]
        
        # Open a distinct short-lived thread connection from your DSN configuration pool
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.executemany("""
                    INSERT INTO api_logs (timestamp, request_id, method, path, status_code, duration_ms, client_ip, exception_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, data_rows)
                
import clickhouse_connect

class ClickHouseBatchWriter(BaseTelemetryWriter):
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8123, 
        username: str = "default", 
        password: str = "",
        database: str = "default",
        batch_size: int = 5000, # OLAP writes favor much larger batch limits
        flush_interval_seconds: float = 3.0
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: asyncio.Task = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._batch_executor())
            logger.info("FACT ClickHouse Batch Writer engine started.")

    async def stop(self):
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        
        remaining_items = []
        while not self.queue.empty():
            remaining_items.append(await self.queue.get())
            self.queue.task_done()
            
        if remaining_items:
            self._flush_to_db(remaining_items)

    async def enqueue(self, item: Dict[str, Any]):
        await self.queue.put(item)

    async def _batch_executor(self):
        while self.is_running:
            batch: List[Dict[str, Any]] = []
            start_time = asyncio.get_event_loop().time()

            while len(batch) < self.batch_size:
                time_remaining = self.flush_interval_seconds - (asyncio.get_event_loop().time() - start_time)
                if time_remaining <= 0:
                    break

                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=max(0.1, time_remaining))
                    batch.append(item)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    break

            if batch:
                try:
                    await asyncio.to_thread(self._flush_to_db, batch)
                except Exception as e:
                    logger.error(f"FACT Engine error trying to write telemetry to ClickHouse: {e}")

    def _flush_to_db(self, batch: List[Dict[str, Any]]):
        """Inserts columnar micro-batches directly into the local ClickHouse instance."""
        # ClickHouse driver accepts data as matrix structures (list of tuples/lists)
        data_rows = [
            [
                item["timestamp"], item["request_id"], item["method"], 
                item["path"], item["status_code"], item["duration_ms"], 
                item["client_ip"], item["exception_message"]
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
            column_names=['timestamp', 'request_id', 'method', 'path', 'status_code', 'duration_ms', 'client_ip', 'exception_message']
        )
        client.close()
        
class TelemetryWriterFactory:
    """Centralized initializer engine to return backend drivers via target configurations."""
    
    @staticmethod
    def create_writer(engine_type: str, config: Dict[str, Any]) -> BaseTelemetryWriter:
        engine_type = engine_type.lower().strip()
        
        if engine_type == "postgres" or engine_type == "postgresql":
            return PostgresBatchWriter(
                dsn=config.get("dsn", "postgresql://postgres:postgres@localhost:5432/postgres"),
                batch_size=config.get("batch_size", 100),
                flush_interval_seconds=config.get("flush_interval_seconds", 3.0)
            )
            
        elif engine_type == "clickhouse":
            return ClickHouseBatchWriter(
                host=config.get("host", "127.0.0.1"),
                port=config.get("port", 8123),
                username=config.get("username", "default"),
                password=config.get("password", ""),
                database=config.get("database", "default"),
                batch_size=config.get("batch_size", 5000),
                flush_interval_seconds=config.get("flush_interval_seconds", 3.0)
            )
            
        else:
            raise ValueError(f"Unsupported telemetry storage engine backend target: '{engine_type}'")