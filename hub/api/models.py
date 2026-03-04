"""
Synapse Hub — Data Models

Pydantic models for tenant configuration, products, CRM connection,
and agent settings. Stored in Firestore collection: tenants/{tenant_id}
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────

class CrmType(str, Enum):
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    DYNAMICS = "dynamics"
    CUSTOM = "custom"


class TenantStatus(str, Enum):
    CONFIGURING = "configuring"
    READY = "ready"
    ACTIVE = "active"


class AuthMethod(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"


# ── Sub-models ───────────────────────────────────────────────────

class Product(BaseModel):
    product_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    description: str = ""
    node_id: str = ""  # kebab-case, auto-generated from name
    knowledge_generated: bool = False
    node_count: int = 0


class CrmConnection(BaseModel):
    crm_type: CrmType = CrmType.CUSTOM
    crm_url: Optional[str] = None
    auth_method: AuthMethod = AuthMethod.API_KEY
    # Credentials are stored as references, not plaintext
    credentials_ref: Optional[str] = None
    connected: bool = False
    field_mapping: dict = Field(default_factory=lambda: {
        # Default mapping: source CRM field → WebhookPayload field
        "deal_id": "deal_id",
        "company_name": "company_name",
        "deal_value": "deal_value",
        "close_date": "close_date",
        "industry": "industry",
        "products": "products",
        "contacts": "contacts",
        "risks": "risks",
        "success_metrics": "success_metrics",
        "sales_transcript": "sales_transcript",
        "contract_pdf_url": "contract_pdf_url",
    })


class AgentConfig(BaseModel):
    roles: list[str] = Field(default_factory=lambda: ["csm", "sales", "support"])
    persona: str = ""
    brand_name: str = ""


# ── Main Tenant Config ──────────────────────────────────────────

class TenantConfig(BaseModel):
    tenant_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str
    brand_name: str = ""
    crm: CrmConnection = Field(default_factory=CrmConnection)
    products: list[Product] = Field(default_factory=list)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    webhook_url: str = ""  # graph-generator endpoint for this tenant
    status: TenantStatus = TenantStatus.CONFIGURING
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ── API Request/Response Models ──────────────────────────────────

class CreateTenantRequest(BaseModel):
    name: str
    brand_name: str = ""
    crm_type: CrmType = CrmType.CUSTOM


class UpdateTenantRequest(BaseModel):
    name: Optional[str] = None
    brand_name: Optional[str] = None
    crm: Optional[CrmConnection] = None
    agent: Optional[AgentConfig] = None
    webhook_url: Optional[str] = None
    status: Optional[TenantStatus] = None


class AddProductRequest(BaseModel):
    name: str
    description: str = ""


class TenantListResponse(BaseModel):
    tenants: list[TenantConfig]
    total: int
