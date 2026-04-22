from __future__ import annotations

import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


DEFAULT_WORKFLOW_SERVICE_URL = "http://127.0.0.1:8001"
WORKFLOW_SERVICE_URL = os.getenv("WORKFLOW_SERVICE_URL", DEFAULT_WORKFLOW_SERVICE_URL)
app = FastAPI(title="Demo Service")
TEMPLATE_DIR = Path(__file__).with_name("templates")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "record": None,
            "record_id": "",
            "error": "",
        },
    )


@app.post("/submit", response_class=HTMLResponse)
async def submit(
    request: Request,
    title: str = Form(""),
    description: str = Form(""),
    location: str = Form(""),
    date: str = Form(""),
    organizer: str = Form(""),
) -> HTMLResponse:
    payload = {
        "title": title,
        "description": description,
        "location": location,
        "date": date,
        "organizer": organizer,
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(f"{WORKFLOW_SERVICE_URL}/submissions", json=payload)
            response.raise_for_status()
            record = response.json()["record"]
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "record": record,
                "record_id": record["id"],
                "error": "",
            },
        )
    except httpx.HTTPError as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "record": None,
                "record_id": "",
                "error": f"Unable to submit activity right now: {exc}",
            },
            status_code=502,
        )


@app.get("/records/{record_id}", response_class=HTMLResponse)
async def view_record(request: Request, record_id: str) -> HTMLResponse:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(f"{WORKFLOW_SERVICE_URL}/submissions/{record_id}")
            response.raise_for_status()
            record = response.json()["record"]
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "record": record,
                "record_id": record_id,
                "error": "",
            },
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            message = f"No submission found for ID {record_id}."
        else:
            message = f"Unable to load submission right now: {exc}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "record": None,
                "record_id": record_id,
                "error": message,
            },
            status_code=exc.response.status_code,
        )


@app.post("/lookup")
async def lookup(record_id: str = Form("")) -> RedirectResponse:
    return RedirectResponse(url=f"/records/{record_id.strip()}", status_code=303)
