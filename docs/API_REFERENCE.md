# 🛰️ ClawdView (Synapse) API Reference

ClawdView is powered by the **Synapse Core Engine**, a multi-tenant microservice architecture. All requests support the `X-Tenant-ID` header for multi-tenant context.

> [!NOTE]
> All base URLs below are examples. Use `terraform output` after deployment to retrieve your specific service endpoints.

---

## 1. Synapse Core API
**Base URL:** `https://synapse-api-[hash].a.run.app`

### Sessions

#### `POST /api/sessions/start`
Initialize a new Gemini Live voice session.

**Request:**
```json
{
    "account_id": "precisionmetal-ltd",
    "tenant_id": "T001",
    "case_id": "WON-2025-CS01",
    "role": "csm"
}
```

**Response:** `{ "session_id": "uuid", "ws_url": "wss://..." }`

#### `WebSocket /ws/{session_id}`
Bidirectional audio streaming. Message types:
- `{"type": "audio", "data": "<base64 PCM>"}` — Send/receive audio
- `{"type": "text", "text": "..."}` — Send text (triggers voice response)
- `{"type": "transcript", "role": "agent|user", "text": "..."}` — Transcript event
- `{"type": "tool_call", "name": "...", "args": {...}}` — Tool execution notification

### Knowledge Graph

#### `GET /api/clients/{account_id}/graph/status`
Graph readiness check. Returns `{ "status": "ready|generating|not_found", "entity_count": 42 }`

#### `GET /api/clients/{account_id}/graph/entities`
Full typed entity list for React Flow visualization.

**Response:**
```json
{
    "entities": [
        {
            "id": "client-001",
            "type": "Client",
            "name": "Acme Corp",
            "data": { "industry": "Manufacturing", "mrr": 45000 },
            "connections": [
                { "target": "risk-001", "edge_type": "HAS_RISK" },
                { "target": "deal-001", "edge_type": "HAS_DEAL" }
            ]
        }
    ]
}
```

### Generative Outputs

#### `POST /api/clients/{account_id}/outputs/briefing`
Generate an AI briefing document. **Request:** `{ "user_role": "csm" }`

#### `POST /api/clients/{account_id}/outputs/action-plan`
Generate a prioritized action plan. **Request:** `{ "user_role": "csm" }`

#### `POST /api/clients/{account_id}/outputs/risk-report`
Generate a risk assessment report.

#### `POST /api/clients/{account_id}/outputs/recommendations`
Generate strategic recommendations. **Request:** `{ "recommendation_type": "general|upsell|retention|expansion" }`

#### `POST /api/clients/{account_id}/outputs/handoff`
Generate a team transition document. **Request:** `{ "from_team": "sales", "to_team": "cs" }`

#### `POST /api/clients/{account_id}/outputs/transcript`
Generate a role-based script. **Request:**
```json
{
    "transcript_type": "sales_script|support_script|qbr_prep|renewal_script|onboarding_guide|discovery_questions",
    "user_role": "sales",
    "additional_context": "Client expressed budget concerns"
}
```

#### `GET /api/clients/{account_id}/outputs/transcript-types`
List available transcript types with descriptions.

#### `GET /api/clients/{account_id}/outputs`
List all generated artifacts (versioned). Returns `{ "outputs": [{ "id", "type", "subtype", "title", "version", "is_latest", "generated_at" }] }`

#### `GET /api/clients/{account_id}/outputs/{output_id}`
Retrieve a specific artifact with full content. Returns `{ "id", "type", "title", "content", "version", "generated_at" }`

### Deals & Clients

#### `GET /api/deals?tenant_id=T001&stages=closed_won,prospecting`
List deals filtered by tenant and stages.

#### `GET /api/clients/{account_id}`
Get client account details.

---

## 2. Hub API (Tenant Configuration)
**Base URL:** `https://synapse-hub-[hash].a.run.app`

#### `GET /api/tenants`
List all tenants.

#### `GET /api/tenants/{tenant_id}`
Get tenant config (branding, roles, CRM field mapping, agent personas).

#### `POST /api/tenants`
Create a new tenant.

#### `PUT /api/tenants/{tenant_id}`
Update tenant configuration.

#### `POST /api/tenants/{tenant_id}/accounts`
Register a new B2B account for a tenant.

---

## 3. Graph Generator
**Base URL:** `https://synapse-graph-generator-[hash].a.run.app`

#### `POST /generate`
Trigger ontology-driven graph generation from CRM webhook data.

**Request:**
```json
{
    "tenant_id": "T001",
    "account_id": "precisionmetal-ltd",
    "crm_data": { "account": {...}, "deals": [...], "contacts": [...] }
}
```

#### `GET /health`
Health check. Returns `{ "status": "healthy", "model": "gemini-3.1-pro" }`

---

## 4. CRM Simulator
**Base URL:** `https://synapse-crm-simulator-[hash].a.run.app`

#### `GET /api/deals`
List all simulated deals.

#### `PATCH /api/deals/{case_id}/flag`
Flag a deal as "at risk" — invoked by the Live Agent's tool when churn risk is detected.

```json
{
    "status": "at_risk",
    "reason": "Missing SSO integration implementation schedule"
}
```
