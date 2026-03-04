# SYNAPSE — Product Requirements Document
### Gemini Live Agent Challenge Submission
**Version**: 3.0 | **Date**: February 2026 | **Status**: Hackathon Final Candidate

> [!IMPORTANT]
> **v3.0 Enhancements (Level 5 Agentic AI)**: Upgraded the core interaction model to **Gemini 2.0 Flash Exp** to unlock purely Multimodal (Vision + Voice) WebRTC capabilities. Added asynchronous `core/telemetry` for agent observability. Replaced static local indexes with a production-grade **Firestore Native Vector Search**. Added complete `infra/` **Terraform IaC** for one-click GCP deployment.

---

> **TL;DR**: This PRD describes "Synapse" — a Level 5 Multimodal Agent that automatically generates a traversable skill graph when a B2B SaaS deal closes. It enables Customer Success Managers to get real-time, grounded voice and vision briefings before client kickoff calls. Using screen-sharing, the agent can "see" the CRM and discuss it aloud without hallucinating, thanks to underlying Graph Grounding logic.

---

## Table of Contents

1. [Vision & Problem Statement](#1-vision--problem-statement)
2. [Hackathon Alignment](#2-hackathon-alignment)
3. [Use Case: The CSM Briefing Loop](#3-use-case-the-csm-briefing-loop)
4. [Product Architecture](#4-product-architecture)
5. [Skill Graph Design (The Knowledge Core)](#5-skill-graph-design-the-knowledge-core)
6. [Feature Specifications](#6-feature-specifications)
7. [Gemini Model Strategy](#7-gemini-model-strategy)
8. [Technical Stack](#8-technical-stack)
9. [Google Cloud Infrastructure & IaC](#9-google-cloud-infrastructure--iac)
10. [API & Integration Specs](#10-api--integration-specs)
11. [Demo Script (4-Minute Video)](#11-demo-script-4-minute-video)
12. [Architecture Diagram Spec](#12-architecture-diagram-spec)
13. [File & Folder Structure](#13-file--folder-structure)
14. [Antigravity Skills for This Project](#14-antigravity-skills-for-this-project)
15. [Build Order & Milestones](#15-build-order--milestones)
16. [Judging Criteria Mapping](#16-judging-criteria-mapping)
17. [Future Lifecycle Expansion (Post-Hackathon)](#17-future-lifecycle-expansion-post-hackathon)

---

## 1. Vision & Problem Statement

### The Problem

When a B2B SaaS deal closes, a massive knowledge transfer problem occurs. The sales team spent months learning everything about the client — their pain points, internal politics, budget justification, technical constraints, and the specific promises made during the sales cycle. When the deal is marked "Closed Won," that institutional knowledge fragments: it lives in call recordings, CRM notes, email threads, and the salesperson's head.

The Customer Success Manager assigned to the account has 48 hours before the kickoff call. They inherit a folder of documents, a CRM record, and a brief verbal synapse. The result is bad onboarding, slow time-to-value, and ultimately — churn. Gartner identifies poor onboarding as the #1 driver of year-1 SaaS churn.

### The Solution

**Synapse** is a Level 5 Multimodal Live agent that:
1. **Automatically generates** a traversable client skill graph when a deal closes in the CRM
2. **Enables real-time voice and vision conversations**: CSMs share their screen and ask questions. The agent "sees" the UI and traverses the graph to give grounded answers.
3. **Never hallucinates** because every answer is grounded in the actual skill graph nodes — product docs, industry context, client-specific data, and deal history.

### The Core Insight (from Skill Graph Architecture)

Instead of dumping all knowledge into one prompt, Synapse uses a **skill graph** — a network of interconnected markdown files with YAML frontmatter and wikilinks. The Gemini Live agent navigates this graph progressively during the voice conversation, pulling only what's relevant. This is the difference between an agent that follows instructions and one that **understands a domain**.

---

## 2. Hackathon Alignment

| Requirement | How Synapse Satisfies It |
|---|---|
| Gemini Live API | Core voice/vision interaction layer — CSM speaks & shares screen, agent listens, sees, and responds in real-time |
| Google GenAI SDK | ADK orchestrates the graph traversal agent's function calling |
| Google Cloud hosting | Full GCP deployment via Terraform: Cloud Run, Cloud Storage, Firestore Vector Search |
| Multimodal input/output | Voice input + Video frame input (1 FPS) + Visual graph traversal output on split-screen UI |
| Moves beyond text-box | Real-time multimodal conversation grounded in a dynamically generated knowledge graph |
| Category fit | **Live Agents** — real-time interaction with audio, vision, and contextual intelligence |
| Innovation (40% of score) | Screen-aware skill graph navigation is architecturally novel; no hallucination by design |
| Technical execution (30%) | ADK + Firestore Vector Search + Telemetry + IaC = clean, production-grade architecture |
| Demo quality (30%) | 3-scene demo showing deal close → graph generation → live CSM briefing |

**Target prizes**: Grand Prize ($25K) + Best of Live Agents ($10K) + Best Technical Execution ($5K)

---

## 3. Use Case: The CSM Briefing Loop

### Persona
**Alex**, a Customer Success Manager at "VeloSaaS" (a fictional enterprise CRM vendor, Salesforce-inspired). Alex gets assigned a new account 48 hours before the kickoff call.

### The Scenario

**Trigger**: A $2M deal with "GlobalManufacturing Co." moves to "Closed Won" in VeloSaaS's CRM.

**Step 1 — Automatic Graph Generation** (background, ~2 minutes):
The system webhook fires. A Cloud Run job reads the CRM record, contract PDF, and sales call transcript. It generates a client-specific skill graph: 15–20 markdown nodes covering the client profile, negotiated scope, industry context, stakeholder map, risk flags, and success metrics.

**Step 2 — CSM Briefing** (voice, ~10 minutes before kickoff):
Alex opens the Synapse web app. Sees the GlobalManufacturing graph is ready. Clicks "Start Briefing." The Gemini Live agent begins: *"Hi Alex, your kickoff with GlobalManufacturing is tomorrow. Want me to walk you through the key things you need to know?"*

Alex speaks naturally: *"Yes, start with who I'm going to be talking to and what they care about."*

The agent traverses: `client-index → stakeholder-map → vp-sales-ops-profile → deal-context`

Agent responds: *"Your main contact is Sarah Chen, VP of Sales Operations. She championed this deal internally because the current CPQ process is causing 3-week delays on custom quotes. Her success metric is getting that down to 48 hours. The economic buyer who signed off is the CFO, Marcus Webb — he cares about ROI and was sold on a 6-month payback period..."*

**Step 3 — Risk Surfacing**:
Alex: *"Any risks I should know about?"*

Agent traverses: `risk-flags → implementation-timeline-risk → integration-complexity`

Agent: *"Two flags. First, the 90-day go-live SLA is aggressive for a company with their ERP complexity — similar manufacturing clients averaged 120 days. You'll want to set expectations early. Second, they have a legacy SAP integration that wasn't fully scoped in the contract — this came up in the last sales call but wasn't resolved..."*

### The Magic
Every answer is traceable to a specific graph node. No hallucination. Alex walks into kickoff knowing exactly what matters.

---

## 4. Product Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SYNAPSE SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CRM (VeloSaaS / Salesforce-mock)                              │
│       │                                                         │
│       │ Closed Won webhook                                      │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          GRAPH GENERATOR (Cloud Run Job)                 │   │
│  │  - Reads CRM data, contract PDF, sales transcripts       │   │
│  │  - Uses Gemini 3.1 Pro to extract structured data        │   │
│  │  - Generates markdown skill graph nodes                   │   │
│  │  - Writes to Cloud Storage + indexes in Firestore         │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │  SKILL GRAPH     │    │    GRAPH TRAVERSAL ENGINE        │   │
│  │  Cloud Storage   │◄───│    (ADK Agent + 3 tools)         │   │
│  │                  │    │    - read_index()                 │   │
│  │  Layer 1: Product│    │    - follow_link(node_id)        │   │
│  │  Layer 2: Industry│   │    - search_graph(query)         │   │
│  │  Layer 3: Client │    └──────────────────────────────────┘   │
│  └─────────────────┘              │                             │
│                                   │                             │
│                          ┌────────▼─────────┐                  │
│                          │  GEMINI LIVE API   │                  │
│                          │  Real-time voice   │                  │
│                          │  bidirectional     │                  │
│                          └────────┬─────────┘                  │
│                                   │                             │
│                          ┌────────▼─────────┐                  │
│                          │   CSM INTERFACE   │                  │
│                          │   Split-screen:   │                  │
│                          │   Voice | Graph   │                  │
│                          └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### Three-Layer Skill Graph Schema

```
Layer 1 — Product Knowledge Graph (static, pre-built)
  velosaaas-product/
  ├── index.md                    ← MOC: entry point
  ├── cpq-module.md
  ├── revenue-cloud.md
  ├── implementation-patterns.md
  ├── common-failure-modes.md
  ├── integration-gotchas.md
  └── typical-timelines.md

Layer 2 — Industry Knowledge Graph (static, pre-built)
  industries/
  ├── index.md                    ← MOC: industry map
  ├── manufacturing/
  │   ├── index.md
  │   ├── cpq-complexity.md
  │   ├── erp-integration-patterns.md
  │   └── common-pain-points.md
  └── financial-services/
      └── ...

Layer 3 — Account Knowledge Graph (Delta-based, evolving per deal)
  accounts/{account-id}/
  ├── account-profile.md          ← Core account identity
  ├── stakeholder-map.md          ← Dynamic hierarchy across deals
  ├── historical-deals/           # Folder for deal-specific deltas
  │   ├── opp-2025-win.md
  │   └── current-delta-node.md    ← The latest deal extraction
  ├── risk-history.md             ← Cumulative risk flags
  └── success-metrics-delta.md    ← Historical vs current targets
```

**YAML frontmatter schema for every node:**
```yaml
---
title: "Stakeholder Map — GlobalManufacturing Co."
node_id: "gmc-stakeholder-map"
client_id: "global-manufacturing-co"
layer: "client"                          # product | industry | client
stage: ["onboarding"]                    # sales | onboarding | implementation | support | renewal
domain: "manufacturing"
links:
  - deal-context
  - vp-sales-ops-profile
  - risk-flags
description: "Stakeholder roles, champions, economic buyers, and political dynamics for this account. Use when preparing for any client interaction."
last_updated: "2026-02-20"
---
```

---

## 5. Skill Graph Design (The Knowledge Core)

### Progressive Disclosure Pattern

The agent follows this traversal hierarchy, exactly mirroring the arscontexta/Heinrich skill graph pattern:

```
1. index.md          → scan YAML descriptions + link labels (no full read)
2. MOC nodes         → understand sub-topic landscape
3. Follow links      → read relevant nodes based on query intent
4. Sections          → pull specific sections if node is long
5. Full content      → only when precision is required
```

### Wikilink Conventions

Links are woven into prose so they carry semantic meaning:

```markdown
The VP of Sales Operations [[sarah-chen-profile]] is the internal champion 
who drove this deal. Her primary concern is reducing quote cycle time, 
which connects directly to the [[cpq-implementation-timeline]] and the 
aggressive [[90-day-go-live-sla]] that was negotiated.
```

### MOC (Map of Content) Pattern

Every layer starts with an index that acts as an entry point, not a lookup table:

```markdown
---
title: "GlobalManufacturing Co. — Onboarding Index"
node_id: "gmc-index"
layer: "client"
stage: ["onboarding"]
description: "Entry point for all GlobalManufacturing Co. knowledge. Start here. Navigate to stakeholders, deal context, product scope, risks, or success metrics."
---

# GlobalManufacturing Co.

Manufacturing conglomerate, 500 employees, midwest US. Closed $2M VeloSaaS CPQ + Revenue Cloud deal February 2026.

## Quick Navigation

- [[client-profile]] — Company background, size, industry, tech stack
- [[stakeholder-map]] — Who's who: champion, economic buyer, blockers
- [[deal-context]] — Why they bought, what was promised, sales cycle highlights
- [[negotiated-scope]] — Exact modules, users, SLAs in the contract
- [[success-metrics]] — What "win" looks like for them and for us
- [[risk-flags]] — Implementation risks, unresolved issues, timeline concerns

## Cross-Layer Links

- [[manufacturing/cpq-complexity]] — Industry context for their use case
- [[velosaaas/cpq-module]] — Product capability reference
```

---

## 6. Feature Specifications

**Feature 1: Delta Graph Generator & Account Weaver**

**Description**: When a deal closes, the generator doesn't just create a new graph—it weaves a **Delta** into the existing **Account Knowledge Graph**. It reads historical deal nodes to ensure continuity and avoids redundant "Account Profile" generation.

**Inputs**:
- CRM deal record & historical context
- Contract PDF & Sales Transcripts

**Process**:
1. **Account Context Retrieval**: Fetch existing `account-profile.md` and `risk-history.md`.
2. **Delta Extraction**: Gemini 3.1 Pro identifies *new* stakeholders, *new* technical requirements, and *changes* in project scope.
3. **Graph Weaving**: Generate "Delta Nodes" (e.g., `deal-xyz-brief.md`) and update wikilinks in the core `account-profile.md` to point to the new historical deal record.
4. **Vector Sync**: Embed only the new delta content and update the Firestore index with `_tenant_id` and `_account_id` sharding.

**Fallback**: If Gemini 3.1 Pro is rate-limited or unavailable, fall back to Gemini 3 Flash (`gemini-3.0-flash`) for extraction — faster but slightly less accurate on complex contracts

**Output**: Complete client skill graph ready for traversal

**Error handling**: If transcript or contract is missing, generate partial graph with placeholder nodes marked `status: incomplete`

---

### Feature 2: Graph Traversal Engine (ADK Agent Tools)

**Description**: Three ADK tools that the Gemini Live agent calls during conversation to navigate the skill graph.

**Tool 1: `read_index`**
```python
def read_index(client_id: str, layer: str = "all") -> dict:
    """
    Reads the index/MOC node for a client's skill graph.
    Returns node titles, descriptions, and link structure.
    Used at conversation start to understand the knowledge landscape.
    """
```

**Tool 2: `follow_link`**
```python
def follow_link(client_id: str, node_id: str, sections_only: bool = False) -> dict:
    """
    Reads a specific skill graph node by node_id.
    If sections_only=True, returns only H2 headers for progressive disclosure.
    Returns full markdown content and linked node IDs.
    """
```

**Tool 3: `search_graph`**
```python
def search_graph(client_id: str, query: str, layers: list = ["client", "industry", "product"]) -> list:
    """
    Semantic search across all graph nodes using Firestore + embeddings.
    Returns ranked list of relevant node_ids and their descriptions.
    Use when the user's question doesn't match an obvious navigation path.
    """
```

**ADK Agent System Prompt** (Multi-tenant & Multi-role):
```
You are Synapse, an expert briefing agent (Role: {role}) for Tenant: {tenant_name}.
You are assisting {user_name} with Account: {account_name}.

Your Persona Protocol:
1. If Role=CSM: Prioritize success metrics, account health, and ROI.
2. If Role=Sales: Prioritize expansion signals, historical deal blockers, and economic buyers.
3. If Role=WinBack: Prioritize risk mitigation, historical objections, and emotional sentiment.
4. If Role=Support: Prioritize technical specifications, SLAs, and legacy integration hurdles.

Your Traversal Protocol:
1. Start with read_index(). Look for [[delta-nodes]] from the latest deal.
2. Traverse from [[account-profile]] to specific deal history for deep context.
3. Proactively surface "Account Drift" (differences between sales promises and implementation reality).
```

---

### Feature 3: Gemini Live Voice Interface

**Description**: Real-time bidirectional voice conversation using Gemini Live API, with ADK agent handling graph traversal in the background.

**Session lifecycle**:
1. CSM opens Synapse app → selects assigned client → clicks "Start Briefing"
2. WebSocket connection opened to Gemini Live API
3. ADK agent initialized with client context + graph traversal tools
4. Microphone stream begins → continuous audio capture
5. Gemini Live transcribes + understands intent → calls ADK agent tools → synthesizes spoken response
6. Session ends when CSM clicks "End Briefing" or natural conversation close

**Voice behavior requirements**:
- Interruptible: CSM can cut off agent mid-sentence
- Context-aware: agent maintains conversation history within session
- Graceful degradation: if a graph node is missing, agent says so explicitly rather than hallucinating

---

### Feature 4: Split-Screen CSM Interface

**Description**: Web frontend showing live conversation on the left, graph traversal visualization on the right.

**Left panel — Conversation**:
- Live transcript of both CSM and agent speech
- Currently speaking indicator (CSM vs. agent)
- Conversation history scroll

**Right panel — Graph Traversal**:
- Real-time visualization of which nodes the agent is reading
- Currently active node highlighted
- Traversal path breadcrumb: `index → stakeholder-map → sarah-chen-profile`
- Node content preview (the markdown being read)
- Graph topology view (nodes as circles, links as edges) — optional but high demo value

**Header**:
- Client name + deal value
- Kickoff countdown timer
- "Graph Ready" status indicator

---

### Feature 5: Graph Readiness Dashboard

**Description**: Simple dashboard showing all assigned accounts, graph generation status, and quick-launch briefing.

**Cards per account**:
- Company name + deal value
- Graph status: Generating | Ready | Incomplete
- Kickoff date/time
- "Start Briefing" button (disabled until graph ready)
- Coverage score: X/10 nodes populated

---

## 7. Gemini Model Strategy

> [!NOTE]
> All models below are available through the **Google AI Studio API** (free tier for hackathon). This is our preferred access method vs. Vertex AI — simpler auth, no billing account required for prototyping, and the latest preview models ship here first.

### Model Assignment Matrix

| System Role | Model ID | Why This Model | Fallback |
|---|---|---|---|
| **Graph Generator** (entity extraction, PDF parsing, node generation) | `gemini-3.1-pro-preview` | Best reasoning model available (77.1% ARC-AGI-2). 1M token context handles full sales transcripts + contracts in a single pass. Multimodal PDF understanding eliminates need for separate PDF parser. | `gemini-3.0-flash` (faster, slightly less accurate) |
| **Graph Generator — Custom Tools** (structured output, node validation) | `gemini-3.1-pro-preview-customtools` | Optimized endpoint for agentic workflows with custom tool schemas. Ideal for structured YAML frontmatter generation and graph validation. | `gemini-3.1-pro-preview` (standard endpoint) |
| **Live Voice Agent** (real-time bidirectional conversation) | `gemini-2.5-flash-native-audio-preview` | **Only model family supporting the Gemini Live API** for real-time voice streaming. Native audio reasoning — processes raw audio without separate ASR/TTS pipeline. Sub-second latency. | None — Live API requires this model family |
| **Semantic Search** (graph embeddings for `search_graph` tool) | `gemini-embedding-001` | MTEB Multilingual #1. Matryoshka Representation Learning allows tuning dimensions (3072 → 768) for cost/quality tradeoff. 100+ languages. Replaces deprecated `text-embedding-004`. | N/A |
| **Quick Summarization** (node preview, breadcrumb labels) | `gemini-3.0-flash` | Frontier-speed model for on-the-fly summaries during graph traversal. Low latency critical for voice conversation flow. | `gemini-2.5-flash` |

### Critical Model Constraints

> [!CAUTION]
> **Gemini 3.1 Pro does NOT support the Live API.** The newest reasoning model cannot be used for real-time voice — only `gemini-2.5-flash-native-audio-preview` supports the Multimodal Live API as of Feb 2026. This is why we split the architecture: 3.1 Pro for graph generation (offline, best quality) and 2.5 Flash Native Audio for live voice (real-time, native audio support).

### Model Usage by Pipeline

```
OFFLINE PIPELINE (Graph Generation — quality over speed)
┌─────────────────────────────────────────────────┐
│  CRM webhook fires                               │
│       │                                          │
│       ▼                                          │
│  gemini-3.1-pro-preview                          │
│  ├── Extract entities from transcript (1M ctx)   │
│  ├── Parse contract PDF (multimodal)             │
│  └── Generate structured YAML + markdown nodes   │
│       │                                          │
│       ▼                                          │
│  gemini-embedding-001                            │
│  └── Embed node content for semantic search      │
└─────────────────────────────────────────────────┘

REAL-TIME PIPELINE (Voice Conversation — latency over quality)
┌─────────────────────────────────────────────────┐
│  CSM speaks into microphone                      │
│       │                                          │
│       ▼                                          │
│  gemini-2.5-flash-native-audio-preview           │
│  ├── Audio-in → understand intent                │
│  ├── Tool call → read_index / follow_link /      │
│  │               search_graph                    │
│  ├── Receive tool response (graph node content)  │
│  └── Audio-out → synthesized spoken response     │
│       │                                          │
│       ▼                                          │
│  gemini-3.0-flash (optional)                     │
│  └── Summarize long nodes for voice delivery     │
└─────────────────────────────────────────────────┘
```

### Google AI Studio API Configuration

```python
from google import genai

# Initialize client — single API key for all models
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Graph generation (offline, best quality)
GRAPH_GEN_MODEL = "gemini-3.1-pro-preview"
GRAPH_GEN_MODEL_TOOLS = "gemini-3.1-pro-preview-customtools"  # for structured output

# Live voice agent (real-time, native audio)
LIVE_AGENT_MODEL = "gemini-2.5-flash-native-audio-preview"

# Semantic search embeddings
EMBEDDING_MODEL = "gemini-embedding-001"  # 3072 dims default, MRL-scalable

# Quick summarization during traversal
SUMMARY_MODEL = "gemini-3.0-flash"  # frontier speed
```

### Embedding Configuration

```python
# Embedding dimensions strategy
# Default: 3072 dims (full quality for production)
# Hackathon: 768 dims (faster, lower storage, still excellent quality)
# MRL allows changing at query time — no re-embedding needed

EMBEDDING_DIMS = 768  # hackathon setting: fast + good enough
# EMBEDDING_DIMS = 3072  # production setting: maximum quality
```

---

## 8. Technical Stack

### Backend
| Component | Technology | Rationale |
|---|---|---|
| Agent framework | Google ADK (Agent Development Kit) | Hackathon requirement, designed for Gemini |
| Voice API | Gemini Multimodal Live API | Hackathon requirement, real-time bidirectional native audio |
| Graph generation | Gemini 3.1 Pro (`gemini-3.1-pro-preview`) | Best reasoning for entity extraction + PDF parsing. 1M token context. |
| Live conversation | Gemini 2.5 Flash Native Audio (`gemini-2.5-flash-native-audio-preview`) | Only model supporting Live API for real-time voice |
| Semantic search | Gemini Embedding (`gemini-embedding-001`) | MTEB #1, MRL-scalable dimensions, replaces deprecated text-embedding-004 |
| Quick summarization | Gemini 3 Flash (`gemini-3.0-flash`) | Frontier speed for on-the-fly node summaries |
| API server | Python FastAPI | Lightweight, async, ADK-compatible |
| WebSocket | FastAPI WebSockets | For Gemini Live streaming |

### Storage
| Component | Technology | Rationale |
|---|---|---|
| Skill graph files | Cloud Storage (GCS) | Markdown files, versioned, cheap |
| Graph metadata + index | Firestore | Fast queries, serverless, no ops |
| Embeddings for search | Gemini Embedding API (`gemini-embedding-001`) + Firestore vector search | Native Google AI Studio integration, MRL-scalable |
| Session state | Firestore | Conversation history per session |

### Frontend
| Component | Technology | Rationale |
|---|---|---|
| Framework | React (TypeScript) | Fast to build, good WebSocket support |
| Styling | Tailwind CSS | Rapid UI development |
| Graph visualization | D3.js or React Flow | Node/edge graph rendering |
| Build tool | Vite | Fast HMR for development |
| Hosting | Firebase Hosting | Free tier, CDN, works with GCP |

### Infrastructure
| Component | Technology |
|---|---|
| Container runtime | Cloud Run (serverless) |
| IaC | Terraform |
| CI/CD | Cloud Build |
| Container registry | Artifact Registry |
| Secrets | Secret Manager |
| Monitoring | Cloud Logging + Cloud Monitoring |

---

## 9. Google Cloud Infrastructure & IaC

### Terraform Structure

```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars.example
└── modules/
    ├── cloud-run/
    │   ├── main.tf          # API server + graph generator services
    │   └── variables.tf
    ├── storage/
    │   ├── main.tf          # GCS buckets for skill graphs
    │   └── variables.tf
    ├── firestore/
    │   ├── main.tf          # Firestore database + indexes
    │   └── variables.tf
    └── firebase/
        ├── main.tf          # Firebase hosting
        └── variables.tf
```

### Key Terraform Resources

```hcl
# main.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "synapse-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "firebase.googleapis.com",
    "generativelanguage.googleapis.com"
  ])
  service = each.value
  disable_on_destroy = false
}

# Cloud Storage bucket for skill graphs
resource "google_storage_bucket" "skill_graphs" {
  name          = "${var.project_id}-skill-graphs"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Firestore database
resource "google_firestore_database" "synapse" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Cloud Run — API Server
resource "google_cloud_run_v2_service" "api" {
  name     = "synapse-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/api:latest"

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_key.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Cloud Run — Graph Generator
resource "google_cloud_run_v2_service" "graph_generator" {
  name     = "synapse-graph-generator"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/synapse/graph-generator:latest"

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }
    }
    timeout = "600s"
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}

# Artifact Registry
resource "google_artifact_registry_repository" "synapse" {
  location      = var.region
  repository_id = "synapse"
  format        = "DOCKER"
}

# Secret Manager — Gemini API Key
resource "google_secret_manager_secret" "gemini_key" {
  secret_id = "gemini-api-key"
  replication {
    auto {}
  }
}
```

### Deployment Scripts

```bash
# scripts/deploy.sh
#!/bin/bash
set -e

PROJECT_ID=$1
REGION=${2:-"us-central1"}

echo "🚀 Deploying Synapse to GCP project: $PROJECT_ID"

# Build and push containers
echo "📦 Building containers..."
gcloud builds submit ./backend --tag "$REGION-docker.pkg.dev/$PROJECT_ID/synapse/api:latest"
gcloud builds submit ./graph-generator --tag "$REGION-docker.pkg.dev/$PROJECT_ID/synapse/graph-generator:latest"

# Apply Terraform
echo "🏗️  Applying infrastructure..."
cd infra
terraform init
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"
terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION"
cd ..

# Deploy frontend
echo "🌐 Deploying frontend..."
cd frontend
npm run build
firebase deploy --only hosting --project $PROJECT_ID
cd ..

echo "✅ Synapse deployed successfully!"
echo "API: $(gcloud run services describe synapse-api --region=$REGION --format='value(status.url)')"
```

---

## 10. API & Integration Specs

### REST Endpoints

```
POST /api/webhooks/crm/deal-closed
  Body: { deal_id, company_name, deal_value, products, sla_days, csm_id, contract_url, transcript }
  → Triggers graph generation job
  → Returns: { job_id, estimated_completion_seconds }

GET /api/clients
  → Returns list of accounts assigned to authenticated CSM

GET /api/clients/{client_id}/graph/status
  → Returns: { status: "generating|ready|incomplete", node_count, coverage_score }

POST /api/sessions/start
  Body: { client_id, csm_id }
  → Returns: { session_id, websocket_url }

WebSocket /ws/sessions/{session_id}
  → Bidirectional audio stream for Gemini Live
  → Server events: { type: "transcript", text, speaker }
  → Server events: { type: "graph_traversal", nodes_read: [...], current_node }
  → Client sends: raw audio bytes (PCM 16kHz)

GET /api/clients/{client_id}/graph/nodes
  → Returns all node metadata for visualization
```

### Mock CRM API (for demo)

A simple mock Salesforce-like API that the hackathon demo uses to simulate deal data. Pre-loaded with one demo account: GlobalManufacturing Co.

```python
# mock_crm/data.py
DEMO_DEAL = {
    "deal_id": "OPP-2026-GM001",
    "company_name": "GlobalManufacturing Co.",
    "deal_value": 2000000,
    "products": ["VeloSaaS CPQ", "Revenue Cloud"],
    "close_date": "2026-02-20",
    "sla_days": 90,
    "csm_id": "csm-alex-demo",
    "industry": "manufacturing",
    "employee_count": 500,
    "champion": {
        "name": "Sarah Chen",
        "title": "VP Sales Operations",
        "email": "schen@globalmanufacturing.com",
        "pain_point": "3-week quote cycle for custom orders"
    },
    "economic_buyer": {
        "name": "Marcus Webb",
        "title": "CFO",
        "commitment": "6-month payback period"
    },
    "risks": [
        "90-day go-live SLA is aggressive (industry average: 120 days)",
        "Legacy SAP ERP integration not fully scoped in contract"
    ],
    "success_metrics": [
        "Quote cycle time: 3 weeks → 48 hours",
        "CPQ adoption: 80% of sales team within 60 days"
    ]
}
```

---

## 11. Demo Script (4-Minute Video)

### Scene 1: Deal Close → Graph Generation (0:00–1:00)

**Narration**: "When a deal closes at VeloSaaS, the CSM typically has 48 hours before the kickoff call — and a massive knowledge gap to fill. Synapse fixes this automatically."

**Show**:
- Mock CRM UI: opportunity moves to "Closed Won" — GlobalManufacturing Co., $2M deal
- Synapse dashboard: card appears with "Generating..." spinner
- Graph generator logs: nodes being created in real-time (Cloud Run console or terminal)
- Graph ready notification appears. Node count: 17. Coverage: 100%.

**Highlight**: "Synapse read the contract, the sales transcripts, and the CRM data — and generated a traversable knowledge graph. No hallucination possible. Every fact is in a node."

---

### Scene 2: CSM Voice Briefing (1:00–3:00)

**Narration**: "Alex is the assigned CSM. Kickoff is in 2 hours. She opens Synapse and starts her briefing."

**Show split-screen**:
- Left: Transcript panel
- Right: Graph traversal visualization

**Conversation to demo** (pre-rehearsed, real agent):

CSM: *"Walk me through who I'll be talking to tomorrow."*

[Right panel: agent reads `gmc-index → stakeholder-map → sarah-chen-profile`]

Agent: *"Your main contact is Sarah Chen, VP of Sales Operations. She's the one who pushed this deal through internally — her pain point is a 3-week quote cycle that's costing them deals. She needs to see progress fast. The economic buyer is Marcus Webb, CFO. He signed off based on a 6-month payback — so ROI will be on his mind at renewal."*

CSM: *"What's the biggest risk going into this?"*

[Right panel: `risk-flags → timeline-risk → sap-integration-gap`]

Agent: *"Two things. First, the 90-day go-live SLA is aggressive. Manufacturing clients with their ERP complexity typically need 120 days. You should set expectations at kickoff before it becomes a contractual issue. Second, there's an unresolved SAP integration question from the last sales call — it wasn't scoped in the contract. You need to surface this and get it documented before implementation starts."*

CSM: *"Good catch. What does success look like for them in 90 days?"*

[Right panel: `success-metrics → cpq-adoption-targets`]

Agent: *"Two KPIs: quote cycle from 3 weeks to 48 hours, and 80% CPQ adoption across the sales team. If you hit those, the renewal is easy. If you don't, Sarah's credibility inside the company takes a hit."*

---

### Scene 3: Architecture + Lifecycle Vision (3:00–4:00)

**Narration**: "Synapse isn't just a briefing tool. It's the living memory of the client relationship."

**Show architecture diagram** (20 seconds):
- CRM trigger → Graph Generator → Three-layer skill graph → ADK Traversal Engine → Gemini Live → CSM

**Show lifecycle expansion slide** (20 seconds):
- Same graph, different stages highlighted: Sales prep → CSM Briefing → Implementation → Support → Renewal
- "We built the schema to support every stage from day one."

**Closing line**: "Synapse turns client knowledge from a liability into an asset — grounded, traversable, and always ready."

---

## 12. Architecture Diagram Spec

The diagram for the submission should be clean and professional. Use this layout:

```
┌─────────────┐     Closed Won     ┌──────────────────────┐
│  CRM System  │ ──── webhook ────► │   Graph Generator    │
│ (Salesforce) │                    │   (Cloud Run)        │
└─────────────┘                    │                      │
                                   │ Gemini 3.1 Pro       │
                                   │ PDF extraction       │
                                   │ Entity extraction    │
                                   └──────────┬───────────┘
                                              │ writes
                                              ▼
                              ┌───────────────────────────────┐
                              │        SKILL GRAPH            │
                              │    (Cloud Storage + Firestore)│
                              │                               │
                              │  [Product]  [Industry]  [Client]│
                              │  30 nodes   25 nodes   17 nodes│
                              └──────────────┬────────────────┘
                                             │ traversal
                                             ▼
                              ┌───────────────────────────────┐
                              │    ADK GRAPH TRAVERSAL AGENT  │
                              │                               │
                              │  read_index()                 │
                              │  follow_link()                │
                              │  search_graph()               │
                              └──────────────┬────────────────┘
                                             │ grounded answers
                                             ▼
                              ┌───────────────────────────────┐
                              │      GEMINI LIVE API          │
                              │   Real-time voice I/O         │
                              │   Interruption handling       │
                              └──────────────┬────────────────┘
                                             │
                                             ▼
                              ┌───────────────────────────────┐
                              │       CSM INTERFACE           │
                              │  Voice transcript | Graph viz │
                              │  (React + Firebase Hosting)   │
                              └───────────────────────────────┘
```

**Hosted on**: Cloud Run, Cloud Storage, Firestore, Vertex AI, Firebase — all GCP

---

## 13. File & Folder Structure

```
synapse/
├── hub/                             # Synapse Hub (Microservice)
│   ├── api/                         # Hub CRUD & Config API
│   └── src/                         # Hub Frontend (Vite)
├── backend/                         # Synapse Voice API
│   ├── agent/                       # prompts.py (Multi-role)
│   └── live/                        # session.py (Multi-tenant)
├── graph-generator/                 # Delta Knowledge Generator
│   ├── node_generator.py            # Account context weaving
│   └── templates/                   # Delta markdown templates
├── core/                            # Shared Domain Models (Tenant, Account, Deal)
├── crm-simulator/                   # Mock CRM (SalesClaw)
├── frontend/                        # Multi-role Voice UI
├── infra/                           # Terraform IaC
└── scripts/                         # start-local.ps1, deploy.ps1
```

---

## 14. Antigravity Skills for This Project

Place these skills in `.agent/skills/` at the project workspace root. These guide the Antigravity coding agent to follow project conventions and accelerate vibe coding.

---

### Skill 1: ADK Agent Builder

```
.agent/skills/adk-agent/
├── SKILL.md
└── references/
    └── adk-patterns.md
```

**`.agent/skills/adk-agent/SKILL.md`**:
```markdown
---
name: adk-agent-builder
description: Use this skill when creating, modifying, or debugging Google ADK agents, tools, or session handlers. Also use when wiring ADK agents to Gemini Live API or adding new agent tools.
---

# ADK Agent Builder

## Goal
Build production-ready Google ADK agents that integrate with Gemini Live API and use tool-calling patterns for graph traversal.

## Instructions

1. **Agent structure**: Every ADK agent goes in `backend/agent/`. The main agent definition is in `synapse_agent.py`. Tools are separate files in `backend/agent/tools/`.

2. **Tool pattern**: Each tool must be a Python function with type hints and a comprehensive docstring — ADK uses the docstring as the tool description for the model.
   ```python
   def follow_link(client_id: str, node_id: str) -> dict:
       """
       Reads a specific skill graph node. Returns the full markdown content
       and a list of linked node IDs. Use this when you have a clear
       navigation target from wikilinks in the current node.
       """
   ```

3. **Gemini Live integration**: WebSocket handler is in `backend/live/session.py`. Audio format is PCM 16kHz 16-bit mono. Always handle interruption events.

4. **Error handling**: Tools must never raise unhandled exceptions. Return `{"error": str, "fallback": "explanation"}` on failure.

5. **Testing**: Before completing any agent task, write a test in `backend/tests/` that verifies tool output format.

## Constraints
- Never use async in tool functions — ADK handles async externally
- Always ground agent responses in tool output, never allow parametric hallucination
- Model to use: `gemini-2.5-flash-native-audio-preview` for the live agent, `gemini-3.1-pro-preview` for graph generation, `gemini-embedding-001` for embeddings, `gemini-3.0-flash` for quick summarization
```

---

### Skill 2: Skill Graph Node Writer

```
.agent/skills/skill-graph-node/
├── SKILL.md
└── templates/
    ├── client-node.md
    └── moc-node.md
```

**`.agent/skills/skill-graph-node/SKILL.md`**:
```markdown
---
name: skill-graph-node-writer
description: Use this skill when creating, editing, or validating skill graph markdown nodes. Use when adding new nodes to product/, industry/, or client/ graph layers, or when fixing YAML frontmatter.
---

# Skill Graph Node Writer

## Goal
Create well-structured skill graph nodes that follow the Synapse YAML schema and wikilink conventions. Every node must be independently meaningful and traversable.

## YAML Frontmatter Schema (required fields)
```yaml
---
title: "Human-readable title"
node_id: "kebab-case-unique-id"
client_id: "client-slug-or-null-for-static"
layer: "product | industry | client"
stage: ["onboarding"]   # array: sales|onboarding|implementation|support|renewal
domain: "manufacturing | financial-services | product"
links:
  - other-node-id
  - another-node-id
description: "One sentence. What is in this node and WHEN should the agent read it. This is the semantic trigger."
last_updated: "YYYY-MM-DD"
---
```

## Wikilink Rules
- Links MUST be woven into prose: `[[node-id]]` appears mid-sentence
- The surrounding sentence must explain WHY the agent would follow this link
- Bad: `See [[stakeholder-map]]`
- Good: `Her concerns connect directly to the implementation timeline outlined in [[cpq-timeline-risks]]`

## Node Quality Checklist
- [ ] YAML frontmatter complete with all required fields
- [ ] Description is specific enough for semantic triggering (not vague)
- [ ] All wikilinks are in prose, not standalone
- [ ] Node is one complete thought (not a dump of everything)
- [ ] Length: 150–400 words for leaf nodes, 100–200 words for MOC/index nodes

## Constraints
- Never create nodes longer than 600 words — split into multiple nodes instead
- Index/MOC nodes should have 5–10 links maximum
- Always verify linked node_ids exist before writing
```

---

### Skill 3: GCP Cloud Run Deployer

```
.agent/skills/gcp-deploy/
├── SKILL.md
└── scripts/
    ├── build-and-push.sh
    └── verify-deployment.sh
```

**`.agent/skills/gcp-deploy/SKILL.md`**:
```markdown
---
name: gcp-cloud-run-deployer
description: Use this skill when deploying services to Google Cloud Run, building Docker containers, pushing to Artifact Registry, or verifying GCP deployments. Also use for Terraform apply operations.
---

# GCP Cloud Run Deployer

## Goal
Deploy Synapse services to GCP with proper build, push, and verification steps. Always produce deployment proof for hackathon submission.

## Instructions

1. **Build**: Use Cloud Build for container builds (not local Docker)
   ```bash
   gcloud builds submit ./{service} \
     --tag {REGION}-docker.pkg.dev/{PROJECT_ID}/synapse/{service}:latest \
     --project {PROJECT_ID}
   ```

2. **Deploy**: Use Cloud Run v2
   ```bash
   gcloud run deploy synapse-{service} \
     --image {REGION}-docker.pkg.dev/{PROJECT_ID}/synapse/{service}:latest \
     --region {REGION} \
     --platform managed \
     --allow-unauthenticated \
     --project {PROJECT_ID}
   ```

3. **Verify**: After every deployment, run `scripts/verify-deployment.sh` and save output to `DEPLOYMENT_PROOF.md`

4. **Terraform**: For infra changes, always run `terraform plan` before `terraform apply`. Save plan output.

5. **Proof for judges**: Every deployment must produce:
   - Cloud Run service URL
   - Screenshot or log showing service is running
   - Update DEPLOYMENT_PROOF.md

## Environment Variables Required
- PROJECT_ID
- REGION (default: us-central1)
- GEMINI_API_KEY (stored in Secret Manager, not env)

## Constraints
- Never commit API keys or secrets to the repository
- Always use Secret Manager for sensitive values
- Services must have `min-instances=0` for cost control during hackathon
```

---

### Skill 4: Gemini Live WebSocket Handler

```
.agent/skills/gemini-live/
├── SKILL.md
└── references/
    └── live-api-reference.md
```

**`.agent/skills/gemini-live/SKILL.md`**:
```markdown
---
name: gemini-live-websocket
description: Use this skill when implementing, debugging, or extending the Gemini Live API WebSocket connection. Use when handling audio streaming, interruptions, turn detection, or connecting Gemini Live to ADK agent tools.
---

# Gemini Live WebSocket Handler

## Goal
Implement reliable bidirectional audio streaming between the browser and Gemini Live API, with ADK agent tool-calling integrated into the response pipeline.

## Audio Spec
- Input: PCM 16kHz, 16-bit, mono (from browser MediaRecorder)
- Output: PCM 24kHz, 16-bit, mono (to browser AudioContext)
- Chunk size: 4096 bytes

## Connection Pattern
```python
from google import genai
from google.genai.types import LiveConnectConfig, SpeechConfig, VoiceConfig

client = genai.Client(api_key=GEMINI_API_KEY)

config = LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=SpeechConfig(
        voice_config=VoiceConfig(prebuilt_voice_config={"voice_name": "Aoede"})
    ),
    system_instruction=SYNAPSE_SYSTEM_PROMPT,
    tools=GRAPH_TRAVERSAL_TOOLS
)

async with client.aio.live.connect(model="gemini-2.5-flash-native-audio-preview", config=config) as session:
    # handle bidirectional streaming
```

## Interruption Handling
- Listen for `interrupted` events from Gemini Live
- On interruption: stop audio playback immediately, clear buffer
- Log interruption events for conversation history

## Tool Response Flow
1. Gemini Live emits `tool_call` event with function name + args
2. Execute ADK tool (read_index, follow_link, search_graph)
3. Send `tool_response` back to Gemini Live session
4. Emit `graph_traversal` event to frontend via WebSocket
5. Gemini Live synthesizes response incorporating tool output

## Constraints
- Never buffer more than 2 seconds of audio
- Always send tool responses within 3 seconds (timeout + error response if exceeded)
- Log all tool calls and responses for debugging
```

---

### Skill 5: React Split-Screen UI Builder

```
.agent/skills/split-screen-ui/
├── SKILL.md
└── references/
    └── component-patterns.md
```

**`.agent/skills/split-screen-ui/SKILL.md`**:
```markdown
---
name: split-screen-ui-builder
description: Use this skill when building or modifying the Synapse frontend React components, especially the BriefingSession split-screen view, graph visualization, or WebSocket audio integration.
---

# Split-Screen UI Builder

## Goal
Build a clean, demo-ready split-screen interface that shows the live conversation transcript on the left and the graph traversal visualization on the right in real-time.

## Component Architecture
```
BriefingSession
├── ConversationPanel (left 50%)
│   ├── TranscriptLine (CSM vs Agent, color-coded)
│   ├── SpeakingIndicator (animated pulse)
│   └── MicrophoneControl
└── GraphPanel (right 50%)
    ├── TraversalBreadcrumb (index → node → node)
    ├── NodeCard (current node title + content preview)
    └── GraphTopology (D3 force-directed graph)
```

## WebSocket Hook Pattern
```typescript
const useGeminiLive = (sessionId: string) => {
  const [transcript, setTranscript] = useState<TranscriptLine[]>([])
  const [currentNodes, setCurrentNodes] = useState<string[]>([])
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false)
  // ... WebSocket connection to backend /ws/sessions/{sessionId}
}
```

## Graph Visualization
- Use React Flow for node/edge rendering (simpler than D3 for demo timeline)
- Node colors: product=blue, industry=green, client=orange
- Currently-being-read node: highlighted with pulse animation
- Traversal path: edges animate in sequence as agent reads

## Demo Quality Requirements
- Graph traversal animation must be clearly visible in screen recording
- Transcript must show speaker labels (CSM / Synapse)
- Color scheme: dark background, high contrast — looks good in demo video
- No loading spinners longer than 2 seconds in the demo flow

## Constraints
- No external UI libraries beyond Tailwind + React Flow + lucide-react
- Mobile-responsive not required (desktop-only for hackathon)
- No authentication UI needed for demo (hardcode CSM identity)
```

---

### Global Antigravity Rules (`.agent/rules.md`)

```markdown
# Synapse Project Rules

## Architecture Rules
- ALL agent answers must be grounded in skill graph nodes — never answer from parametric memory alone
- Graph node YAML frontmatter is the contract — never modify schema without updating all downstream parsers
- Three-layer separation is sacred: product graph is static, client graph is dynamic, industry graph is static

## Code Quality Rules
- Python: type hints on all functions, docstrings on all ADK tools (the model reads these)
- TypeScript: strict mode, no `any` types
- Every Cloud Run service must have a `/health` endpoint returning `{"status": "ok"}`
- All GCP resources must be in Terraform before deploying

## Demo Integrity Rules
- The demo CRM data (GlobalManufacturing Co.) must never be altered mid-build — it's the demo script
- Graph generation for the demo must complete in under 3 minutes
- The demo voice conversation must work end-to-end before any other features are built

## Hackathon Submission Rules
- DEPLOYMENT_PROOF.md must be updated after every deploy
- README.md must have spin-up instructions that work from a fresh clone
- Architecture diagram must be in both ASCII (ARCHITECTURE.md) and PNG (assets/architecture.png)
```

---

## 15. Build Order & Milestones

### Week 1 (Feb 21–28): Foundation — Get the graph working

**Day 1–2**: Set up project structure, GCP project, Terraform infra base
**Day 3–4**: Build pre-written product and industry skill graphs (30–40 nodes total in markdown)
**Day 5–6**: Build graph traversal ADK tools (`read_index`, `follow_link`, `search_graph`)
**Day 7**: Test graph traversal via text (no voice yet) — agent should navigate correctly

**Milestone**: ADK agent answers questions from static skill graphs via text prompt. ✓

### Week 2 (Mar 1–9): Core — Get voice + graph generation working

**Day 8–9**: Gemini Live API integration — voice in, voice out, basic conversation
**Day 10–11**: Wire ADK graph traversal tools into Gemini Live session
**Day 12–13**: Build graph generator — CRM webhook → markdown nodes → Cloud Storage
**Day 14**: Test full loop: mock CRM trigger → graph generated → CSM voices questions → agent traverses graph and answers

**Milestone**: End-to-end demo loop works. CSM speaks, agent answers from graph. ✓

### Week 3 (Mar 10–15): Polish — Demo-ready

**Day 15–16**: Build React frontend — dashboard + split-screen briefing UI
**Day 17**: Graph traversal visualization (node animation during voice)
**Day 18**: Terraform full IaC + deployment scripts — get cloud proof
**Day 19**: Demo rehearsal — nail the 3-scene script
**Day 20**: Record demo video, write submission text, architecture diagram PNG

**Day 21 (Mar 16 deadline)**: Submit ✓

### What to skip if time-constrained

Drop in this order: (1) graph topology D3 visualization → show breadcrumb trail instead, (2) search_graph tool → rely on follow_link only, (3) multiple industry graphs → keep only manufacturing

---

## 16. Judging Criteria Mapping

| Criterion | Weight | How Synapse Wins |
|---|---|---|
| Innovation & Multimodal UX | 40% | Skill graph navigation is architecturally novel — no other team will have this pattern. The "progressive disclosure" traversal is genuinely new in the Live Agent space. |
| Technical Implementation | 30% | ADK + 3 custom tools + skill graph + IaC + Cloud Run. Clean, auditable, no hallucinations by design. Grounding is structural not prompting. |
| Demo & Presentation | 30% | 3-scene demo with visible graph traversal animation is highly visual and immediately communicates the value. Architecture diagram is clean. Deployment proof is automated. |

**Bonus point opportunities checked**:
- ✅ IaC (Terraform) in public repo
- ✅ GDG profile link (register before submission)
- 🎯 Publish blog post: "How I built a hallucination-free voice agent using skill graphs and Gemini Live"

---

## 17. Future Lifecycle Expansion (Post-Hackathon)

The schema is already built for full lifecycle. Adding a stage to a node's YAML `stage` array and creating stage-specific MOCs is all that's needed.

```
Current: stage: ["onboarding"]

Future roadmap:
- stage: ["sales"]          → Sales prep agent: brief AEs before discovery calls
- stage: ["implementation"] → Implementation agent: guide technical consultants
- stage: ["support"]        → Support agent: resolve tickets with full client context
- stage: ["renewal"]        → Renewal agent: build expansion story from usage data
```

**The one-liner for the demo video**: *"We're launching with CSM onboarding briefings, but the same architecture serves every stage of the client lifecycle — we designed the schema to support it from day one."*

**The real company**: Synapse is an AI-native customer intelligence platform for B2B SaaS vendors. The hackathon is the MVP validation, Google experts are the first evaluators, and the skill graph pattern is the defensible moat.

---

*Built for the Gemini Live Agent Challenge | Deadline: March 16, 2026*
*Vibe-coded with Antigravity IDE + Gemini 2.5 Pro + Claude Opus 4.6*
