# Handoff — Deployment Proof

## Infrastructure Provisioned via Terraform

### GCS Buckets
| Bucket | Purpose | Features |
|---|---|---|
| `{project}-skill-graphs` | Skill graph markdown storage | Versioning enabled, CORS configured |
| `{project}-handoff-uploads` | CRM file uploads (contracts, transcripts) | Lifecycle rule → Nearline after 90d |

### Firestore
| Collection | Purpose |
|---|---|
| `skill_graphs/{client_id}` | Client graph status (ready/generating) |
| `skill_graphs/{client_id}/nodes/{node_id}` | Node metadata, links, 768d embeddings |

### Cloud Run Services
| Service | Port | Resources | Purpose |
|---|---|---|---|
| `handoff-api` | 8000 | 2 CPU, 1Gi RAM, 600s timeout | Backend API + WebSocket |
| `handoff-graph-generator` | 8002 | 2 CPU, 2Gi RAM, 900s timeout | Graph generation pipeline |

### Other GCP Resources
| Resource | Purpose |
|---|---|
| Artifact Registry `handoff` | Docker image repository |
| Secret Manager `gemini-api-key` | Gemini API key storage |
| Service Account `handoff-runner` | Cloud Run identity with GCS/Firestore/SM access |
| Firebase Web App | Frontend hosting |

### APIs Enabled
- Cloud Run (`run.googleapis.com`)
- Firestore (`firestore.googleapis.com`)
- Cloud Storage (`storage-api.googleapis.com`)
- AI Platform (`aiplatform.googleapis.com`)
- Secret Manager (`secretmanager.googleapis.com`)
- Cloud Build (`cloudbuild.googleapis.com`)
- Firebase (`firebase.googleapis.com`)
- Generative Language (`generativelanguage.googleapis.com`)
- Artifact Registry (`artifactregistry.googleapis.com`)

## Terraform Modules

```
infra/
├── main.tf              # Root: provider, APIs, Secret Manager
├── variables.tf         # project_id, region, environment
├── outputs.tf           # All service URLs + bucket names
├── terraform.tfvars.example
└── modules/
    ├── storage/         # GCS buckets with lifecycle rules
    ├── firestore/       # Native mode database
    ├── cloud-run/       # 2 services + Artifact Registry + IAM
    └── firebase/        # Firebase Web App
```

## Local Development Setup

```bash
# 1. Clone
git clone https://github.com/aroucadi/handoff_agent.git
cd handoff_agent

# 2. Set environment
export GEMINI_API_KEY="your-key"
export PROJECT_ID="your-project"

# 3. Start all services
./scripts/demo-setup.sh   # Seeds static graphs
./scripts/start-local.sh  # Starts all 4 services

# 4. Open
# CRM Simulator:  http://localhost:5173
# Handoff Voice:   http://localhost:5174
# Backend API:     http://localhost:8000/health
# Graph Generator: http://localhost:8002/health
```

## Release Tags

| Tag | Release | Date | Key Feature |
|---|---|---|---|
| `v0.1.0` | R0 — Foundation | 2026-02-20 | CRM Simulator, IaC base, static skill graphs |
| `v0.2.0` | R1 — Skill Graph Engine | 2026-02-20 | Gemini 3.1 Pro extraction, ADK agent, embeddings |
| `v0.3.0` | R2 — Voice Agent | 2026-02-21 | Gemini Live audio streaming, WebSocket sessions |
| `v0.4.0` | R3 — Full UI | 2026-02-21 | Dashboard, split-screen briefing, React Flow graph |
| `v1.0.0` | R4 — Submission | 2026-02-21 | Demo polish, documentation, deployment scripts |
