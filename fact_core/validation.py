from datetime import datetime
from typing import Any, Dict


REQUIRED_FIELDS = {
    "timestamp": datetime,
    "request_id": str,
    "tenant_id": str,
    "method": str,
    "path": str,
    "status_code": int,
    "duration_ms": (int, float),
    "request_bytes": int,
    "response_bytes": int,
    "client_ip": str,
    "exception_message": str,
    "metadata": dict,
}


def validate_telemetry_record(record: Dict[str, Any]) -> None:
    """
    Validate the FACT core telemetry contract.
    Raises ValueError if validation fails.
    """

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in record:
            raise ValueError(f"Missing required field: {field}")

        if not isinstance(record[field], expected_type):
            raise ValueError(
                f"Invalid type for '{field}'. "
                f"Expected {expected_type}, got {type(record[field])}"
            )