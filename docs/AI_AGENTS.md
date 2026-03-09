# 🤖 Synapse AI Agents Architecture

Synapse relies on a suite of **specialized, purpose-driven AI Agents** powered by Google's Gemini models. By dividing cognitive labor between asynchronous data extraction, real-time voice conversation, and on-demand document generation, Synapse achieves its "Level 5 Agent" status.

---

## 1. The Graph Generator (Asynchronous Multi-Agent)
**Model:** `gemini-3.1-pro`

### Ontology-Driven Pipeline

When CRM data arrives (via webhook or Hub sync), the Graph Generator builds a structured knowledge graph using a formal ontology with 20+ entity types and typed relationships:

**Entity Types:** `Account`, `Case`, `Contact`, `Risk`, `Product`, `Feature`, `Limitation`, `SuccessMetric`, `Competitor`, `Integration`, `Timeline`, `KBArticle`, and more.

**Edge Types:** `HAS_RISK`, `INCLUDES`, `CHAMPIONS`, `USES_PRODUCT`, `MITIGATED_BY`, `DEPENDS_ON`, `COMPETES_WITH`, etc.

### Phase A: The Extractor Agents
- **CRM Extractor**: Parses structured CRM data (accounts, deals, contacts, products) via Hub's agnostic field mapping. Emits typed entities + relationships.
- **Knowledge Center Extractor**: Crawls the static ClawdView Knowledge Center site to extract product docs, features, limitations, and KB articles.

### Phase B: Generator + Reviewer
1. **Generator**: Takes extracted entities and generates delta knowledge graph nodes. Account-oriented: pulls historical cases to generate only new/changed content.
2. **Reviewer**: QA agent that validates entity types match the ontology, edges are correctly typed, and cross-references resolve.

---

## 2. The Semantic Indexer
**Model:** `gemini-embedding-001` (768d vectors)

Every entity in the knowledge graph is embedded and stored in **Firestore** with typed metadata. Supports:
- **Type-filtered search**: Search only `Risk` entities, or only `Product` entities
- **Multi-hop traversal**: Follow typed edges across entities (e.g., Deal → Risk → Mitigation Strategy)
- **Cross-layer linking**: Account entities link to Product features and KB articles

---

## 3. The Multimodal Live Agent (Real-Time Voice + Vision)
**Model:** `gemini-live-2.5-flash-native-audio`

### 14 ADK Tools
 
The agent has access to 14 function-calling tools organized into three categories:

#### Structured Graph Tools (7)
| Tool | Description |
|---|---|
| `graph_overview` | High-level graph overview: entity types, counts, format |
| `get_entity` | Retrieve a specific entity and its connections |
| `get_entities_by_type` | All entities of a type (e.g., all Risks, all Contacts) |
| `traverse_graph` | Multi-hop traversal following typed edges |
| `search_entities` | Semantic search with optional type filter |
| `risk_profile` | Comprehensive risk assessment with severity breakdown |
| `product_knowledge` | Products, features, limitations, and KB articles |
| `web_scrape` | Real-time browsing and scraping of public website content |

#### Output Generation Tools (3)
| Tool | Description |
|---|---|
| `generate_briefing` | Pre-meeting briefing with stakeholders, risks, talking points |
| `generate_action_plan` | Post-session prioritized action items with owners |
| `generate_transcript` | Role-based scripts (6 types — see below) |

#### Legacy Tools (3)
| Tool | Description |
|---|---|
| `read_index` | Table-of-contents for a skill graph layer |
| `follow_link` | Navigate to a specific node by wikilink |
| `search_graph` | Semantic search across the graph |

### Google Search Grounding

The Live agent has access to **Google Search** as a supplementary information source:

- **When**: Industry trends, competitor context, market data not in the knowledge graph
- **When NOT**: Account case data, internal CRM info, pricing (always from the graph)
- **Guardrails**: Prompt policy limits searches to 1-2 per conversation, requires the agent to cite when using external data

### Multi-Role Support (Zero Adaptation)

The system prompt dynamically adapts based on the tenant's brand name and the user's mapped role persona. Available roles can be completely customized via the Hub:

| Role | Focus | Vocabulary |
|---|---|---|
| **CSM** | Onboarding, health scores, adoption, QBRs | "time-to-value", "champion", "go-live", "milestone" |
| **Sales** | Pipeline, competitive positioning, win strategy | "MEDDIC", "economic buyer", "value prop", "displacement" |
| **Support** | Technical context, SLAs, escalation paths | "MTTR", "root cause", "runbook", "severity level" |
| **Strategy** | Loss analysis, win-back, market positioning | "churn indicators", "whitespace", "cohort analysis" |

---

## 4. The Document Generator (On-Demand)
**Model:** `gemini-3.1-pro` / `gemini-3.1-flash-lite` (Thinking)

### 7 Output Types

Available as both REST API endpoints and agent tools during live sessions:

| Generator | Description |
|---|---|
| `generate_briefing` | Executive briefing with stakeholders, risks, talking points |
| `generate_action_plan` | Prioritized follow-ups grouped by urgency |
| `generate_risk_report` | Risk assessment with severity dashboard |
| `generate_recommendations` | Strategic guidance (general/upsell/retention/expansion) |
| `generate_handoff` | Team transition documents (Sales→CS, CS→Support) |
| `generate_transcript` | Role-based scripts (6 types) |
| `web_scrape` | Real-time public web content extraction |
| `list_outputs` / `get_output` | Retrieve versioned artifacts from Firestore |

### 6 Transcript Types

Each type has a tailored Gemini system persona:

| Type | Use Case | Key Sections |
|---|---|---|
| `sales_script` | Sales call prep | Opening, Value Prop, Objection Handling, Close |
| `support_script` | Frustrated customer | Empathetic Greeting, De-escalation, Resolution |
| `qbr_prep` | QBR discussion guide | Value Delivered, Adoption Metrics, Next Quarter |
| `renewal_script` | Contract renewal | Value Recap, ROI Summary, Expansion Opportunity |
| `onboarding_guide` | New customer setup | Account Setup, Feature Tour, 30-60-90 Plan |
| `discovery_questions` | Qualification | Pain Points, Decision Process, Success Criteria |

### Versioning

All generated artifacts are versioned in Firestore:
- Each type maintains a version counter
- Previous versions remain accessible via the ArtifactViewer
- Dashboard shows artifact badges per account with latest counts

---

## 5. The Hub Integration Layer
**Stack:** React + FastAPI

The Hub is the multi-tenant configuration portal that makes Synapse CRM-agnostic:

- **Tenant Management**: Create/configure tenants with custom branding
- **CRM Field Mapping**: Map any CRM's data schema to Synapse's ontology
- **Role Persona Mapping**: Map team roles to specific stages, filters, and icons
- **Taxonomy Normalization**: Map CRM stages and product names to Synapse canonical taxonomy
- **Terminology Overrides**: Change software-wide labels (e.g. "Account" -> "Client")
- **Webhook Registration**: Auto-register webhooks for case events
- **Launch Agent**: Direct link to the Voice UI with tenant context
