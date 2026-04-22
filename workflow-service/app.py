'''
Author: borui li 101801839+dalele2002@users.noreply.github.com
Date: 2026-04-21 20:16:11
LastEditors: dalele2002 dagujie@126.com
LastEditTime: 2026-04-22 16:51:49
FilePath: \campus-activity-review-system-main\workflow-service\app.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from __future__ import annotations

import sys
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
# 新增的路径修复代码 ↑

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

from functions.process_submission.handler import lambda_handler as process_handler
from functions.submission_event.handler import lambda_handler as submission_event_handler
from functions.update_result.handler import lambda_handler as update_result_handler
from shared.models import SubmissionInput

DEFAULT_DATA_SERVICE_URL = "http://127.0.0.1:8002"
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", DEFAULT_DATA_SERVICE_URL)
app = FastAPI(title="Workflow Service")


async def get_record(record_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{DATA_SERVICE_URL}/records/{record_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Record not found")
    response.raise_for_status()
    return response.json()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/submissions")
async def create_submission(payload: SubmissionInput) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        create_response = await client.post(
            f"{DATA_SERVICE_URL}/records",
            json=payload.dict(),
        )
        create_response.raise_for_status()
        record = create_response.json()

        submission_event = submission_event_handler({"record": record}, None)
        processed = process_handler(submission_event, None)
        update_payload = update_result_handler(processed, None)

        update_response = await client.put(
            f"{DATA_SERVICE_URL}/records/{record['id']}",
            json=update_payload,
        )
        update_response.raise_for_status()
        final_record = update_response.json()

    return {
        "message": "Submission stored and processed successfully.",
        "record": final_record,
        "workflow": [
            "container:workflow_service created initial record",
            "serverless:submission_event_function transformed the new submission",
            "serverless:processing_function computed status, category, and priority",
            "serverless:result_update_function prepared the update payload",
            "container:data_service stored the final result",
        ],
    }


@app.get("/submissions/{record_id}")
async def fetch_submission(record_id: str) -> dict[str, Any]:
    record = await get_record(record_id)
    return {"record": record}
