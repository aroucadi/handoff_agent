## Goals
- Make seeding behave like the UI by calling the same APIs (no /generate shortcuts).
- Add tenant-scoped, runtime-wired Knowledge Sync (decoupled from deal close) using flexible knowledge_sources.
- Make CRM Simulator able to create/update deals like a human user would.
- Ensure contracts are sourced only via CRM-provided URIs and Graph Generator fails fast when missing.
- Add a quota-aware journey runner with built-in verification + one negative-path scenario.

## Scope Of Code Changes
- Hub API + models (tenant config extensions).
- Graph Generator (new sync endpoint + tenant knowledge storage + linking logic).
- CRM Simulator (new endpoints + payload fixes + contract URI behavior).
- Seed/journey runner tooling.
- Contract PDF generator upgrade (multi-page, product-aware).

## 1) Hub: TenantConfig Knowledge Sources
- Update [hub/api/models.py](file:///d:/rouca/DVM/workPlace/handoff/hub/api/models.py)
  - Add `knowledge_sources: list[dict]` to TenantConfig.
  - Add typed submodels for sources (preferred): `KnowledgeSource` with `type` enum (website_crawl, document_upload, zendesk_api) and per-type config.
  - Extend UpdateTenantRequest to allow updating knowledge_sources.
- Update [hub/api/main.py](file:///d:/rouca/DVM/workPlace/handoff/hub/api/main.py)
  - Ensure create/update endpoints persist knowledge_sources.
  - Add a new endpoint: `POST /api/tenants/{tenant_id}/sync-knowledge` that calls Graph Generator’s sync endpoint (Hub acts like the UI button).

## 2) Graph Generator: Tenant Knowledge Sync API
- Add endpoint in Graph Generator (new file or integrate into existing router):
  - `POST /api/sync-knowledge/{tenant_id}`
  - Reads tenant config from Firestore (`tenants/{tenant_id}`), iterates knowledge_sources.
  - For `website_crawl` (ClawdView demo): support both local path (dev) and URL fetch (prod). If URL fetch is non-trivial, implement URL mode as “download HTML pages from GCS bucket” initially.
  - Produces extracted nodes/edges via [knowledge_center_extractor.py](file:///d:/rouca/DVM/workPlace/handoff/graph-generator/extractors/knowledge_center_extractor.py).
- Persist tenant KB to Firestore:
  - New collections: `tenant_knowledge/{tenant_id}/entities` and `/edges`, plus status doc at `tenant_knowledge/{tenant_id}`.
  - Enforce stable ID conventions for Product nodes (e.g., `product_clawdview-hub`), matching what CRM edges reference.

## 3) Graph Generator: Link Tenant KB Into Client Graphs
- Update generation pipeline so that when a deal webhook triggers client graph generation:
  - It looks up tenant KB in `tenant_knowledge/{tenant_id}`.
  - It injects/copies relevant KB entities into the client graph payload before indexing:
    - Always include Products referenced by the deal.
    - Include connected Features/Limitations/KBArticles for those Products.
  - This ensures [backend graph tools](file:///d:/rouca/DVM/workPlace/handoff/backend/graph/traversal.py) like product_knowledge work with real product docs.

## 4) CRM Simulator: UI-Equivalent APIs + Correct Webhook Payload
- Update [crm-simulator/models.py](file:///d:/rouca/DVM/workPlace/handoff/crm-simulator/models.py)
  - Extend DealUpdate to allow updating `tenant_id` and `crm_platform`.
  - Add a CreateDeal model (or reuse Deal with server-side defaults) for POST /api/deals.
- Update [crm-simulator/main.py](file:///d:/rouca/DVM/workPlace/handoff/crm-simulator/main.py)
  - Add `POST /api/deals` to create deals programmatically.
  - Ensure `_fire_webhook()` injects `stage` into the JSON body.
  - Contract URIs:
    - Keep `contract_pdf_url` as the canonical field.
    - Optionally add `contract_file_uri` as an alias (payload includes both), with Graph Generator accepting either.
  - Ensure stage transitions + contract upload mirror the UI.

## 5) Mapping/Normalization Without Breaking CRM-Agnosticism
- Prefer doing shape transforms in tenant field mapping (Graph Generator ingest):
  - Extend mapping logic to support nested transforms for success_metrics (metric→name, current_value→baseline, timeframe→timeline).
- Add a minimal safety fallback in [crm_extractor.py](file:///d:/rouca/DVM/workPlace/handoff/graph-generator/extractors/crm_extractor.py) so it can accept both shapes if mapping is missing, but keep it generic (not “HubSpot vs Salesforce”, just “expected keys absent, map common synonyms”).

## 6) Contracts: Multi-Page, Product-Aware PDFs
- Upgrade [scripts/generate_contracts.py](file:///d:/rouca/DVM/workPlace/handoff/scripts/generate_contracts.py)
  - Generate 5–12 page PDFs with sections: Order Form, Pricing table, SLA, DPA, Industry addendum, Integration scope, Signature blocks.
  - Pull product names from deal.products and include product-specific clauses.
  - Ensure output is uploaded via CRM API `/api/deals/{deal_id}/upload-contract` (not direct GCS writes).

## 7) Journey Runner (The New Seeding Mechanism)
- Add `scripts/journey_runner.py`
  - Phases: clean → health → tenant onboard → generate product nodes → sync tenant knowledge → create deals → upload contract/transcript → stage progression → poll job completion → verify graph/tools/outputs.
  - Verification checks:
    - Firestore: `deals/{tenant}/items/{deal_id}` graph_ready flips true.
    - Firestore: `knowledge_graphs/{client_id}/entities|edges|outputs` exist.
    - Backend API: call output generation endpoints and confirm stored outputs.
  - Quota-aware pacing:
    - Serialize graph-generation triggers.
    - Poll job status instead of fixed sleeps.
    - Exponential backoff on 429/5xx.
  - Negative-path scenario:
    - Seed one tenant with intentionally broken mapping → expect ingest 422 + integration_status error → fix mapping via Hub API → replay.

## 8) Verification Plan (How We’ll Prove It Works)
- Local dev:
  - Start services via existing scripts.
  - Run journey_runner end-to-end.
  - Confirm UI views (Hub, CRM, Voice UI) reflect the seeded world.
- Assertions:
  - Product knowledge appears in product_knowledge tool output.
  - Contracts are downloadable in CRM and referenced in extracted entities.
  - One negative-path account shows error then recovers.

## Deliverable: Post-Implementation Explanation
- After you approve this plan and I implement it, I will provide:
  - A per-file change log (what changed and why).
  - The exact new endpoints and example requests.
  - A walkthrough of journey_runner execution phases.
  - Any new data/fixture formats and how to extend them.