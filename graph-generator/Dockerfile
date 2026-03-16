FROM python:3.11-slim

WORKDIR /app

COPY graph-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY graph-generator/ ./

EXPOSE 8080

# Use shell form to allow environment variable expansion for PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
