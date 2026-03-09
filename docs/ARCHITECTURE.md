# Synapse — Architecture

## System Overview

```mermaid
graph LR
    subgraph External
        CRM["CRM (HubSpot/SF/Custom)"]
        KC["ClawdView Knowledge Center"]
        GS["Google Search"]
    end

    subgraph Admin ["Synapse Admin Portal"]
        AdminUI["Admin React UI"]
        AdminAPI["Admin FastAPI"]
    end

    subgraph Hub ["Synapse Hub"]
        HubUI["Hub React UI"]
        HubAPI["Hub FastAPI"]
    end

    subgraph Core ["Synapse Core (Cloud Run)"]
        API["Synapse API (FastAPI)"]
        GG["Graph Generator"]
        CRMSIM["CRM Simulator"]
    end

    subgraph AI ["Gemini Models"]
        PRO["Gemini 3.1 Pro"]
        LITE["Gemini 3.1 Flash Lite"]
        LIVE["Gemini Live 2.5 Flash"]
    end

    subgraph Storage ["Google Cloud"]
        FS["Firestore (KG + Outputs)"]
        GCS["Cloud Storage"]
    end

    subgraph Frontend ["Live Agent"]
        DASH["Dashboard"]
        BRIEF["Briefing Session"]
        AV["Artifact Viewer"]
    end

    CRM -->|Webhook/Sync| HubAPI
    HubAPI -->|Config| API
    HubUI --> HubAPI
    API -->|Session| LIVE
    API -->|Extract| GG
    GG -->|Entities| PRO
    GG -->|Embed| EMB
    GG -->|Store| FS
    KC -->|Crawl| GG
    LIVE -->|Search| GS
    LIVE -->|Tools| FS
    API -->|WebSocket| BRIEF
    DASH -->|Fetch| API
    AV -->|Outputs| API
    CRMSIM -->|Webhook| API

    subgraph Scripts ["Maintenance & Seeding"]
        CU["cleanup_db.py"]
        JR["journey_runner.py"]
        TP["test_pipeline.py"]
    end

    CU -->|Reset| FS
    CU -->|Reset| GCS
    JR -->|Onboard| AdminAPI
    JR -->|Seed| CRMSIM
    TP -->|Test| HubAPI
    TP -->|Verify| FS
    AdminAPI -->|Provision| HubAPI
```

---

## Multimodal Live Agent Flow

```mermaid
sequenceDiagram
    participant User as User (CSM/Sales/Support/Strategy)
    participant React as Live Agent UI
    participant API as Synapse API
    participant Hub as Hub API
    participant Gemini as Gemini Live API
    participant Search as Google Search
    participant KG as Firestore Knowledge Graph

    User->>React: Selects Role + Deal
    React->>API: POST /sessions/start (tenant_id, role, client_id)
    API->>Hub: Get Tenant Config (branding, prompts)
    Hub-->>API: Config Data

    React->>API: WebSocket Connect
    API->>Gemini: LiveConnect (14 tools + GoogleSearch)

    loop Voice Conversation
        User->>React: Speaks / Types / Clicks Smart Chip
        React->>API: Audio/Text via WebSocket
        API->>Gemini: Forward Audio

        alt Graph Tool Call
            Gemini->>API: Tool Call: get_entity("risk-001")
            API->>KG: Query Firestore
            KG-->>API: Entity Data
            API-->>Gemini: Tool Result
        else Google Search
            Gemini->>Search: Industry query
            Search-->>Gemini: Search results
        else Artifact Generation
            Gemini->>API: Tool Call: generate_briefing(client_id)
            API->>KG: Fetch graph data
            API->>Gemini: Generate document (3.1 Pro)
            API->>KG: Save versioned output
            API-->>Gemini: "Briefing v2 saved"
        else Web Search/Scrape
            Gemini->>Search: Google Search or Web Scrape tool
            Search-->>Gemini: Grounded content
        end

        Gemini-->>API: Audio Response
        API-->>React: WebSocket Audio
        React-->>User: Plays Synthesized Voice
    end
```

---

## Atlassian-Style Multi-Tenancy

