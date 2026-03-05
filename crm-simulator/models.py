"""CRM Simulator — Pydantic Data Models.

These models define the CRM deal structure that mirrors what a real Salesforce-like
CRM would provide. Pre-seeded with the GlobalManufacturing Co. demo data.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DealStage(str, Enum):
    """CRM deal pipeline stages."""

    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    IMPLEMENTED = "implemented"


class Contact(BaseModel):
    """A stakeholder contact within a deal."""

    name: str
    title: str
    email: Optional[str] = None
    role: str = Field(description="champion | economic_buyer | technical_evaluator | blocker")
    pain_point: Optional[str] = None
    commitment: Optional[str] = None
    notes: Optional[str] = None


class DealProduct(BaseModel):
    """A product included in the deal."""

    name: str
    annual_value: Optional[float] = None


class Risk(BaseModel):
    """An identified risk for the deal."""

    description: str
    severity: str = Field(default="medium", description="low | medium | high | critical")
    source: str = Field(default="sales_notes", description="Where this risk was identified")


class SuccessMetric(BaseModel):
    """A measurable success metric for the client."""

    metric: str
    current_value: Optional[str] = None
    target_value: Optional[str] = None
    timeframe: Optional[str] = None


class Deal(BaseModel):
    """A CRM deal record — the core data model."""

    deal_id: str
    company_name: str
    deal_value: float
    stage: DealStage = DealStage.PROSPECTING
    products: list[DealProduct] = []
    close_date: Optional[date] = None
    sla_days: Optional[int] = None
    csm_id: Optional[str] = None
    industry: str = ""
    employee_count: Optional[int] = None
    contacts: list[Contact] = []
    risks: list[Risk] = []
    success_metrics: list[SuccessMetric] = []
    sales_transcript: Optional[str] = None
    contract_pdf_url: Optional[str] = None
    webhook_url: Optional[str] = None
    crm_platform: str = "custom"  # salesforce | hubspot | dynamics | custom
    tenant_id: Optional[str] = None  # Hub tenant ID for ingest routing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Webhook tracking
    webhook_fired: bool = False
    webhook_response: Optional[str] = None


class DealUpdate(BaseModel):
    """Partial update for a deal."""

    company_name: Optional[str] = None
    deal_value: Optional[float] = None
    stage: Optional[DealStage] = None
    sla_days: Optional[int] = None
    csm_id: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    sales_transcript: Optional[str] = None
    webhook_url: Optional[str] = None
    crm_platform: Optional[str] = None
    tenant_id: Optional[str] = None


class DealCreate(BaseModel):
    deal_id: Optional[str] = None
    company_name: str
    deal_value: float
    stage: DealStage = DealStage.PROSPECTING
    products: list[DealProduct] = []
    close_date: Optional[date] = None
    sla_days: Optional[int] = None
    csm_id: Optional[str] = None
    industry: str = ""
    employee_count: Optional[int] = None
    contacts: list[Contact] = []
    risks: list[Risk] = []
    success_metrics: list[SuccessMetric] = []
    sales_transcript: Optional[str] = None
    contract_pdf_url: Optional[str] = None
    webhook_url: Optional[str] = None
    crm_platform: str = "custom"
    tenant_id: Optional[str] = None


class WebhookPayload(BaseModel):
    """The payload sent when a deal moves to Closed Won."""

    deal_id: str
    company_name: str
    deal_value: float
    stage: str
    products: list[dict]
    close_date: str
    sla_days: Optional[int]
    csm_id: Optional[str]
    industry: str
    employee_count: Optional[int]
    contacts: list[dict]
    risks: list[dict]
    success_metrics: list[dict]
    sales_transcript: Optional[str]
    contract_pdf_url: Optional[str]
    contract_file_uri: Optional[str] = None
    historical_deals: list[dict] = Field(default_factory=list, description="Other deals mapping to this account")
