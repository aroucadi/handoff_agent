# 🛰️ Synapse API Reference

Synapse uses a multi-tenant microservice architecture. All requests to Voice API, Hub, and Graph Generator require a `X-Tenant-ID` header (default `T001` for demo).

---

## 1. Hub API (Tenant Configuration)
**Base URL:** `https://synapse-hub-api-[...].a.run.app`

### `GET /tenants/{tenant_id}`
Returns branding, agent personas, and GCS bucket configuration for a specific tenant.

### `POST /tenants/{tenant_id}/accounts`
Registers a new B2B account for a tenant and initializes their Account Skill Graph.

---

## 2. Graph Generator (Delta Pipe)
**Base URL:** `https://synapse-graph-generator-[...].a.run.app`

### `POST /generate`
Accepts a webhook payload. It performs an "Account Context Weaver" operation: checking for existing nodes and generating deal-specific **Deltas**.

---

## 2. Agent Core API
**Base URL:** `https://synapse-api-[...].a.run.app`

### `GET /clients/{client_id}/graph`
Fetches the fully materialized Markdown skill graph for a given client to be rendered on the React Flow topology dashboard.

**Response (200 OK):**
```json
{
  "client_id": "acme-corp",
  "nodes": [
    {
       "node_id": "acme_req_rbac",
       "title": "Role-Based Access Control",
       "category": "Requirement",
       "markdown": "## Details\nThe client needs LDAP sync...",
       "connections": ["acme_sec_sla"]
    }
  ]
}
```

### `GET /sessions/start`
Initializes a new `gemini-2.5-flash-native-audio-preview` Voice session.
**Query Params**: `tenant_id`, `account_id`, `role` (CSM/Sales/Support/WinBack).
Returns the WebSocket URI for real-time WebRTC audio/vision.

---

## 3. CRM Simulator
**Base URL:** `https://synapse-crm-simulator-[...].a.run.app`

### `PATCH /api/deals/{deal_id}/flag`
An internal endpoint invoked *exclusively* as a Function Call by the Live Agent. If the Voice Agent detects major churn risk during its conversation with the CSM, it uses a Tool to hit this endpoint, marking the deal "At Risk" in the external system.

**Request Body:**
```json
{
  "status": "at_risk",
  "reason": "Missing SSO integration implementation schedule"
}
```
