-- ============================================================================
-- HIGH-THROUGHPUT CLICKHOUSE OPTIMIZATION & SCHEMAS (EVOLVED)
-- Location: fact_core/clickhouse_optimizations.sql
-- ============================================================================

-- 1. Evolved Core Raw Log Table
CREATE TABLE IF NOT EXISTS api_logs (
    timestamp DateTime64(6, 'UTC'),
    request_id String,
    tenant_id LowCardinality(String),  
    method LowCardinality(String),
    path String,
    status_code UInt16,
    duration_ms Float32,
    request_bytes UInt64,             
    response_bytes UInt64,            
    client_ip String,
    exception_message String
) ENGINE = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (status_code, path, timestamp)
TTL timestamp + INTERVAL 7 DAY;

-- 2. Evolved Hourly Aggregation Target Table
CREATE TABLE IF NOT EXISTS hourly_api_metrics (
    hour DateTime,
    tenant_id LowCardinality(String),
    method LowCardinality(String),
    path String,
    total_requests UInt64,
    error_requests UInt64,
    total_duration_ms Float64
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (method, path, hour, tenant_id);

-- 3. Materialized View Data Pipeline Trigger
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_api_metrics
TO hourly_api_metrics
AS SELECT
    toStartOfHour(timestamp) as hour,
    tenant_id,
    method,
    path,
    count() as total_requests,
    sum(status_code >= 500) as error_requests,
    sum(duration_ms) as total_duration_ms
FROM api_logs
GROUP BY hour, tenant_id, method, path;

-- 4. Path-Optimized Performance Projection
ALTER TABLE api_logs ADD PROJECTION IF NOT EXISTS p_path_performance (
    SELECT path, status_code, avg(duration_ms), count() 
    GROUP BY path, status_code, timestamp
);