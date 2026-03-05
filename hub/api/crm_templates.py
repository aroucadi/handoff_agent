"""
Synapse Hub — CRM Field Mapping Templates

Pre-built field mapping templates for supported CRM platforms.
Inspired by how Zapier/Workato use Schema Discovery APIs
(Salesforce sObject Describe, HubSpot Properties API, Dynamics EntityMetadata)
to auto-populate field mappings for tenants.

Each template maps SOURCE CRM field paths → Synapse internal field names.
Dot-notation is supported for nested objects (e.g., "sobject.Name").
"""

from __future__ import annotations


# Synapse internal schema — the canonical field names used by the graph generator
SYNAPSE_SCHEMA_FIELDS = [
    "deal_id",
    "company_name",
    "deal_value",
    "close_date",
    "industry",
    "employee_count",
    "sla_days",
    "products",
    "contacts",
    "risks",
    "success_metrics",
    "sales_transcript",
    "contract_pdf_url",
    "contract_file_uri",
    "csm_id",
]


# ── Salesforce ───────────────────────────────────────────────────
# Based on Salesforce sObject Describe API field names for
# Opportunity and Account objects.
SALESFORCE_TEMPLATE = {
    "Id": "deal_id",
    "Account.Name": "company_name",
    "Amount": "deal_value",
    "CloseDate": "close_date",
    "Account.Industry": "industry",
    "Account.NumberOfEmployees": "employee_count",
    "SLA_Days__c": "sla_days",
    "OpportunityLineItems": "products",
    "OpportunityContactRoles": "contacts",
    "Risk_Factors__c": "risks",
    "Success_Metrics__c": "success_metrics",
    "Sales_Transcript__c": "sales_transcript",
    "Contract_PDF_URL__c": "contract_pdf_url",
    "OwnerId": "csm_id",
}


# ── HubSpot ──────────────────────────────────────────────────────
# Based on HubSpot Properties API field names for Deal and Company
# objects. HubSpot nests deal properties under "properties".
HUBSPOT_TEMPLATE = {
    "properties.hs_object_id": "deal_id",
    "properties.dealname": "company_name",
    "properties.amount": "deal_value",
    "properties.closedate": "close_date",
    "associations.company.properties.industry": "industry",
    "associations.company.properties.numberofemployees": "employee_count",
    "properties.sla_days": "sla_days",
    "associations.line_items": "products",
    "associations.contacts": "contacts",
    "properties.risk_factors": "risks",
    "properties.success_metrics": "success_metrics",
    "properties.sales_transcript": "sales_transcript",
    "properties.contract_pdf_url": "contract_pdf_url",
    "properties.hubspot_owner_id": "csm_id",
}


# ── Microsoft Dynamics 365 ───────────────────────────────────────
# Based on Dynamics 365 Web API EntityMetadata field names for
# Opportunity and Account entities.
DYNAMICS_TEMPLATE = {
    "opportunityid": "deal_id",
    "customerid_account.name": "company_name",
    "estimatedvalue": "deal_value",
    "estimatedclosedate": "close_date",
    "customerid_account.industrycode": "industry",
    "customerid_account.numberofemployees": "employee_count",
    "new_sladays": "sla_days",
    "opportunity_products": "products",
    "opportunity_contacts": "contacts",
    "new_riskfactors": "risks",
    "new_successmetrics": "success_metrics",
    "new_salestranscript": "sales_transcript",
    "new_contractpdfurl": "contract_pdf_url",
    "ownerid": "csm_id",
}


# ── Custom / Synapse Simulator ──────────────────────────────────
# Identity mapping — the Synapse CRM simulator already uses the
# internal field names directly (this is backward-compatible).
CUSTOM_TEMPLATE = {
    "deal_id": "deal_id",
    "company_name": "company_name",
    "deal_value": "deal_value",
    "close_date": "close_date",
    "industry": "industry",
    "employee_count": "employee_count",
    "sla_days": "sla_days",
    "products": "products",
    "contacts": "contacts",
    "risks": "risks",
    "success_metrics": {
        "target": "success_metrics",
        "item_map": {
            "metric": "name",
            "current_value": "baseline",
            "target_value": "target",
            "timeframe": "timeline",
        },
        "preserve_unmapped": True,
    },
    "sales_transcript": "sales_transcript",
    "contract_pdf_url": "contract_pdf_url",
    "contract_file_uri": "contract_file_uri",
    "csm_id": "csm_id",
}


# ── Template Registry ───────────────────────────────────────────

CRM_TEMPLATES: dict[str, dict[str, object]] = {
    "salesforce": SALESFORCE_TEMPLATE,
    "hubspot": HUBSPOT_TEMPLATE,
    "dynamics": DYNAMICS_TEMPLATE,
    "custom": CUSTOM_TEMPLATE,
}


# ── CRM Setup Instructions ─────────────────────────────────────

CRM_SETUP_INSTRUCTIONS: dict[str, dict] = {
    "salesforce": {
        "title": "Salesforce Integration",
        "steps": [
            "Navigate to Setup → Workflow & Approvals → Outbound Messages",
            "Create a new Outbound Message triggered on Opportunity Stage = 'Closed Won'",
            "Set the Endpoint URL to your Synapse webhook URL (shown below)",
            "Select the fields listed in the mapping table",
            "Activate the workflow rule",
        ],
        "docs_url": "https://help.salesforce.com/s/articleView?id=sf.workflow_managing_outbound_messages.htm",
    },
    "hubspot": {
        "title": "HubSpot Integration",
        "steps": [
            "Navigate to Settings → Integrations → Private Apps",
            "Create a new Private App with 'crm.objects.deals.read' scope",
            "Go to Workflows → Create workflow → Deal-based",
            "Set trigger: Deal Stage = 'Closed Won'",
            "Add action: 'Send webhook' with your Synapse URL (shown below)",
        ],
        "docs_url": "https://knowledge.hubspot.com/workflows/how-do-i-use-webhooks-with-hubspot-workflows",
    },
    "dynamics": {
        "title": "Dynamics 365 Integration",
        "steps": [
            "Navigate to Advanced Settings → Customizations → Customize the System",
            "Go to Processes → New → Workflow (Opportunity entity)",
            "Set trigger: Status Reason = 'Won'",
            "Add step: 'Perform Action' → HTTP Request to your Synapse URL (shown below)",
            "Alternatively, use Power Automate with the 'When a row is modified' trigger",
        ],
        "docs_url": "https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/customize/workflow-processes",
    },
    "custom": {
        "title": "Custom CRM / API Integration",
        "steps": [
            "Configure your CRM to send a POST request to the Synapse webhook URL on deal events",
            "Include an HMAC-SHA256 signature in the X-Webhook-Signature header",
            "Use the field mapping below to ensure your payload matches the expected schema",
            "Send a test webhook to verify the connection",
        ],
        "docs_url": None,
    },
}


def get_template_for_crm(crm_type: str) -> dict[str, str]:
    """Get the default field mapping template for a given CRM type."""
    return CRM_TEMPLATES.get(crm_type, CUSTOM_TEMPLATE).copy()


def get_setup_instructions(crm_type: str) -> dict:
    """Get CRM-specific setup instructions."""
    return CRM_SETUP_INSTRUCTIONS.get(crm_type, CRM_SETUP_INSTRUCTIONS["custom"])
