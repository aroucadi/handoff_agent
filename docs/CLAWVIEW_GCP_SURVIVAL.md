# 🛑 ClawdView GCP Survival & Safety Guide

This document explains the technical safeguards implemented to protect the **ClawdView** platform from Google Cloud Platform (GCP) suspensions, specifically focusing on GenAI API usage and web crawling ethics.

---

## 📜 The Context
During the scale-up of **Phase 6**, the system triggered a GCP account suspension. After a structural analysis, we identified two primary "high-risk" behaviors:
1.  **Bursty GenAI Traffic**: High-concurrency extraction of Knowledge Center pages and CRM deals.
2.  **Unrestricted Crawling**: The crawler could theoretically navigate outside the intended Knowledge Center boundaries.

---

## 🛡️ Implemented Safeguards

### 1. Concurrent Request Throttling (Semaphores)
We have implemented global **asyncio Semaphores** across the `graph-generator` microservice to ensure we never overwhelm the Vertex AI / Gemini API quotas.

*   **Extraction Semaphore (`limit=3`)**: Restricts concurrent calls to `extract_entities_from_page`.
*   **Embedding Semaphore (`limit=5`)**: Restricts concurrent vector generation calls.
*   **Orchestrator Bottleneck (`limit=2`)**: Restricts the maximum number of simultaneous deal graph generations.

### 2. The `--lite` Guardrail
The `journey_runner.py` and `seed_rag.py` scripts now support a `--lite` flag designed for safe, low-impact demonstrations.

*   **Paced Seeding**: When `--lite` is active, a mandatory `sleep(5)` is inserted between every deal webhook event.
*   **Volume Caps**: Limits total seeded deals to 3 and total crawled pages to 3.

### 3. Strict Crawler Boundaries
The crawling engine in `sync_knowledge.py` now enforces a **Path-Prefix Boundary**.

> [!IMPORTANT]
> The crawler will only follow links that share the **exact same start path** as the seed URL. For example, seeding `storage.googleapis.com/knowledge/index.html` will NOT allow the crawler to jump to other buckets or Google services.

### 4. Background Task Decoupling
Heavy GenAI tasks (extracting a whole website or processing 10 deals) have been moved from the request-response cycle into a **non-blocking background worker**. 

The Hub UI now returns a `job_id` immediately, and the frontend polls for completion, preventing "hanging" HTTP requests that can be flagged as malicious or hung processes.

---

## 🚦 Best Practices for Demos

1.  **Always use `--lite`** for local testing or secondary project deployments.
2.  **Check Quotas**: Monitor your [Google Cloud Console Quotas](https://console.cloud.google.com/iam-admin/quotas) regularly.
3.  **Avoid Loop Crawls**: Do not point the Hub knowledge source at extremely deep or circular web structures.

By following these patterns, we ensure ClawdView remains a high-performance yet "good citizen" on the Google Cloud platform.
