CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    request_id VARCHAR(255),
    method VARCHAR(10),
    path TEXT,
    status_code INT,
    duration_ms REAL,
    client_ip VARCHAR(45),
    exception_message TEXT
);

-- Index critical columns used frequently in analytical aggregation queries
CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_logs_path_status ON api_logs(path, status_code);