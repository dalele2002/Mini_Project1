FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workflow-service /app/workflow-service
COPY shared /app/shared
COPY functions /app/functions

CMD ["uvicorn", "app:app", "--app-dir", "/app/workflow-service", "--host", "0.0.0.0", "--port", "8001"]
