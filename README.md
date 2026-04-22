# Campus Activity Review System

This project implements the PDF workflow as a small hybrid cloud-native app with exactly:

- 3 container services: `demo-service`, `workflow-service`, `data-service`
- 3 serverless functions: `submission_event_function`, `processing_function`, `result_update_function`

## Workflow

1. The user submits a campus activity in the demo service.
2. The workflow service creates an initial record in the data service.
3. The submission event function converts the new record into a processing request.
4. The processing function applies the required rules from the assignment.
5. The result update function prepares the final update.
6. The data service stores the final result, and the demo service shows it to the user.

## Rules implemented

- All required fields must be present.
- Missing required fields always produce `INCOMPLETE` and stop later rules from overriding that result.
- Date must use `YYYY-MM-DD`.
- Description must contain at least 40 characters.
- Categories use the required priority order:
  - `OPPORTUNITY`
  - `ACADEMIC`
  - `SOCIAL`
  - `GENERAL`
- Priority mapping:
  - `OPPORTUNITY` -> `HIGH`
  - `ACADEMIC` -> `MEDIUM`
  - `SOCIAL` or `GENERAL` -> `NORMAL`
- Final statuses:
  - `INCOMPLETE`
  - `NEEDS REVISION`
  - `APPROVED`

## Run
### method one：
```bash
docker compose up --build
```
Then open http://localhost:8000.

If you face the issue was caused by network restrictions in the campus local area network, where the intranet firewall blocked external access required by Docker, use the follow method.
### method two：
1. Activate the virtual environment
```bash
venv\Scripts\activate
```
2. Start the data-service (8002)
```bash
cd data-service
uvicorn app:app --reload --port 8002
```
3. Start workflow-service（8001）
```bash
venv\Scripts\activate
cd workflow-service
uvicorn app:app --reload --port 8001
```
4. Start demo-service（8000）
```bash
venv\Scripts\activate
cd demo-service
uvicorn app:app --reload --port 8000
```
Then open http://localhost:8000.

## Service ports

- Demo UI: `8000`
- Workflow API: `8001`
- Data API: `8002`

## Example submission

- Title: `AI Internship and Career Fair`
- Description: `Meet recruiters, discuss internship opportunities, and learn how to prepare for technical interviews at the annual campus hiring event.`
- Location: `Innovation Center`
- Date: `2026-05-10`
- Organizer: `Career Office`
