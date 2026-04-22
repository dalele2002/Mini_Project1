from __future__ import annotations

from typing import Any


def lambda_handler(event: dict[str, Any], _context: Any = None) -> dict[str, Any]:
    record = event["record"]
    return {
        "record_id": record["id"],
        "payload": {
            "title": record["title"],
            "description": record["description"],
            "location": record["location"],
            "date": record["date"],
            "organizer": record["organizer"],
        },
        "source": "submission_event_function",
    }
