# 🛰️ Synapse API Reference

Synapse uses a microservice architecture built with Python FastAPI. This document outlines the primary REST capabilities and internal communication endpoints.

---

## 1. Graph Generator Webhook API
**Base URL:** `https://synapse-graph-generator-[...].a.run.app`

### `POST /generate`
Accepts a webhook payload from the CRM simulator when a deal is "Closed Won". Triggers the asynchronous, multi-agent graph generation pipeline. Returns a Tracking ID instantly while generation continues in the background.

**Request Body:**
```json
{
  "deal_id": "opp-99321",
  "company_name": "Acme Corp",
  "industry": "FinTech",
  "sales_transcript": "Customer requires strict RBAC...",
  "contract_pdf_url": "https://storage.googleapis.com/..."
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "a8f3b211",
  "status": "queued",
  "message": "Graph generation started for Acme Corp"
}
```

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

### `GET /live/setup`
Initializes a new `gemini-2.0-flash-exp` Voice session. Returns the ephemeral session URI and WebSocket protocol configuration over HTTP before the client upgrades the connection.

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
