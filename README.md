# HANDOFF

**Gemini Live Agent Challenge Submission**

> When a B2B SaaS deal closes, Handoff automatically generates a traversable client skill graph and enables Customer Success Managers to get real-time, grounded voice briefings before kickoff calls — powered by Gemini Live.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Cloud SDK (`gcloud`)
- Terraform 1.5+
- A GCP project with billing enabled
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd handoff
cp infra/terraform.tfvars.example infra/terraform.tfvars
# Edit terraform.tfvars with your GCP project ID
```

### 2. Set Up API Key

```bash
export GEMINI_API_KEY="your-api-key-from-ai-studio"
```

### 3. Deploy Infrastructure

```bash
cd infra
terraform init
terraform apply
cd ..
```

### 4. Start the CRM Simulator

```bash
cd crm-simulator
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

In a separate terminal:
```bash
cd crm-simulator/frontend
npm install
npm run dev
```

### 5. Start the Handoff Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Seed Static Graphs

```bash
./scripts/seed-graphs.sh
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system diagram.

## Project Structure

```
handoff/
├── infra/              ← Terraform IaC
├── backend/            ← FastAPI + ADK agent
├── graph-generator/    ← Skill graph generation service
├── crm-simulator/      ← CRM Simulator web app
├── skill-graphs/       ← Pre-built product & industry knowledge
├── frontend/           ← React briefing UI
└── scripts/            ← Deployment & setup scripts
```

## Tech Stack

- **Models**: Gemini 3.1 Pro, Gemini 2.5 Flash Native Audio, Gemini 3 Flash, gemini-embedding-001
- **Backend**: Python, FastAPI, Google ADK
- **Frontend**: React, TypeScript, Vite, React Flow
- **Infra**: GCP (Cloud Run, GCS, Firestore, Firebase Hosting), Terraform

---

*Built for the Gemini Live Agent Challenge | Deadline: March 16, 2026*
