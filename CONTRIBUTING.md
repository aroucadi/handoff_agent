# Contributing to Synapse

Welcome! Synapse is a multi-modal React + Python FastAPI application using Gemini. Here is how you can set up your local development environment.

## 1. Local Environment Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- [Firebase CLI](https://firebase.google.com/docs/cli)
- Docker Desktop (Optional, for building deployment containers)

### Backend Services
Synapse uses a shared `core/` package across its three Python microservices. To develop locally:

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Or `.\venv\Scripts\Activate` on Windows

# 2. Install dependencies for all services
pip install -r backend/requirements.txt
pip install -r graph-generator/requirements.txt
pip install -r crm-simulator/requirements.txt

# 3. Export your Gemini API Key
export GEMINI_API_KEY="AIzaSyYourKeyHere..."

# 4. Start the services on different ports
uvicorn backend.main:app --port 8000 --reload
uvicorn crm-simulator.main:app --port 8001 --reload
uvicorn graph-generator.main:app --port 8002 --reload
```

### Frontend Dashboard
The React frontend lives in the `frontend/` directory.

```bash
cd frontend
npm install
npm run dev
```
The React app defaults to hitting `localhost` ports for the backend services when deployed locally.

## 2. Development Guidelines

### Prompt Engineering
All prompts for the Graph Generator are kept in `graph-generator/prompts.py` or alongside the extractor scripts. Please submit PRs with evaluation datasets if changing the strict Reviewer prompts.

### TypeScript / React
We use `eslint` and `prettier` for style. Ensure `npm run lint` passes before committing.

## 3. Pull Requests
1. Fork the repo and create your branch from `main`.
2. Add comprehensive descriptions to your PR regarding the feature or fix.
3. Ensure no API keys or `.env` files are accidentally committed.
