# Synapse — Architecture

## System Overview

```mermaid
graph LR
    subgraph External
        CRM["CRM (HubSpot/SF/Custom)"]
        KC["ClawdView Knowledge Center"]
        GS["Google Search"]
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
        EMB["Embedding 001"]
        LIVE["2.5 Flash Native Audio"]
    end

    subgraph Storage ["Google Cloud"]
        FS["Firestore (KG + Outputs)"]
        GCS["Cloud Storage"]
    end

    subgraph Frontend ["Voice UI"]
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
```

---

## Multimodal Live Agent Flow

```mermaid
sequenceDiagram
    participant User as User (CSM/Sales/Support/Strategy)
    participant React as Voice UI
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
    API->>Gemini: LiveConnect (13 tools + GoogleSearch)

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
        end

        Gemini-->>API: Audio Response
        API-->>React: WebSocket Audio
        React-->>User: Plays Synthesized Voice
    end
```

---

## Ontology-Driven Graph Pipeline

```mermaid
graph TD
    subgraph Sources ["Data Sources"]
        CRM["CRM Data (via Hub)"]
        KC["Knowledge Center"]
        TR["Sales Transcripts"]
    end

    subgraph Extractors ["Extractor Agents"]
        CE["CRM Extractor"]
        KCE["Knowledge Center Extractor"]
    end

    subgraph Generator ["Graph Generator"]
        ONT["Ontology Schema (20+ types)"]
        GEN["Generator Agent (Gemini 3.1 Pro)"]
        REV["Reviewer Agent (QA)"]
    end

    subgraph Storage ["Firestore"]
        ENT["Typed Entities"]
        EDG["Typed Edges"]
        VEC["Vector Embeddings"]
        OUT["Versioned Outputs"]
    end

    CRM --> CE
    KC --> KCE
    TR --> CE
    CE -->|Entities + Relationships| GEN
    KCE -->|KB Articles + Products| GEN
    ONT -.->|Schema Validation| GEN
    GEN -->|Draft Nodes| REV
    REV -->|Validated Graph| ENT
    REV --> EDG
    ENT -->|Embed| VEC
    
    style ONT fill:#d4edda,stroke:#28a745
    style REV fill:#cce5ff,stroke:#007bff
```

### Entity Types (Ontology)

| Category | Types |
|---|---|
| **Core** | Client, Deal, Contact, Account |
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
| `gemini-3.1-pro-preview` | Entity extraction, node generation, document generation | Graph Generator, Output Generators |
| `gemini-embedding-001` | 768d vector embeddings for semantic search | Graph Generator, Backend |
| `gemini-2.5-flash-native-audio-preview` | Real-time voice (Multimodal Live API) | Backend Live Sessions |
| Google Search Grounding | Industry context, competitor data, market trends | Live Sessions (supplementary) |

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 6, TypeScript 5, React Flow |
| **Backend API** | Python 3.11, FastAPI, WebSockets |
| **Hub** | React + FastAPI (multi-tenant config portal) |
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
│   │   ├── tools.py            # 13 tool definitions + wrappers
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
├── core/                       # Shared Config + DB
├── infra/                      # Terraform (4 modules)
└── scripts/                    # deploy.ps1, start-local, teardown
```
