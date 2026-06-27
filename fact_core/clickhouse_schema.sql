CREATE TABLE IF NOT EXISTS api_logs (
    timestamp DateTime64(6, 'UTC'),
    request_id String,
    method LowCardinality(String),
    path String,
    status_code UInt16,
    duration_ms Float32,
    client_ip String,
    exception_message String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (status_code, path, timestamp);