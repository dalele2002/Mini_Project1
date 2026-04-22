from __future__ import annotations

from typing import Any

from shared.models import SubmissionInput
from shared.rules import process_submission


def lambda_handler(event: dict[str, Any], _context: Any = None) -> dict[str, Any]:
    payload = SubmissionInput(**event["payload"])
    result = process_submission(payload)
    return {
        "record_id": event["record_id"],
        "status": result.status,
        "category": result.category,
        "priority": result.priority,
        "reason": result.reason,
        "details": result.details,
        "source": "processing_function",
    }
