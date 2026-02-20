---
title: "Typical Timelines — Go-Live Expectations"
node_id: "typical-timelines"
client_id: null
layer: "product"
stage: ["sales", "onboarding", "implementation"]
domain: "product"
links:
  - implementation-patterns
  - common-failure-modes
description: "Historical go-live timelines by vertical, deal size, and module combination. Use when setting client expectations during sales or kickoff."
last_updated: "2026-02-20"
---

# Typical Implementation Timelines

## By Module Combination

| Modules | Median Timeline | 80th Percentile |
|---|---|---|
| CPQ only | 75 days | 95 days |
| Revenue Cloud only | 60 days | 80 days |
| CPQ + Revenue Cloud (phased) | 110 days | 140 days |
| CPQ + Revenue Cloud (simultaneous) | 150 days | 200 days |

## By Industry

| Industry | CPQ Median | CPQ 80th Percentile | Key Driver |
|---|---|---|---|
| Manufacturing | 95 days | 120 days | ERP complexity, large catalogs |
| Financial Services | 75 days | 95 days | Compliance review cycles |
| Technology/SaaS | 50 days | 65 days | Simpler pricing, API-native stacks |
| Healthcare | 85 days | 110 days | Regulatory approvals |

## Timeline Red Flags

- **Client requests go-live < 60 days for manufacturing**: Almost always fails. Only 12% of manufacturing clients hit a sub-60-day timeline.
- **No IT resource assigned by Week 2**: Adds 30+ days to every timeline.
- **Product catalog > 10,000 SKUs**: Add 2-3 weeks for migration alone.
- **Legacy ERP with heavy customization**: Add 4-6 weeks for integration. See [[integration-gotchas]].

## Success Correlation

Clients that hit ±10% of their original timeline share these traits: dedicated project manager (92%), clean product data (88%), executive sponsor engaged weekly (85%), change management plan by Week 3 (78%).
