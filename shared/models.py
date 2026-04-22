from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SubmissionInput(BaseModel):
    title: str = ""
    description: str = ""
    location: str = ""
    date: str = ""
    organizer: str = ""


class SubmissionRecord(BaseModel):
    id: str
    title: str
    description: str
    location: str
    date: str
    organizer: str
    status: str = "PENDING"
    category: str = "GENERAL"
    priority: str = "NORMAL"
    reason: str = "Submission received and waiting for processing."
    created_at: str
    updated_at: str


class ProcessingResult(BaseModel):
    status: str
    category: str
    priority: str
    reason: str
    details: dict[str, Any] = Field(default_factory=dict)
