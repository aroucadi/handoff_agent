# SalesClaw CRM Simulator — Container
# Includes both the FastAPI backend and the pre-built React frontend.
FROM python:3.11-slim

WORKDIR /app

COPY crm-simulator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared core module
COPY core/ ./core/

# Copy CRM backend source files
COPY crm-simulator/main.py ./
COPY crm-simulator/models.py ./
COPY crm-simulator/seed_data.py ./

# Copy pre-built frontend dist (built by deploy.ps1 before Cloud Build)
COPY crm-simulator/frontend/dist/ ./frontend/dist/

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
