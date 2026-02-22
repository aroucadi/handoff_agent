# 🚀 Synapse Developer Onboarding Guide

Welcome to the Synapse monorepo! This repository houses the entire Level 5 AI Voice Agent for Customer Success platform. It contains multiple independent microservices, a frontend dashboard, shared libraries, and infrastructure-as-code (IaC). 

This guide will help you understand how the repository is structured, how we manage global versioning, and how to use our shared automation scripts.

---

## 1. Monorepo Repository Structure

The codebase is split conceptually into Frontend, Backend Microservices, Infrastructure, and Shared Tooling.

```text
synapse_agent/
├── backend/            # (Microservice) The real-time FastAPI WebSocket/WebRTC bridge linking the UI to Gemini Live
├── crm-simulator/      # (Microservice) A mock FastAPI CRM used to trigger deals and test the closed-won webhooks
├── graph-generator/    # (Microservice) A FastAPI asynchronous multi-agent pipeline generating knowledge nodes
├── core/               # (Shared Library) Shared Python database models, LLM prompts, and Firestore connections
├── frontend/           # (UI Application) React + Vite dashboard displaying the graph topology and Live Agent Voice interface
├── infra/              # (Infrastructure) Terraform configurations to deploy Cloud Run, Storage, and Firestore
├── scripts/            # (Tooling) One-click automation scripts (Bash + PowerShell) for deploying or bumping versions
├── docs/               # Technical Documentation hub covering AI Agents, APIs, and Architecture
├── synapse.yaml        # The Global Monorepo Manifest
└── CONTRIBUTING.md     # Quickstart guide for setting up local dependencies (venv, npm)
```

> **Developer Note:** The three Python microservices (`backend/`, `crm-simulator/`, and `graph-generator/`) all rely on the shared `core/` package. When building Docker images, the build context is run from the **Root** of this repository so the `core/` directory can be legitimately mounted into each microservice container.

---

## 2. The Monorepo Manifest (`synapse.yaml`)

Because this repo runs 4 parallel applications, we utilize a single **Root Manifest** (`synapse.yaml`) to coordinate the platform.

### Global Versioning
To prevent API mismatch, we enforce a unified version number (e.g., `v3.1.0`) across all sub-components. **Do not manually edit version strings in Python or Node.js files.** 

Instead, perform version bumps using our manifest tooling:
1. Open `synapse.yaml`.
2. Update the `global_version: X.Y.Z` string.
3. Run `bash scripts/bump-version.sh` (or `.ps1` on Windows).
4. The script will dynamically inject the global version downward into `frontend/package.json` and the three `main.py` FastAPI definitions.

### Infrastructure Truth
The manifest also contains the explicit `gcp_project` and `firebase_project` identifiers used by our zero-touch CI/CD scripts.

---

## 3. Automation Scripts (`scripts/`)

We embrace "One-Click" automation for developers regardless of their OS (Windows PowerShell `.ps1` or macOS/Linux Bash `.sh`). 

| Script | Purpose | Execution Example |
|---|---|---|
| `bump-version` | Propagates the version from `synapse.yaml` globally | `bash scripts/bump-version.sh` |
| `start-local` | Spins up the UI and all microservices concurrently | `bash scripts/start-local.sh` |
| `seed-graphs` | Injects synthetic test nodes into Firestore | `bash scripts/seed-graphs.sh` |
| `deploy` | Non-interactive Terraform and Cloud Run/Firebase pipeline | `bash scripts/deploy.sh <gcp-project>` |
| `teardown` | Reverses `deploy` and destroys all cloud assets safely | `bash scripts/teardown.sh <gcp-project>` |

---

## Where to go next?
* If you want to spin up the code locally immediately, follow [CONTRIBUTING.md](../CONTRIBUTING.md).
* If you want to understand *how* the Gemini Live agent actually works, read [AI_AGENTS.md](AI_AGENTS.md).
