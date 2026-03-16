# ClawdView Showcase Video — Final Walkthrough

## Customer Journey Covered

```
ClawdView CRM → Synapse Admin → Synapse Hub → Synapse Live Agent
```

### Phase 01: ClawdView CRM
- **Overview** (400f/13s): Browse tab bar, see Home dashboard with deal metrics
- **Kanban** (600f/20s): Traverse pipeline columns (Prospecting → Qualification → Negotiation → Won), expand deal cards showing contacts, products, risks, transcripts

### Phase 02: Synapse Admin
- **Admin Portal** (700f/23s): View tenant list → click "Provision New" → fill form (PrecisionMetal Ltd) → provisioning animation → success confirmation

### Phase 03: Synapse Hub
- **Tenant Wizard** (900f/30s): 7-step progression with natural reading pauses:
  1. Identity (tenant name, slug)
  2. CRM Config (**webhook URL**, field mapping)
  3. Taxonomy & Mapping (stage normalization)
  4. Role Personas (CSM, Sales, Support, Win-Back)
  5. **Knowledge Sources** (Knowledge Center integration)
  6. Product Catalog (AgilePlace, Portfolios, Hub, PPM Pro)
  7. Review & Launch

### Phase 04: Synapse Live Agent
- **Dashboard** (400f/13s): Role selection → browse deal cards → hover "Ground Context" CTA
- **Briefing Session** (800f/27s): Split-pane layout:
  - **Left — ConversationPanel**: 6 progressive messages (user asks about BioSynth Labs, agent responds with grounded intelligence), typing indicators, voice input button
  - **Right — GraphPanel**: 14 entity nodes (Organization → Deal → Contacts → Products → Risks → Features → UseCases → KBArticles → Commitments → SuccessMetrics) with 18 typed edges and live traversal

---

## Mock Data Summary

| Data | Count | Source |
|---|---|---|
| Deals | 17 | `crm-simulator/seed_data.py` |
| Accounts | 12 | Across 10 industries |
| Tenant Config | 1 | Full Hub config with 4 products, 4 roles |
| Graph Entities | 14 | Organization, Deal, 2 Contacts, 2 Products, 2 Risks, DeriskingStrategy, SuccessMetric, Feature, UseCase, KBArticle, Commitment |
| Graph Edges | 18 | HAS_DEAL, HAS_CONTACT, INCLUDES_PRODUCT, HAS_RISK, MITIGATED_BY, HAS_FEATURE, ENABLES_USECASE, etc. |

## Files Modified

| File | Change |
|---|---|
| [MockDataProvider.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/components/MockDataProvider.tsx) | Full rewrite: 17 deals, graph entities/edges, node content |
| [HubKnowledgeGraph.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/HubKnowledgeGraph.tsx) | 7-step wizard, 8-dot indicator, 6 click points |
| [LiveAgentBriefing.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/LiveAgentBriefing.tsx) | Full rewrite: split-pane with progressive conversation + GraphPanel |
| [LiveAgentDashboard.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/LiveAgentDashboard.tsx) | Added cursor, role selection timing, AnimatedCursor import |
| [CRMSimulatorKanban.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/CRMSimulatorKanban.tsx) | 600-frame cursor path across pipeline columns |
| [CRMSimulatorOverview.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/CRMSimulatorOverview.tsx) | Natural 5-point cursor path |
| [AdminPortalTenant.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/scenes/AdminPortalTenant.tsx) | Updated cursor + overlay timing for 700 frames |
| [Showcase.tsx](file:///d:/rouca/DVM/workPlace/handoff/showcase/src/Showcase.tsx) | Added fade transition between Dashboard and Briefing |
