---
title: "Common Failure Modes — Post-Mortem Patterns"
node_id: "common-failure-modes"
client_id: null
layer: "product"
stage: ["onboarding", "implementation", "support"]
domain: "product"
links:
  - implementation-patterns
  - integration-gotchas
  - typical-timelines
description: "What goes wrong in VeloSaaS implementations and why, based on post-mortems. Read this to proactively surface risks during kickoff or when an implementation is going off-track."
last_updated: "2026-02-20"
---

# Common Failure Modes

Based on 200+ post-mortem reviews across VeloSaaS implementations.

## 1. Catalog Migration Death Spiral (35% of failures)

**Pattern**: Client underestimates product catalog complexity. Migration takes 3x expected time. Go-live pushed back. Executive sponsor loses confidence.

**Early warning**: Client can't provide a clean SKU export within the first 2 weeks.

**Mitigation**: Require a catalog audit in Week 1. If the catalog has > 5,000 SKUs or complex bundling rules, add 30 days to the timeline immediately.

## 2. Simultaneous Module Launch (20% of failures)

**Pattern**: Client insists on launching CPQ and Revenue Cloud simultaneously. Both modules are half-configured. Neither works well. Sales team revolts.

**Mitigation**: Always recommend phased deployment. CPQ first, stabilize for 30 days, then Revenue Cloud. Reference the [[implementation-patterns]] phased approach.

## 3. Integration Underscoping (25% of failures)

**Pattern**: ERP integration complexity was underestimated during sales. Custom fields, legacy data formats, or middleware requirements weren't captured.

**Early warning**: IT team raises concerns about integration in the first kickoff meeting. See [[integration-gotchas]] for the full list.

## 4. Change Management Neglect (20% of failures)

**Pattern**: Technology is configured correctly, but sales team doesn't adopt because nobody invested in training or change management.

**Mitigation**: Require a named change management lead on the client side by Week 2.
