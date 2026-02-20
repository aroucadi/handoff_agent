---
title: "CPQ Module — Configure, Price, Quote"
node_id: "cpq-module"
client_id: null
layer: "product"
stage: ["sales", "onboarding", "implementation"]
domain: "product"
links:
  - revenue-cloud
  - implementation-patterns
  - integration-gotchas
  - typical-timelines
description: "VeloSaaS CPQ module capabilities, pricing models, and configuration options. Read this when a client has purchased CPQ or is evaluating it."
last_updated: "2026-02-20"
---

# VeloSaaS CPQ Module

The Configure, Price, Quote (CPQ) module is VeloSaaS's core product. It enables sales teams to generate accurate, complex quotes in minutes instead of days.

## Capabilities

- **Product configuration**: Rule-based product bundling with dependency and exclusion logic. Supports 10,000+ SKU catalogs.
- **Dynamic pricing**: Tiered, volume, and subscription pricing models. AI-assisted optimal discounting based on win-rate history.
- **Quote generation**: Branded PDF quotes with e-signature integration. Multi-currency support for global deals.
- **Approval workflows**: Configurable approval chains by discount threshold, deal size, or product combination.

## Architecture

CPQ runs as a microservice within the VeloSaaS platform. Key integration points:
- **ERP sync** — real-time product catalog and pricing sync from SAP, Oracle, or NetSuite via [[integration-gotchas]]
- **CRM opportunity** — auto-populates quote from opportunity data
- **Revenue Cloud** — approved quotes flow into [[revenue-cloud]] for billing and revenue recognition

## Performance Benchmarks

- Average quote generation time: **45 seconds** (vs. industry average of 2-3 days for complex quotes)
- Pricing accuracy: **99.2%** (vs. 87% with manual processes)
- Adoption: 85% of sales reps actively using CPQ within 60 days of go-live is the target benchmark

## Common Onboarding Pitfalls

The most frequent problem during CPQ onboarding is **product catalog migration** — clients underestimate the effort of mapping their existing SKU taxonomy to VeloSaaS's schema. See [[implementation-patterns]] for the recommended approach and [[common-failure-modes]] for what happens when this step is rushed.
