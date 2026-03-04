---
title: "Manufacturing Industry Guide"
node_id: "manufacturing-index"
layer: "static"
domain: "industry"
links:
  - implementation-patterns
  - planview-portfolios
description: "Core concepts and common challenges when deploying to Manufacturing clients."
last_updated: "2026-03-01"
---

# Manufacturing Industry Guide

Manufacturing clients typically operate under extreme regulatory scrutiny and strict waterfall supply-chain timelines, making agile transformations difficult but highly valuable.

## Key Themes
- **Data Sovereignty:** Many manufacturing clients have strict rules about where data is stored (e.g., EU-only regions to comply with GDPR or German Works Council requirements).
- **ITAR Compliance:** US Aerospace and Defense manufacturers require FedRAMP High or GovCloud environments. Data cannot leave US soil and cannot be accessed by non-US citizens.
- **Legacy ERP Integration:** Almost all manufacturing clients run SAP, Oracle, or heavily customized legacy ERPs. Integrating [[planview-portfolios]] with these systems via [[planview-hub]] is the most common technical blocker.

## Value Drivers
- Reducing physical prototype waste by shifting to synchronized digital modeling.
- Aligning R&D spending with physical production capacity.
