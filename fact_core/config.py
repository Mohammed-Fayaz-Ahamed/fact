import os
from dataclasses import dataclass


@dataclass(slots=True)
class FactConfig:
    """
    Central configuration object for the FACT framework.
    Supports both programmatic configuration and environment variables.
    """

    # Storage
    storage_backend: str = "clickhouse"

    # PostgreSQL
    postgres_dsn: str = (
        "postgresql://postgres:postgres@localhost:5432/postgres"
    )

    # ClickHouse
    clickhouse_host: str = "127.0.0.1"
    clickhouse_port: int = 8123
    clickhouse_username: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "default"

    # Batch Processing
    batch_size: int = 5000
    flush_interval_seconds: float = 3.0

    # Reliability
    max_retries: int = 5
    base_retry_delay: float = 1.0
    dlq_path: str = "failed_batches/telemetry_dlq.jsonl"

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "FactConfig":
        return cls(
            storage_backend=os.getenv(
                "FACT_STORAGE_BACKEND",
                "clickhouse",
            ),

            postgres_dsn=os.getenv(
                "FACT_POSTGRES_DSN",
                "postgresql://postgres:postgres@localhost:5432/postgres",
            ),

            clickhouse_host=os.getenv(
                "FACT_CLICKHOUSE_HOST",
                "127.0.0.1",
            ),

            clickhouse_port=int(
                os.getenv(
                    "FACT_CLICKHOUSE_PORT",
                    "8123",
                )
            ),

            clickhouse_username=os.getenv(
                "FACT_CLICKHOUSE_USERNAME",
                "default",
            ),

            clickhouse_password=os.getenv(
                "FACT_CLICKHOUSE_PASSWORD",
                "",
            ),

            clickhouse_database=os.getenv(
                "FACT_CLICKHOUSE_DATABASE",
                "default",
            ),

            batch_size=int(
                os.getenv(
                    "FACT_BATCH_SIZE",
                    "5000",
                )
            ),

            flush_interval_seconds=float(
                os.getenv(
                    "FACT_FLUSH_INTERVAL",
                    "3.0",
                )
            ),

            max_retries=int(
                os.getenv(
                    "FACT_MAX_RETRIES",
                    "5",
                )
            ),

            base_retry_delay=float(
                os.getenv(
                    "FACT_BASE_RETRY_DELAY",
                    "1.0",
                )
            ),

            dlq_path=os.getenv(
                "FACT_DLQ_PATH",
                "failed_batches/telemetry_dlq.jsonl",
            ),

            log_level=os.getenv(
                "FACT_LOG_LEVEL",
                "INFO",
            ),
        )