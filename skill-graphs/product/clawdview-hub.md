---
title: "ClawdView Hub"
node_id: "clawdview-hub"
layer: "static"
domain: "product"
links:
  - clawdview-portfolios
  - implementation-patterns
description: "Core information about ClawdView Hub (Tasktop), integration patterns, and value proposition."
last_updated: "2026-03-01"
---

# ClawdView Hub

ClawdView Hub (formerly Tasktop) is the enterprise integration layer that connects disparate tools across the software delivery value stream (Jira, ServiceNow, Azure DevOps, SAP, Git, etc.).

## Key Capabilities
- **Model-Based Integration:** Syncs artifacts (defects, stories) based on universal models rather than rigid point-to-point APIs.
- **Value Stream Flow:** Enables measurement of how value flows between teams using different tools.

## Typical Buyer Persona
- **Champion:** Enterprise Architect, Director of Engineering Tools, CIO.
- **Pain Points:** 'Swivel-chair' integration where developers have to update states in Jira AND in an external portfolio tool. Lost productivity.

## Risk Factors
- Integration projects inherently carry mapping risks. Custom fields in Jira or SAP require careful mapping sessions during discovery.
- Requires network/infosec approval to broker connections between cloud and on-prem systems.
