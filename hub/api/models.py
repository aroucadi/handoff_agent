"""
Synapse Hub — Data Models

Pydantic models for tenant configuration, products, CRM connection,
and agent settings. Stored in Firestore collection: tenants/{tenant_id}
"""

from __future__ import annotations

import secrets

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


class IntegrationStatus(str, Enum):
    NOT_CONFIGURED = "not_configured"
    PENDING = "pending"
    VERIFIED = "verified"
    ERROR = "error"


class AuthMethod(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"


class KnowledgeSourceType(str, Enum):
    WEBSITE_CRAWL = "website_crawl"
    DOCUMENT_UPLOAD = "document_upload"
    ZENDESK_API = "zendesk_api"
    CONFLUENCE_API = "confluence_api"


class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    ERROR = "error"


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
    # Stage Normalization: source stage -> canonical Synapse stage
    # Canonical stages: closed_won, prospecting, qualification, negotiation, implemented, closed_lost
    stage_mapping: dict[str, str] = Field(default_factory=dict)


class RoleViewConfig(BaseModel):
    display_name: str
    stage_filter: list[str] = Field(default_factory=list)
    icon: str = "LayoutDashboard"


class AgentConfig(BaseModel):
    roles: list[str] = Field(default_factory=lambda: ["csm", "sales", "support"])
    persona: str = ""
    brand_name: str = ""
    # Role Views: role_id -> view config (filter, label)
    role_views: dict[str, RoleViewConfig] = Field(default_factory=lambda: {
        "csm": RoleViewConfig(display_name="Success Dashboard", stage_filter=["closed_won"], icon="LayoutDashboard"),
        "sales": RoleViewConfig(display_name="Pipeline Intelligence", stage_filter=["prospecting", "qualification", "negotiation"], icon="Zap"),
        "support": RoleViewConfig(display_name="Deployment Hub", stage_filter=["implemented"], icon="Database"),
        "strategy": RoleViewConfig(display_name="Win-Back Suite", stage_filter=["closed_lost"], icon="Briefcase")
    })
    # Stage Display: internal stage -> human-readable label
    stage_display_config: dict[str, str] = Field(default_factory=lambda: {
        "closed_won": "Won",
        "prospecting": "Prospecting",
        "qualification": "Qualifying",
        "negotiation": "Negotiating",
        "implemented": "Deployed",
        "closed_lost": "Lost"
    })


class KnowledgeSource(BaseModel):
    source_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    type: KnowledgeSourceType
    uri: str  # URL, GCS path, or API endpoint
    name: str = ""
    config: dict = Field(default_factory=dict) # Connector-specific configuration
    status: SyncStatus = SyncStatus.PENDING
    last_synced_at: Optional[str] = None


# ── Main Tenant Config ──────────────────────────────────────────

class TenantConfig(BaseModel):
    tenant_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str
    brand_name: str = ""
    crm: CrmConnection = Field(default_factory=CrmConnection)
    products: list[Product] = Field(default_factory=list)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    knowledge_sources: list[KnowledgeSource] = Field(default_factory=list)
    # Product Aliases: source CRM product name -> internal canonical slug
    product_alias_map: dict[str, str] = Field(default_factory=dict)
    # Terminology Overrides: generic key -> tenant label (e.g., {"account": "Client", "case": "Opportunity"})
    terminology_overrides: dict[str, str] = Field(default_factory=lambda: {
        "account": "Client",
        "case": "Deal"
    })
    webhook_url: str = ""  # auto-provisioned: graph-generator ingest endpoint
    webhook_secret: str = Field(
        default_factory=lambda: secrets.token_hex(32)  # HMAC-SHA256 key
    )
    integration_status: IntegrationStatus = IntegrationStatus.NOT_CONFIGURED
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
    knowledge_sources: Optional[list[KnowledgeSource]] = None
    product_alias_map: Optional[dict[str, str]] = None
    webhook_url: Optional[str] = None
    status: Optional[TenantStatus] = None


class AddProductRequest(BaseModel):
    name: str
    description: str = ""



class TenantListResponse(BaseModel):
    tenants: list[TenantConfig]
    total: int


class TestConnectionRequest(BaseModel):
    crm_type: CrmType
    crm_url: str
    auth_method: AuthMethod


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None
