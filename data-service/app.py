from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DEFAULT_DB_PATH = "/data/submissions.db" if os.name != "nt" else "./data/submissions.db"
DB_PATH = Path(os.getenv("DB_PATH", DEFAULT_DB_PATH))
app = FastAPI(title="Data Service")


class CreateRecordRequest(BaseModel):
    title: str = ""
    description: str = ""
    location: str = ""
    date: str = ""
    organizer: str = ""


class UpdateRecordRequest(BaseModel):
    status: str
    category: str
    priority: str
    reason: str
    details: dict[str, Any] = Field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                organizer TEXT NOT NULL,
                status TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/records")
def create_record(payload: CreateRecordRequest) -> dict[str, Any]:
    record_id = str(uuid4())
    now = utc_now()
    record = {
        "id": record_id,
        "title": payload.title,
        "description": payload.description,
        "location": payload.location,
        "date": payload.date,
        "organizer": payload.organizer,
        "status": "PENDING",
        "category": "GENERAL",
        "priority": "NORMAL",
        "reason": "Submission received and queued for automated review.",
        "created_at": now,
        "updated_at": now,
    }
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO submissions (
                id, title, description, location, date, organizer,
                status, category, priority, reason, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(record.values()),
        )
        connection.commit()
    return record


@app.get("/records/{record_id}")
def get_record(record_id: str) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (record_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return dict(row)


@app.put("/records/{record_id}")
def update_record(record_id: str, payload: UpdateRecordRequest) -> dict[str, Any]:
    now = utc_now()
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            UPDATE submissions
            SET status = ?, category = ?, priority = ?, reason = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                payload.status,
                payload.category,
                payload.priority,
                payload.reason,
                now,
                record_id,
            ),
        )
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        row = connection.execute(
            "SELECT * FROM submissions WHERE id = ?",
            (record_id,),
        ).fetchone()
    return dict(row)
