# Handoff — AI Voice Agent for B2B SaaS Customer Success

> **Gemini-powered voice agent** that transforms CRM deal closure into real-time, grounded customer success briefings.

[![Release](https://img.shields.io/badge/release-v1.0.0-blue)]()
[![Gemini](https://img.shields.io/badge/Gemini-3.1_Pro_%7C_2.5_Flash_Audio_%7C_Embedding_001-orange)]()
[![IaC](https://img.shields.io/badge/IaC-Terraform_with_GCP-purple)]()

---

## What Is This?

When a B2B SaaS deal closes, critical context is trapped in CRM data and sales transcripts. Handoff uses **Gemini 3.1 Pro** to extract that knowledge into a navigable **skill graph**, then serves it through a **Gemini Live voice agent** that Customer Success Managers can talk to before their kickoff call.

### The Demo Flow

1. **CSM closes a deal** in the CRM Simulator → webhook fires
2. **Graph Generator** extracts entities with Gemini 3.1 Pro → creates 8 client-specific knowledge nodes → stores in GCS → indexes with embeddings in Firestore
3. **CSM opens Handoff** → sees account ready on Dashboard
4. **CSM clicks "Start Briefing"** → real-time voice conversation with the agent
5. **Agent navigates the skill graph** using 3 tools (read_index, follow_link, search_graph) → provides grounded, never-hallucinated answers
6. **Split-screen UI** shows live transcript + React Flow graph topology animating in real-time

### Gemini Models Used

| Model | Purpose |
|---|---|
| `gemini-3.1-pro-preview` | Entity extraction + node generation |
| `gemini-embedding-001` | 768d vector embeddings for semantic search |
| `gemini-2.0-flash-exp` | Real-time multimodal (Vision + Voice) via Live API |
| `gemini-2.5-flash-native-audio-preview` | Voice-only fallback |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- A Gemini API key ([Google AI Studio](https://aistudio.google.com/))

### Setup

```bash
# Clone
git clone https://github.com/aroucadi/handoff_agent.git
cd handoff_agent

# Set your API key
export GEMINI_API_KEY="your-key-here"

# Install everything
bash scripts/demo-setup.sh

# Start all services
bash scripts/start-local.sh
```

### Access Points

| Service | URL |
|---|---|
| CRM Simulator | http://localhost:5173 |
| Handoff Voice UI | http://localhost:5174 |
| Backend API | http://localhost:8000/health |
| Graph Generator | http://localhost:8002/health |

### Demo Walkthrough

1. Open **CRM Simulator** → click "Closed Won" on a deal
2. Open **Handoff Voice UI** → enter the deal ID → click "Start Briefing"
3. Talk to the agent or type questions
4. Watch the React Flow graph animate as the agent navigates nodes

### Keyboard Shortcuts

| Key | Action |
|---|---|
| **Space** | Toggle microphone on/off |
| **Escape** | End briefing session |
| **Enter** | Send text message |

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system diagram.

```
CRM Simulator → webhook → Handoff API → Graph Generator
                                ↕                 ↓
                          Gemini Live        GCS + Firestore
                          (voice)            (skill graphs)
                                ↕
                          Voice UI ←── WebSocket (bidirectional audio)
```

---

## Project Structure

```
handoff/
├── backend/                # Handoff API (FastAPI)
│   ├── agent/              # ADK agent (tools, prompts, handoff_agent)
│   ├── graph/              # Graph traversal engine
│   └── live/               # Gemini Live session handler
├── graph-generator/        # Graph Generator (FastAPI)
│   └── extractors/         # Gemini 3.1 Pro entity extraction
├── crm-simulator/          # CRM Simulator (FastAPI + React)
├── frontend/               # Handoff Voice UI (React + React Flow)
├── skill-graphs/           # 12 static knowledge nodes
├── infra/                  # Terraform IaC (4 modules)
└── scripts/                # Deploy, demo-setup, start-local
```

---

## Infrastructure (Terraform)

All infrastructure is defined as code in `infra/`:

| Module | Resources |
|---|---|
| `storage` | GCS buckets (skill-graphs + uploads) |
| `firestore` | Firestore database (native mode) |
| `cloud-run` | 2 Cloud Run services, Artifact Registry, IAM |
| `firebase` | Firebase Web App |

### Deploy to GCP

To deploy the entire architecture (Frontend, FastAPIs, Cloud Run, Firestore, Storage) to Google Cloud, you need a GCP Project ID where you have billing and owner permissions.

We have provided one-click PowerShell scripts to handle the Docker builds, Terraform execution, and Firebase deployment.

```powershell
# 1. Open PowerShell and run the deployment script, passing your GCP Project ID:
.\scripts\deploy.ps1 -ProjectId "YOUR_GCP_PROJECT_ID" -Region "us-central1"

# 2. To completely destroy the environment and avoid billing:
.\scripts\teardown.ps1 -ProjectId "YOUR_GCP_PROJECT_ID" -Region "us-central1"
```

See [DEPLOYMENT_PROOF.md](DEPLOYMENT_PROOF.md) for full infrastructure details.

---

## Release History

| Version | Release | What Shipped |
|---|---|---|
| `v0.1.0` | R0 — Foundation | CRM Simulator, IaC base, 12 static skill graphs |
| `v1.0.0` | R4 — Submission | Demo polish, documentation, deployment scripts |
| `v1.4.0` | R8 — Grounding | Native Firestore Vector Search (`FindNearest`) |
| `v1.6.0` | R10 — Telemetry | Asynchronous `core/telemetry.py` traces |
| `v1.7.0` | R11 — Vision | Multimodal WebRTC screen sharing |
| `v1.8.0` | R12 — Polish | Global exception handlers and architecture diagrams |
| `v1.9.0` | R13 — IaC | Hardened Terraform & PowerShell deployment scripts |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript 5, Vite 6, React Flow |
| Backend | Python 3.11, FastAPI, WebSockets |
| AI | Gemini 3.1 Pro, Embedding 001, 2.5 Flash Native Audio |
| Infrastructure | Terraform, GCP (Cloud Run, GCS, Firestore, Secret Manager) |

---

## License

MIT
