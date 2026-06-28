import pytest
from datetime import datetime, timezone

from fact_core.validation import validate_telemetry_record


def valid_record():
    return {
        "timestamp": datetime.now(timezone.utc),
        "request_id": "123",
        "tenant_id": "default",
        "method": "GET",
        "path": "/",
        "status_code": 200,
        "duration_ms": 10.5,
        "request_bytes": 100,
        "response_bytes": 200,
        "client_ip": "127.0.0.1",
        "exception_message": "",
        "metadata": {},
    }


def test_valid_record():
    validate_telemetry_record(valid_record())


def test_missing_field():
    record = valid_record()
    del record["path"]

    with pytest.raises(ValueError):
        validate_telemetry_record(record)


def test_invalid_type():
    record = valid_record()
    record["status_code"] = "200"

    with pytest.raises(ValueError):
        validate_telemetry_record(record)


def test_metadata_can_contain_anything():
    record = valid_record()

    record["metadata"] = {
        "user": "abc",
        "cart": "5",
        "anything": "allowed",
        "another_key": "works",
    }

    validate_telemetry_record(record)