FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data-service /app/data-service

CMD ["uvicorn", "app:app", "--app-dir", "/app/data-service", "--host", "0.0.0.0", "--port", "8002"]
