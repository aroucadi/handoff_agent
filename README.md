# Synapse — The Living Memory of Your Customer Journey

> **Gemini-powered multimodal voice agent** that transforms CRM data into real-time, grounded customer intelligence — with role-specific briefings, Google Search enrichment, and AI-generated artifacts.

[![Release](https://img.shields.io/badge/release-v2.0.0-blue)]()
[![Gemini](https://img.shields.io/badge/Gemini-3.1_Pro_%7C_2.5_Flash_Audio_%7C_Embedding_001-orange)]()
[![IaC](https://img.shields.io/badge/IaC-Terraform_with_GCP-purple)]()
[![CRM](https://img.shields.io/badge/CRM-Agnostic_%7C_HubSpot_%7C_Salesforce-green)]()

---

## What Is This?

Synapse is a **CRM-agnostic AI briefing platform** for B2B SaaS teams. It connects to any CRM via its **Hub integration layer**, extracts deal data into a structured **ontology-driven knowledge graph**, then serves it through a **Gemini Live multimodal voice agent** that Sales, CSM, Support, and Strategy teams can talk to before customer meetings.

### Key Capabilities

| Capability | Description |
|---|---|
| **Knowledge Graph** | Ontology-driven entity extraction (20+ node types, typed edges) from CRM data + static Knowledge Center |
| **4 Role Personas** | CSM, Sales, Support, Strategy — each with unique system prompts, vocabulary, and data focus |
| **13 ADK Tools** | 7 structured graph tools + 3 output generators + 3 legacy traversal tools |
| **6 Transcript Types** | Sales script, support script, QBR prep, renewal script, onboarding guide, discovery questions |
| **Google Search Grounding** | Enriches briefings with real-time industry trends and competitor data |
| **Versioned Artifacts** | AI-generated documents (briefings, action plans, risk reports) with version history |
| **Hub Integration** | Multi-tenant config portal — CRM-agnostic plug & play with custom branding |

### The Flow

1. **Connect CRM** via Hub → configure field mapping + branding
2. **Graph Generator** extracts entities with Gemini 3.1 Pro → builds ontology-driven knowledge graph → stores in Firestore
3. **User opens Synapse** → selects role → sees deals on Dashboard
4. **User clicks "Ground Context"** → real-time voice briefing with the agent
5. **Agent navigates the knowledge graph** using 13 tools + Google Search → provides grounded, never-hallucinated answers
6. **Smart Action Chips** → user or agent triggers artifact generation (scripts, reports, action plans)
7. **Artifacts visible on Dashboard** with version history, Markdown preview, and download

### Gemini Models Used

| Model | Purpose |
|---|---|
| `gemini-3.1-pro-preview` | Entity extraction, node generation, document generation |
| `gemini-embedding-001` | 768d vector embeddings for semantic search |
| `gemini-2.5-flash-native-audio-preview` | Real-time voice via Multimodal Live API |
| Google Search Grounding | Industry context enrichment during live sessions |

---

## 📚 Documentation Hub

- **[Developer Onboarding](docs/ONBOARDING.md)** — Monorepo structure, manifests, and cross-platform scripts
- **[Product Requirements Document (PRD)](docs/PRD.md)** — Vision and UX flows
- **[System Architecture](docs/ARCHITECTURE.md)** — Core design decisions, data flows, and knowledge graph ontology
- **[AI Agents Deep Dive](docs/AI_AGENTS.md)** — Agent tools, Google Search grounding, generative outputs, and role-aware prompts
- **[Cloud Infrastructure](docs/INFRASTRUCTURE.md)** — GCP Terraform diagrams and Cloud Run topologies
- **[API Reference](docs/API_REFERENCE.md)** — REST endpoints, WebSocket protocol, and Hub API
- **[Observability & Telemetry](docs/OBSERVABILITY.md)** — Agent tracing, token counting, and tool-call logging

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- A GCP project with Gemini API enabled

### Setup

```bash
# Clone
git clone https://github.com/aroucadi/handoff_agent.git
cd handoff_agent

# Install everything
bash scripts/demo-setup.sh

# Start all services
bash scripts/start-local.sh
```

### Access Points

| Service | URL |
|---|---|
| Hub (Tenant Config Portal) | http://localhost:5176 |
| Synapse Voice UI | http://localhost:5174 |
| Backend API | http://localhost:8000/health |
| Graph Generator | http://localhost:8002/health |
| CRM Simulator | http://localhost:5173 |
| Knowledge Center | http://localhost:3000 |

---

## Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system diagram.

```
Hub (Tenant Config)──→ Synapse API ←── CRM (HubSpot/Salesforce/Custom)
         │                  ↕                      ↓
         │            Gemini Live          Graph Generator
         │            (Voice + Search)     (Ontology Pipeline)
         │                  ↕                      ↓
         │            Voice UI ←── WebSocket    Firestore
         │                                    (Knowledge Graph)
         │                  ↕
         │            Smart Action Chips → Artifact Generation
         └────────────────────────────→ Dashboard (Artifact Viewer)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript 5, Vite 6, React Flow |
| Backend | Python 3.11, FastAPI, WebSockets |
| AI | Gemini 3.1 Pro, Embedding 001, 2.5 Flash Native Audio, Google Search Grounding |
| Infrastructure | Terraform, GCP (Cloud Run, GCS, Firestore, Secret Manager) |
| Hub | React + FastAPI — multi-tenant CRM integration portal |
| Knowledge Center | Static ClawdView product knowledge site |

---

## Project Structure

```
synapse/
├── hub/                        # Synapse Hub (Multi-Tenant Config Portal)
│   ├── api/                    # Hub CRUD API (tenants, CRM field mapping)
│   └── src/                    # Hub React Frontend
├── backend/                    # Synapse API (Core Voice Service)
│   ├── agent/                  # ADK agent (13 tools, 4 role prompts)
│   │   ├── prompts.py          # Role-specific system prompts + search policy
│   │   ├── tools.py            # 13 tool definitions + wrappers
│   │   └── synapse_agent.py    # Main agent runner
│   ├── graph/                  # Knowledge Graph Engine
│   │   ├── traversal.py        # Multi-hop typed entity traversal
│   │   ├── search.py           # Semantic search with type filters
│   │   ├── outputs.py          # 7 Gemini-powered document generators
│   │   └── ontology.py         # 20+ entity types, typed edge schema
│   └── live/                   # Gemini Live Session Handler
│       └── session.py          # Voice + Google Search + 13 tools
├── graph-generator/            # Graph Generator (Ontology Pipeline)
│   ├── extractors/             # CRM extractor + Knowledge Center extractor
│   └── main.py                 # Dual-pipeline: CRM + KB
├── knowledge-center/           # ClawdView Static Knowledge Site
├── frontend/                   # Synapse Voice UI (React + React Flow)
│   └── src/components/
│       ├── Dashboard.tsx        # Deal cards + artifact badges
│       ├── BriefingSession.tsx  # Voice session + graph panel
│       ├── ConversationPanel.tsx # Transcript + smart action chips
│       ├── ArtifactViewer.tsx   # Modal viewer with version history
│       └── GraphPanel.tsx       # Typed entity visualization
├── infra/                      # Terraform IaC
└── scripts/                    # deploy.ps1, start-local, teardown
```

---

## Infrastructure (Terraform)

All infrastructure is defined as code in `infra/`:

| Module | Resources |
|---|---|
| `storage` | GCS buckets (skill-graphs, uploads, knowledge-center) |
| `firestore` | Firestore database (native mode) — knowledge graphs, sessions, outputs |
| `cloud-run` | 4 Cloud Run services (API, Graph Generator, CRM Simulator, Hub) |
| `firebase` | Firebase Web App + Hosting |

### Deploy to GCP

```powershell
# Full deployment: containers, Terraform, Knowledge Center, Firebase Hosting
.\scripts\deploy.ps1 -ProjectId "YOUR_GCP_PROJECT_ID" -Region "us-central1"

# Teardown
.\scripts\teardown.ps1 -ProjectId "YOUR_GCP_PROJECT_ID" -Region "us-central1"
```

---

## Release History

| Version | What Shipped |
|---|---|
| `v0.1` | CRM Simulator, IaC base, 12 static skill graphs |
| `v1.0` | Demo polish, documentation, deployment scripts |
| `v1.4` | Native Firestore Vector Search |
| `v1.7` | Multimodal WebRTC screen sharing |
| `v1.9` | Hardened Terraform & PowerShell deployment |
| `v2.0` | **Hub Integration** — CRM-agnostic multi-tenant portal, field mapping, custom branding |
| `v2.1` | **Knowledge Center** — ClawdView static product knowledge site for KB enrichment |
| `v2.2` | **Ontology-Driven Graph** — 20+ entity types, typed edges, structured traversal |
| `v2.3` | **13 ADK Tools** — Structured graph tools, risk profiles, product knowledge |
| `v2.4` | **Generative Outputs** — 7 generators, 6 transcript types, versioned artifacts |
| `v2.5` | **Google Search Grounding** — Real-time industry enrichment, smart action chips |

---

## License

MIT
