from __future__ import annotations

from datetime import datetime

from .models import ProcessingResult, SubmissionInput


REQUIRED_FIELDS = {
    "title": "title",
    "description": "description",
    "location": "location",
    "date": "date",
    "organizer": "organizer",
}

KEYWORD_GROUPS = [
    (
        "OPPORTUNITY",
        "HIGH",
        [
            "career",
            "careers",
            "internship",
            "intern",
            "job",
            "jobs",
            "recruitment",
            "hiring",
            "employment",
            "resume",
            "cv",
        ],
    ),
    (
        "ACADEMIC",
        "MEDIUM",
        [
            "seminar",
            "lecture",
            "research",
            "academic",
            "workshop",
            "symposium",
            "conference",
            "study",
        ],
    ),
    (
        "SOCIAL",
        "NORMAL",
        [
            "club",
            "social",
            "community",
            "party",
            "mixer",
            "networking",
            "gathering",
            "celebration",
            "society",
        ],
    ),
]


def determine_category(title: str, description: str) -> tuple[str, str]:
    haystack = f"{title} {description}".lower()
    for category, priority, keywords in KEYWORD_GROUPS:
        if any(word in haystack for word in keywords):
            return category, priority
    return "GENERAL", "NORMAL"


def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def process_submission(payload: SubmissionInput) -> ProcessingResult:
    missing = [
        field_name
        for field_name, label in REQUIRED_FIELDS.items()
        if not getattr(payload, field_name, "").strip()
    ]
    if missing:
        return ProcessingResult(
            status="INCOMPLETE",
            category="GENERAL",
            priority="NORMAL",
            reason=f"Missing required fields: {', '.join(missing)}.",
            details={"missing_fields": missing},
        )

    category, priority = determine_category(payload.title, payload.description)

    revision_reasons: list[str] = []
    if not validate_date(payload.date):
        revision_reasons.append("Date must use YYYY-MM-DD format.")

    if len(payload.description.strip()) < 40:
        revision_reasons.append("Description must be at least 40 characters.")

    if revision_reasons:
        return ProcessingResult(
            status="NEEDS REVISION",
            category=category,
            priority=priority,
            reason=" ".join(revision_reasons),
            details={"revision_reasons": revision_reasons},
        )

    return ProcessingResult(
        status="APPROVED",
        category=category,
        priority=priority,
        reason="All required fields are complete and the submission passed automated review.",
        details={},
    )
