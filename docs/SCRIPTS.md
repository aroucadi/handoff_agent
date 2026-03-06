# 🛠️ Synapse & ClawdView Scripts Directory

This guide explains the purpose, usage, and **execution order** of every automation script in the `scripts/` folder. 

---

## 🚦 Recommended Execution Order

To set up a fresh environment from scratch, follow this exact sequence:

1.  **`demo-setup.ps1`**: Prepare your local environment (Dependencies + Assets).
2.  **`deploy.ps1`**: Provision cloud infrastructure and deploy code.
3.  **`seed_all.py`**: Wipe and re-populate the system with high-fidelity demo data.
4.  **`test_pipeline.py`**: Verify that the entire end-to-end pipeline is healthy.

---

## 📂 Categorized Script List

### 🏗️ Deployment & Environment
| Script | OS | Description |
|---|---|---|
| `demo-setup.ps1` | Win | Installs all Node/Python dependencies and syncs static skill-graphs to GCS. |
| `deploy.ps1` | Win | Multi-phase PowerShell script: Terraform + Cloud Build + Firebase + Verification. |
| `start-local.ps1` | Win | Orchestrates 7+ local processes (APIs and Frontends) for offline development. |
| `teardown.ps1` | Win | Full resource destruction via Terraform + manual GCS/Firestore cleanup. |
| `bump-version.ps1`| Win | Updates version strings across the monorepo for release management. |

### 🧬 Data Seeding & Simulation
| Script | OS | Description |
|---|---|---|
| **`seed_all.py`** | All | **The Grand Orchestrator**. Resets DB, generates PDFs, seeds CRM, and triggers first graphs. |
| `journey_runner.py` | All | Simulates a user onboarding a new tenant and closing deals. Supports `--lite` mode. |
| `generate_contracts.py`| All | Generates realistic, multi-page industry-specific PDFs (MSA, SLA). |
| `seed_rag.py` | All | Scrapes the Knowledge Center and builds the product-knowledge vector base. |
| `seed_hub.py` | All | Initializes a default tenant and CRM mapping in the Hub API. |

### 🔍 Maintenance & Testing
| Script | OS | Description |
|---|---|---|
| `test_pipeline.py` | All | Headless integration test. Fires a webhook and polls Firestore for graph completion. |
| `cleanup_db.py` | All | Atomic reset script. Purges all Firestore collections and specific GCS prefixes. |
| `query_graph.py` | All | Utility to perform raw Firestore Lookups or Vector Searches for debugging. |

---

## 🍎 macOS / Linux Notes
While our primary automation is `.ps1` for Windows, we maintain a core set of `.sh` scripts in the same folder.
*   Use `bash scripts/demo-setup.sh` and `bash scripts/deploy.sh`.
*   All `.py` scripts are natively cross-platform and should be run with `python3` or `py`.

---

## 💡 Pro-Tip: The `--lite` Flag
When running `journey_runner.py` or `seed_rag.py`, use the `--lite` flag to stay within GCP safe-usage limits:
```bash
py scripts/journey_runner.py --lite
```
