from __future__ import annotations

from typing import Any


def lambda_handler(event: dict[str, Any], _context: Any = None) -> dict[str, Any]:
    return {
        "record_id": event["record_id"],
        "status": event["status"],
        "category": event["category"],
        "priority": event["priority"],
        "reason": event["reason"],
        "details": event.get("details", {}),
        "source": "result_update_function",
    }
