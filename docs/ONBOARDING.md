# 🚀 ClawdView (Synapse) Developer Onboarding Guide

Welcome to the **ClawdView** monorepo! This repository houses a Level 5 AI Voice Agent for Customer Success — a CRM-agnostic, multi-tenant briefing system powered by the **Synapse Core Engine (Gemini 3.1 Pro + 2.5 Flash)**.

---

## 1. Monorepo Repository Structure

```text
synapse/
├── hub/                    # (UI + API) Tenant Configuration Hub — CRM-agnostic portal
├── backend/                # (Microservice) Core Voice API — 13 ADK tools, Live sessions
│   ├── agent/              # Agent engine: prompts, tools, system instructions
│   ├── graph/              # Knowledge graph: ontology, traversal, search, output generators
│   └── live/               # Gemini Live session handler (voice + Google Search)
├── graph-generator/        # (Microservice) Ontology-driven graph pipeline
│   └── extractors/         # CRM extractor + Knowledge Center extractor
├── crm-simulator/          # (Microservice) SalesClaw mock CRM
├── frontend/               # (UI) Multi-role Voice UI (Dashboard, Briefing, ArtifactViewer)
├── knowledge-center/       # (Static) ClawdView product knowledge site
├── core/                   # (Shared) Config, DB, models
├── infra/                  # (IaC) GCP Terraform modules (4 modules)
├── scripts/                # One-click automation (deploy, teardown, start-local)
└── synapse.yaml            # Global Monorepo Manifest
```

> **Developer Note:** The Python microservices (`backend/`, `crm-simulator/`, `graph-generator/`) all depend on the shared `core/` package. Docker builds use the **root** as build context so `core/` is mounted into each container.

---

## 2. Key Components

| Component | Stack | Purpose |
|---|---|---|
| **Hub** | React + FastAPI | Multi-tenant config: CRM field mapping, branding, role config |
| **Backend** | FastAPI + WebSockets | Voice sessions, 13 ADK tools, 7 output generators, REST API |
| **Graph Generator** | FastAPI + Gemini 3.1 Pro | Ontology-driven entity extraction (20+ types, typed edges) |
| **Knowledge Center** | Static HTML/CSS | ClawdView product docs — crawled by graph generator for KB enrichment |
| **Frontend** | React 19 + React Flow | Dashboard, voice briefing, smart action chips, artifact viewer |
| **CRM Simulator** | FastAPI + React | Mock CRM for demos (replaceable via Hub with real CRM) |

---

## 3. The Monorepo Manifest (`synapse.yaml`)

We use a Root Manifest for cross-service coordination:

- **Global Versioning**: Unified version across all sub-components. Run `bash scripts/bump-version.sh` after updating `global_version` in `synapse.yaml`.
- **Infrastructure IDs**: Contains `gcp_project` and `firebase_project` identifiers for CI/CD.

---

## 4. Automation Scripts (`scripts/`)

| Script | Purpose | Example |
|---|---|---|
| `deploy.ps1` | Full GCP deployment (Cloud Build → Terraform → Firebase) | `.\scripts\deploy.ps1 -ProjectId "my-project"` |
| `teardown.ps1` | Destroy all GCP resources | `.\scripts\teardown.ps1 -ProjectId "my-project"` |
| `start-local.ps1` | Spin up all services locally | `.\scripts\start-local.ps1` |
| `demo-setup.ps1` | Install all dependencies | `.\scripts\demo-setup.ps1` |
| `bump-version` | Propagate version globally | `py scripts/bump-version.py` |

---

## 5. Quick Start (Local Development)

```bash
# 1. Install dependencies
.\scripts\demo-setup.ps1

# 2. Set your API key
$env:GEMINI_API_KEY = "your-key-here"

# 3. Start all services
.\scripts\start-local.ps1

# 4. Open services
# Hub:             http://localhost:5176
# Voice UI:        http://localhost:5174
# Backend API:     http://localhost:8000/health
# Graph Generator: http://localhost:8002/health
# CRM Simulator:   http://localhost:5173
# Knowledge Center: http://localhost:3000
```

---

## Where to go next?

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) — System diagrams and data flow
- **AI Agents**: [AI_AGENTS.md](AI_AGENTS.md) — 13 tools, Google Search, 7 generators, 4 role personas
- **GCP Safety**: [CLAWVIEW_GCP_SURVIVAL.md](CLAWVIEW_GCP_SURVIVAL.md) — Safeguards against API abuse
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md) — All REST endpoints and WebSocket protocol
- **Infrastructure**: [INFRASTRUCTURE.md](INFRASTRUCTURE.md) — GCP Terraform modules and deployment pipeline
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md) — Code style, PR process, testing
