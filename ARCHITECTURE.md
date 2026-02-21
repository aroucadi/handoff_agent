# Handoff — Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        HANDOFF ARCHITECTURE                          │
│                                                                      │
│  ┌─────────────┐    webhook     ┌──────────────────┐                │
│  │   CRM       │───────────────▶│   Handoff API    │                │
│  │  Simulator  │   deal-closed  │   (Cloud Run)    │                │
│  │  :8001      │                │   :8000          │                │
│  └─────────────┘                └──────┬───────────┘                │
│        │                               │                             │
│        │                    ┌──────────┴──────────┐                  │
│        │                    │                     │                  │
│        │              POST /generate      WS /ws/sessions           │
│        │                    │                     │                  │
│        │                    ▼                     ▼                  │
│        │          ┌──────────────┐     ┌─────────────────┐          │
│        │          │   Graph      │     │  Gemini Live    │          │
│        │          │  Generator   │     │  Session Mgr    │          │
│        │          │  (Cloud Run) │     │                 │          │
│        │          │  :8002       │     │  gemini-2.5-    │          │
│        │          └──────┬───────┘     │  flash-native-  │          │
│        │                 │             │  audio-preview  │          │
│        │         ┌───────┼───────┐     └────────┬────────┘          │
│        │         │       │       │              │                    │
│        │         ▼       ▼       ▼              │                    │
│        │     ┌──────┐┌──────┐┌──────┐          │                    │
│        │     │Gemini││Gemini││Gemini│    tool calls                 │
│        │     │3.1Pro││3.1Pro││Embed │    (read_index,               │
│        │     │      ││      ││001   │     follow_link,              │
│        │     │Extract││Nodes ││768d  │     search_graph)             │
│        │     └──────┘└──────┘└──────┘          │                    │
│        │         │       │       │              │                    │
│        │         ▼       ▼       ▼              ▼                    │
│        │    ┌─────────────────────────────────────────┐              │
│        │    │        Google Cloud Platform             │              │
│        │    │                                         │              │
│        │    │  ┌──────────┐  ┌──────────────────┐    │              │
│        │    │  │   GCS    │  │    Firestore     │    │              │
│        │    │  │          │  │                  │    │              │
│        │    │  │ skill-   │  │ skill_graphs/    │    │              │
│        │    │  │ graphs/  │  │   {client_id}/   │    │              │
│        │    │  │          │  │     nodes/       │    │              │
│        │    │  │ clients/ │  │       metadata   │    │              │
│        │    │  │ product/ │  │       links      │    │              │
│        │    │  │ industry/│  │       embedding  │    │              │
│        │    │  └──────────┘  └──────────────────┘    │              │
│        │    │                                         │              │
│        │    │  ┌──────────────────────────────────┐   │              │
│        │    │  │     Secret Manager               │   │              │
│        │    │  │     GEMINI_API_KEY                │   │              │
│        │    │  └──────────────────────────────────┘   │              │
│        │    └─────────────────────────────────────────┘              │
│        │                                                             │
│        │    ┌─────────────────────────────────────────┐              │
│        ▼    │         Frontend (Voice UI)              │              │
│  ┌──────────────┐                                     │              │
│  │  Handoff     │◀── WebSocket (bidirectional audio) ─┘              │
│  │  Voice UI    │                                                    │
│  │  (React)     │    Features:                                       │
│  │  :5174       │    • Dashboard (account cards)                     │
│  │              │    • Split-screen briefing                         │
│  │              │    • React Flow graph topology                     │
│  │              │    • Mic capture (PCM 16kHz)                       │
│  │              │    • Audio playback (PCM 24kHz)                    │
│  └──────────────┘    • Breadcrumb + node content                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Deal Close → Voice Briefing

```
1. CSM closes deal in CRM Simulator
       │
       ▼
2. CRM fires webhook → POST /api/webhooks/crm/deal-closed
       │
       ▼
3. Backend forwards to Graph Generator → POST /generate
       │
       ▼
4. Graph Generator pipeline (async, ~60-120 seconds):
   a. Extract entities from CRM payload
   b. Extract entities from transcript (Gemini 3.1 Pro)
   c. Generate 8 markdown nodes (Gemini 3.1 Pro)
   d. Write nodes to GCS: gs://bucket/clients/{id}/*.md
   e. Index in Firestore with embeddings (gemini-embedding-001)
       │
       ▼
5. CSM opens Handoff dashboard → sees account card "Ready"
       │
       ▼
6. CSM clicks "Start Briefing" → creates session
       │
       ▼
7. WebSocket connects to Gemini Live (gemini-2.5-flash-native-audio)
       │
       ▼
8. Real-time voice conversation with tool calling:
   Agent reads graph nodes → provides grounded briefing
   Frontend shows: transcript, speaking indicator, graph animation
```

## Gemini Models Used

| Model | Purpose | Where Used |
|---|---|---|
| `gemini-3.1-pro-preview` | Entity extraction + node generation | Graph Generator |
| `gemini-embedding-001` | 768d vector embeddings for search | Graph Generator, Backend |
| `gemini-2.5-flash-native-audio-preview` | Real-time voice (Multimodal Live API) | Backend Live Sessions |
| `gemini-3.0-flash` | Fallback / summaries | Backend (optional) |

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 6, TypeScript 5, React Flow |
| **Backend API** | Python 3.11, FastAPI, WebSockets |
| **Graph Generator** | Python 3.11, FastAPI, Google GenAI SDK |
| **Infrastructure** | Terraform, Google Cloud (Cloud Run, GCS, Firestore, Secret Manager) |
| **AI** | Gemini 3.1 Pro, Gemini Embedding 001, Gemini 2.5 Flash Native Audio |
| **IaC** | Terraform modules (storage, firestore, cloud-run, firebase) |

## Project Structure

```
handoff/
├── backend/                    # Handoff API (FastAPI)
│   ├── main.py                 # Routes + WebSocket handler
│   ├── config.py               # Environment config
│   ├── agent/                  # ADK agent
│   │   ├── handoff_agent.py    # Multi-round function calling
│   │   ├── tools.py            # read_index, follow_link, search_graph
│   │   └── prompts.py          # System prompt
│   ├── graph/                  # Graph traversal engine
│   │   ├── traversal.py        # Navigation logic
│   │   ├── storage.py          # GCS reads
│   │   └── search.py           # Vector search
│   └── live/                   # Gemini Live integration
│       └── session.py          # Live session handler
├── graph-generator/            # Graph Generator service (FastAPI)
│   ├── main.py                 # 5-step pipeline orchestrator
│   ├── extractors/             # Entity extraction
│   ├── node_generator.py       # Markdown node generation
│   ├── storage.py              # GCS writes
│   └── indexer.py              # Firestore + embeddings
├── crm-simulator/              # CRM Simulator (FastAPI + React)
│   ├── main.py                 # Deal CRUD + webhooks
│   └── frontend/               # Kanban board UI
├── frontend/                   # Handoff Voice UI (React)
│   └── src/
│       ├── App.tsx             # Dashboard ↔ Briefing routing
│       ├── useVoiceSession.ts  # WebSocket audio hook
│       └── components/         # Dashboard, BriefingSession, etc.
├── skill-graphs/               # Static knowledge nodes
│   ├── product/                # 7 VeloSaaS product nodes
│   └── industries/             # 5 manufacturing industry nodes
├── infra/                      # Terraform IaC
│   ├── main.tf                 # Root config
│   └── modules/                # storage, firestore, cloud-run, firebase
└── scripts/                    # Deployment & demo scripts
```
