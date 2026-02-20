"""Handoff Backend — FastAPI Application Entry Point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config

app = FastAPI(
    title="Handoff API",
    description="Gemini Live voice agent for B2B SaaS customer success handoffs",
    version="0.1.0",
)

# CORS — allow CRM Simulator and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint — required for Cloud Run."""
    return {"status": "ok", "version": "0.1.0", "environment": config.environment}


@app.post("/api/webhooks/crm/deal-closed")
async def webhook_deal_closed(request: Request):
    """Receive webhook from CRM Simulator when a deal is marked Closed Won.

    In R0, this logs the payload and returns acknowledgement.
    In R1, this triggers the Graph Generator.
    """
    payload = await request.json()
    deal_id = payload.get("deal_id", "unknown")
    company = payload.get("company_name", "unknown")
    print(f"[WEBHOOK] Deal closed: {deal_id} — {company}")
    print(f"[WEBHOOK] Full payload: {payload}")

    return JSONResponse(
        status_code=200,
        content={
            "status": "received",
            "deal_id": deal_id,
            "message": f"Webhook received for {company}. Graph generation will be triggered in R1.",
        },
    )


@app.get("/api/clients")
async def list_clients():
    """List all client accounts assigned to the authenticated CSM.

    Placeholder in R0 — will connect to Firestore in R1.
    """
    return {"clients": [], "message": "Client listing will be available after R1 (graph generation)."}
