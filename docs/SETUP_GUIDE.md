# 🏁 ClawdView Zero-Knowledge Setup Guide

Follow these steps to deploy the entire **ClawdView** platform from scratch. This guide is designed for users with zero prior knowledge of the codebase.

---

## 📋 Prerequisites

### 1. Google Cloud Environment
*   **Project**: Create a new project at [GCP Console](https://console.cloud.google.com/).
*   **Billing**: Ensure billing is enabled.
*   **Permissions**: Your account must have `Owner` or `Editor` permissions.
*   **CLI**: Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) and run `gcloud auth login`.

### 2. Local Development Tools
| Tool | Minimum Version | Note |
|---|---|---|
| **Python** | 3.11+ | Add to PATH during install. |
| **Node.js** | 20+ | LTS version recommended. |
| **Terraform** | 1.5+ | [Download here](https://developer.hashicorp.com/terraform/downloads). |
| **PowerShell** | 7.0+ | **Required for Windows** (built-in 5.1 is incompatible). |

---

## 🏗️ Step 1: Environment Preparation

Open a **PowerShell 7** terminal in the project root and execute the following:

```powershell
# 1. Initialize all submodules and dependencies
.\scripts\demo-setup.ps1

# 2. Get a Gemini API Key from https://aistudio.google.com/
$env:GEMINI_API_KEY = "AIzaSy..."
```

---

## 🚀 Step 2: Full Infrastructure Deployment

This single atomic script handle container builds, database provisioning, and web hosting.

```powershell
# Replace with your actual project ID
.\scripts\deploy.ps1 -ProjectId "your-project-id"
```

> [!NOTE]
> This process takes **5–10 minutes**. It uses Google Cloud Build to build 4 Docker images remotely, so a heavy local machine is not required.

---

## 🧬 Step 3: High-Fidelity Data Seeding

Once the infrastructure is live, populate it with realistic enterprise demo data.

```powershell
# The "Perfect Run" orchestrator
py scripts/seed_all.py
```

*   **Result**: Generates 15+ multi-page contracts, seeds the CRM, and builds high-fidelity knowledge graphs automatically.

---

## 🔍 Step 4: Verification

Run the automated governance check:

```powershell
py scripts/test_pipeline.py
```

If you see `✅ Pipeline End-to-End Governance Tested Successfully!`, your demo is ready.

---

## 🛠️ Troubleshooting & Common Issues

### 1. `CommandNotFoundException` for `py`
If `py` is not recognized, try `python` or `python3`. Ensure you selected "Add Python to PATH" during installation.

### 2. `npm : The term 'npm' is not recognized`
Ensure Node.js is installed. You must restart your terminal after installing Node for changes to take effect.

### 3. `terraform : Access is denied`
This usually happens if the Terraform `.exe` wasn't moved to a folder in your PATH. Try moving `terraform.exe` to `C:\Windows\System32` or a dedicated Tools folder.

### 4. `RESOURCE_EXHAUSTED` (API Errors)
We have implemented exponential backoff. If you see this in the logs, the system will automatically pause and retry. Do not cancel the script.

---

## 🧹 Cleanup
To destroy all resources and stop GCP billing:
```powershell
.\scripts\teardown.ps1 -ProjectId "your-project-id"
```
