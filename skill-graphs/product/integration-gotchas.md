---
title: "Integration Gotchas — ERP & Third-Party Pitfalls"
node_id: "integration-gotchas"
client_id: null
layer: "product"
stage: ["onboarding", "implementation"]
domain: "product"
links:
  - cpq-module
  - common-failure-modes
  - implementation-patterns
description: "Known integration pitfalls with SAP, Oracle, NetSuite, and other ERPs. Read when scoping integration work or when a client reports data sync issues."
last_updated: "2026-02-20"
---

# Integration Gotchas

## SAP Integration

- **SAP ECC 6.0**: Requires BAPI-based middleware. Custom IDOC configurations for product catalog sync. Plan 4–6 weeks for integration alone.
- **SAP S/4HANA**: Cleaner API layer, but authentication (OAuth2 with X.509) is complex to set up. Plan 2–3 weeks.
- **Common trap**: SAP SD module customizations (custom pricing procedures, condition types) are rarely documented. Always request the client's SD configuration spreadsheet before scoping.

## Oracle

- **Oracle EBS**: REST API available but pagination is unreliable for large catalogs. Batch sync recommended over real-time.
- **Oracle Fusion**: Modern APIs but rate limiting is aggressive. Build retry logic from day one.

## NetSuite

- **SuiteScript/RESTlet**: Generally the smoothest integration. Main gotcha is NetSuite's saved search performance with large result sets.
- **SuiteTalk SOAP API**: Deprecated but many clients still use it. Push for migration to REST.

## General Rules

1. **Never trust the client's integration docs** — always verify by inspecting actual API responses
2. **Build idempotent sync jobs** — duplicate data is inevitable, design for it
3. **Log everything** — integration bugs are the #1 support ticket category