Synapse uses a path-based workspace model (`/t/:slug`) ensuring ironclad isolation driven by cryptographic signatures.

Detailed Deep Dive: [MULTI_TENANCY.md](MULTI_TENANCY.md)

```mermaid
sequenceDiagram
    participant UI as Frontend (React)
    participant Hub as Hub API (Registry)
    participant Backend as Synapse Voice API
    
    UI->>Hub: GET /api/resolve-tenant?slug=acme
    Hub-->>UI: Config + Signed Token (HMAC)
    UI->>Backend: Request with Authorization: Bearer <token>
    Backend-->>Backend: Middleware Verify Signature
    Backend->>Backend: Access Firestore {tenant_id} context
```

---

## Ontology-Driven Graph Pipeline

This pipeline transforms raw, unformatted CRM objects and web pages into a structured knowledge net.

```mermaid
graph TD
    subgraph Ingress ["Ingress Engine"]
        W["Web Scraper (KC)"]
        C["CRM Scraper (SalesClaw)"]
    end

    subgraph Extraction ["GenAI Extraction Layer"]
        EX["Extractor Agent (Gemini 3.1 Pro)"]
        SEM["Semaphore Control (limit=3)"]
    end

    subgraph Transformation ["Ontology Processing"]
        TYP["Typed Node Construction (20+ types)"]
        EDG["Typed Edge Linking (15+ types)"]
    end

    subgraph Storage ["Persistent State"]
        FS["Firestore (NoSQL Nodes)"]
        VEC["Firestore Vector Search"]
    end

    Ingress --> SEM
    SEM --> EX
    EX --> TYP
    TYP --> EDG
    EDG --> FS
    FS --> VEC
```

---

## 🎙️ Multimodal Live Session Loop

The Live Agent (Gemini 2.5 Flash) operates in an immersive, low-latency loop that combines real-time sensory inputs with grounded knowledge.

```mermaid
graph LR
    subgraph Client ["Frontend (React)"]
        MIC["Audio (PCM)"]
        VSN["Vision (JPEG)"]
        UI["React Flow Dashboard"]
    end

    subgraph Backend ["Synapse API (Live)"]
        LIV["Gemini Live Session"]
        GND["Grounding Logic"]
        ADK["ADK Tools"]
    end

    subgraph Store ["Persistence"]
        FS["Firestore (Knowledge)"]
        GCS["GCS (Artifacts)"]
    end

    MIC -->|WSS| LIV
    VSN -->|WSS| LIV
    LIV <--> GND
    GND <--> ADK
    ADK <--> FS
    LIV -->|Trigger| GCS
    LIV -->|Audio Chunks| MIC
    FS -->|Active Node| UI
```

### Entity Types (Ontology & Terminology)

The system is terminology-agnostic. While the internal ontology uses these defaults, the Hub allows mapping "Account" to "Client", "Case" to "Deal", etc.

| Category | Types |
|---|---|
| **Core** | Account (Organization), Case (Deal), Contact |
| **Product** | Product, Feature, Limitation, Integration |
| **Risk** | Risk, CompetitorThreat, ChurnSignal |
| **Strategy** | SuccessMetric, Milestone, Timeline |
| **Knowledge** | KBArticle, BestPractice, UseCase |

### Edge Types

| Edge | From → To | Description |
|---|---|---|
| `HAS_RISK` | Client → Risk | Client-level risk |
| `INCLUDES` | Deal → Product | Products in deal |
| `CHAMPIONS` | Contact → Deal | Stakeholder advocacy |
| `USES_PRODUCT` | Client → Product | Current product usage |
| `MITIGATED_BY` | Risk → Feature | Risk mitigation |
| `DEPENDS_ON` | Integration → Product | Technical dependency |
| `COMPETES_WITH` | Product → Competitor | Competitive landscape |

---

## Gemini Models Used

