FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ ./templates/

EXPOSE 5002

CMD ["gunicorn", "--workers", "2", "--threads", "4", "--bind", "0.0.0.0:5002", "app:app"]