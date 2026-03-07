# 🌌 ClawdView (by Synapse) — The Living Memory of Your Customer Journey

> **Gemini-powered multimodal voice agent** that transforms CRM data into real-time, grounded customer intelligence — with role-specific briefings, Google Search enrichment, and AI-generated enterprise artifacts.

---

### 🚨 Current System Status: Recovery Mode
Our Google Cloud Platform project is currently in **Recovery Mode** following a temporary account suspension. We have implemented aggressive anti-abuse safeguards and submitted a formal appeal to Google Trust & Safety.

**Progress:** 
- [x] Phase 11: Anti-Abuse Hardening (Rate-limiting, Semaphores, Crawler Boundaries)
- [x] Phase 12: Codebase Verification (Zero-surprise build audit)
- [x] Phase 22: Zero Adaptation (Generic Terminology & Role Mapping)
- [x] Phase 23: Closing the Normalization Gap (End-to-End Taxonomy Sync)

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
| **Synapse Hub** | [http://localhost:5176](http://localhost:5176) |
| **ClawdView Voice UI** | [http://localhost:5174](http://localhost:5174) |
| **CRM Simulator** | [http://localhost:5173](http://localhost:5173) |

---

## 🗺️ Project Structure

```text
synapse/
├── hub/             # Multi-Tenant Config Portal (React + FastAPI)
├── backend/         # Core Voice API & ADK Agent Engine
├── graph-generator/ # Extraction Pipeline (CRM + Knowledge Center)
├── frontend/        # ClawdView Voice UI (React + WebRTC)
├── crm-simulator/   # Mock Enterprise CRM (SalesClaw)
├── infra/           # Terraform IaC Modules
└── scripts/         # Deployment & Seeding Automation
```

---

## 📜 License
MIT © 2026 ClawdView Team
