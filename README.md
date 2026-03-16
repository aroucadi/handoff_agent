# 🌌 ClawdView (by Synapse) — The Living Memory of Your Customer Journey

> **Gemini-powered multimodal voice agent** that transforms CRM data into real-time, grounded customer intelligence — with role-specific briefings, Google Search enrichment, and AI-generated enterprise artifacts.

---

### ✅ System Status: Production Ready (Hardened)
The Synapse ecosystem has been fully hardened with "Ironclad" multi-tenancy and zero-fallback administrative security.

**Recent Hardening Highlights:**
- [x] **Fail-Closed Admin Auth**: Removed all hardcoded fallbacks in services and automation; system refuses to operate if unconfigured.
- [x] **Isolated Workflow Execution**: All protected deal data, graph traversals, and voice sessions require valid, cryptographically signed tenant context.
- [x] **Secure Discovery Bootstrap**: Explicit separation between public tenant resolution (slug-to-config) and private data access (token-gated).
- [x] **Protected Sync Monitoring**: All extraction metadata and status endpoints are hidden behind Master Admin authorization.

---

## 💡 What Is ClawdView?

ClawdView is a **CRM-agnostic AI briefing platform** for B2B SaaS teams. It connects to any CRM via the **Hub integration layer**, extracts deal data into a structured **ontology-driven knowledge graph**, and serves it through a **Gemini Live multimodal voice agent**.

### ✨ Core Capabilities

| Feature | Description |
|---|---|
| **🧠 Knowledge Graph** | 20+ entity types (Risks, Milestones, Products) extracted with **Gemini 3.1 Pro**. |
| **🎙️ Live Briefings** | Low-latency voice sessions using **Gemini Live 2.5 Flash**. |
| **🎭 Zero Adaptation** | Workflow-agnostic architecture: override terminology (**Account**, **Case**) and mapped roles. |
| **🌍 Search Grounding** | Real-time industry enrichment via Google Search. |
| **📄 Smart Artifacts** | Generate MSAs, SLAs, and Discovery Guides with **Thinking-enabled** reasoning (3.1 Flash Lite). |
| **🔌 Hub Portal** | Multi-tenant integration portal for CRM field mapping, stage normalization, and brand mapping. |

---

## 🛠️ Tech Stack

- **AI Engine**: Gemini 3.1 Pro (Extraction), Gemini 3.1 Flash Lite (Thinking/Artifacts), Gemini 2.5 Flash (Voice).
- **Frontend**: React 19, Vite 6, Tailwind CSS, Lucide icons.
- **Backend**: Python 3.11, FastAPI, WebSockets.
- **Infrastructure**: Terraform, GCP (Cloud Run, GCS, Firestore).

---

## 📚 Documentation Hub

Explore our comprehensive guides to get the most out of ClawdView:

### 🏁 Getting Started
- **[Zero-Knowledge Setup Guide](docs/SETUP_GUIDE.md)** — From zero to deployed in 10 minutes.
- **[Developer Onboarding](docs/ONBOARDING.md)** — Monorepo layout and local environment variables.
- **[Automation Scripts](docs/SCRIPTS.md)** — Detailed guide to all 20+ PowerShell and Python utilities.

### 🏗️ Architecture & AI
- **[System Architecture](docs/ARCHITECTURE.md)** — Deep dive into the Hub, GraphQL pipeline, and Voice WebSocket flow.
- **[GCP Survival / Safety](docs/CLAWVIEW_GCP_SURVIVAL.md)** — How we prevent API abuse and account suspensions.
- **[API Reference](docs/API_REFERENCE.md)** — Endpoints for Hub, Sync, and Voice sessions.

### 📝 Product & Strategy
- **[PRD & Vision](docs/PRD.md)** — The "Big Picture" and user journey maps.
- **[Demo Scripts](docs/DEMO_SCRIPT.md)** — Step-by-step instructions for a perfect stakeholder presentation.

---

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- GCP CLI (`gcloud auth login`)
- [Gemini API Key](https://aistudio.google.com/)

### 2. Launch
```powershell
# Install everything
.\scripts\demo-setup.ps1

# Set Key
$env:GEMINI_API_KEY = "your_key"

# Start All
.\scripts\start-local.ps1
```

### 3. Access
| Portal | URL |
|---|---|
| **Synapse Admin** | [http://localhost:5177](http://localhost:5177) |
| **Synapse Hub** | [http://localhost:5176](http://localhost:5176) |
| **Live Agent UI** | [http://localhost:5174](http://localhost:5174) |
| **CRM Simulator** | [http://localhost:5173](http://localhost:5173) |

---

## 🗺️ Project Structure

```text
synapse/
├── admin-portal/    # Global Registry & Provisioning (React + FastAPI)
├── hub/             # Tenant Config Portal (React + FastAPI)
├── live-agent/      # Synapse Live Agent UI (React + WebRTC)
├── backend/         # Core Voice API & ADK Agent Engine
├── graph-generator/ # Extraction Pipeline (CRM + Knowledge Center)
├── crm-simulator/   # Mock Enterprise CRM (SalesClaw)
├── infra/           # Terraform IaC Modules
└── scripts/         # Deployment & Seeding Automation
```

---

## 📜 License
MIT © 2026 ClawdView Team
