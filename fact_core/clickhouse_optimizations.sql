-- ============================================================================
-- HIGH-THROUGHPUT CLICKHOUSE OPTIMIZATION & SCHEMAS
-- Location: fact_core/clickhouse_optimizations.sql
-- ============================================================================

-- 1. Hourly Aggregation Target Table for Long-Term Trends
CREATE TABLE IF NOT EXISTS hourly_api_metrics (
    hour DateTime,
    method LowCardinality(String),
    path String,
    total_requests UInt64,
    error_requests UInt64,
    total_duration_ms Float64
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (method, path, hour);

-- 2. Materialized View Data Pipeline Trigger
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_hourly_api_metrics
TO hourly_api_metrics
AS SELECT
    toStartOfHour(timestamp) as hour,
    method,
    path,
    count() as total_requests,
    sum(status_code >= 500) as error_requests,
    sum(duration_ms) as total_duration_ms
FROM api_logs
GROUP BY hour, method, path;

-- 3. Path-Optimized Performance Projection
-- Note: ClickHouse structures sorting automatically by the GROUP BY expression keys.
ALTER TABLE api_logs ADD PROJECTION IF NOT EXISTS p_path_performance (
    SELECT path, status_code, avg(duration_ms), count() 
    GROUP BY path, status_code, timestamp
);

-- 4. Materialize the Projection across Pre-Existing Data Chunks
ALTER TABLE api_logs MATERIALIZE PROJECTION p_path_performance;

-- 5. Data Retention Storage Policy (TTL)
-- Automatically purges granular raw log records older than 7 days during background merges
ALTER TABLE api_logs MODIFY TTL timestamp + INTERVAL 7 DAY;