| Model | Purpose | Where Used |
|---|---|---|
| `gemini-3.1-pro-preview` | Entity extraction, high-fidelity node generation | Graph Generator |
| `gemini-3.1-flash-lite-preview` | Thinking-enabled reasoning, document generation, agent summarization | Hub, Output Generators, ADK |
| `gemini-live-2.5-flash-native-audio` | Real-time voice (Multimodal Live API) | Backend Live Sessions |
| Google Search / Web Scrape | Industry context, real-time browsing, market trends | Live Sessions, Text Agent |

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 6, TypeScript 5, React Flow |
| **Live Agent** | React 19 + Gemini Live Agent |
| **Admin Portal** | React + FastAPI (Global oversight) |
| **Hub** | React + FastAPI (Tenant config portal) |
| **Backend API** | Python 3.11, FastAPI, WebSockets |
| **Graph Generator** | Python 3.11, FastAPI, Google GenAI SDK |
| **Knowledge Center** | Static HTML/CSS (ClawdView product docs) |
| **Infrastructure** | Terraform, GCP (Cloud Run, GCS, Firestore, Secret Manager) |
| **AI** | Gemini 3.1 Pro, Embedding 001, 2.5 Flash Native Audio, Google Search |

---

## Project Structure

```
synapse/
├── hub/                        # Synapse Hub (Multi-Tenant Config Portal)
│   ├── api/                    # Hub CRUD API (tenants, field mapping)
│   └── src/                    # Hub React Frontend
├── backend/                    # Synapse API (Core Voice Service)
│   ├── main.py                 # FastAPI + 30+ endpoints
│   ├── agent/                  # ADK Agent Engine
│   │   ├── prompts.py          # 4 role prompts + search policy
│   │   ├── tools.py            # 14 tool definitions + wrappers
│   │   └── synapse_agent.py    # Agent runner
│   ├── graph/                  # Knowledge Graph Engine
│   │   ├── ontology.py         # 20+ entity types, edge schema
│   │   ├── traversal.py        # Multi-hop typed traversal
│   │   ├── search.py           # Semantic search + type filters
│   │   └── outputs.py          # 7 generators, 6 transcripts, versioning
│   └── live/                   # Gemini Live Sessions
│       └── session.py          # Voice + GoogleSearch + 13 tools
├── graph-generator/            # Graph Generator (Ontology Pipeline)
│   ├── extractors/
│   │   ├── crm_extractor.py    # CRM entity extraction
│   │   └── kc_extractor.py     # Knowledge Center extraction
│   └── main.py                 # Dual-pipeline orchestrator
├── knowledge-center/           # ClawdView Static Knowledge Site
├── crm-simulator/              # Mock CRM (SalesClaw)
├── frontend/                   # Synapse Voice UI
│   └── src/components/
│       ├── Dashboard.tsx        # Deal cards + artifact badges
│       ├── BriefingSession.tsx  # Voice session orchestrator
│       ├── ConversationPanel.tsx # Smart action chips + transcript
│       ├── ArtifactViewer.tsx   # Version history + preview
│       └── GraphPanel.tsx       # Typed entity visualization
├── core/                       # Shared Config, Database access, and Normalization bridge
│   ├── config.py               # Global settings & model strategy
│   ├── db.py                   # Firestore/GCS handle management
│   └── normalization.py        # Centralized Stage & Product ID normalization logic (Phase 23)
├── infra/                      # Terraform (4 modules)
└── scripts/                    # Maintenance & Seeding Scripts
    ├── deploy.ps1              # Full Infra + App deployment
    ├── cleanup_db.py           # Atomic Firestore + GCS purge
    ├── journey_runner.py       # Tenant onboarding + demo seeding
    └── test_pipeline.py        # E2E integration verification
```

---

## Script Interoperability & Terraform Integration

The maintenance scripts are designed to work together as an atomic pipeline. They dynamically resolve infrastructure state using Terraform outputs to ensure consistency across environments.

### The "Perfect Run" Sequence
See [PERFECT_RUN.md](PERFECT_RUN.md) for the exact command sequence.

### Terraform Logic
The scripts utilize `terraform output -raw <variable>` to satisfy the following dependencies:
- **`hub_url`**: Used by `journey_runner.py` to target the correct multi-tenant entry point.
- **`crm_simulator_url`**: Used by both `journey_runner.py` and `test_pipeline.py` for deal simulation.
- **`firestore_database`**: Ensures `cleanup_db.py` targets the correct native-mode instance.
