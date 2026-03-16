"""
CRM Simulator — Platform Webhook Emitters

Wraps deal data in CRM-platform-specific webhook formats to test
the dynamic field mapping engine end-to-end.

Each emitter transforms the simulator's internal deal model into
the webhook payload format that the real CRM platform would send:
- Salesforce: sObject-based Outbound Message format
- HubSpot: Properties-based webhook format
- Dynamics 365: Entity-based webhook format
- Custom: Pass-through (backward compatible)
"""

from __future__ import annotations


def emit_salesforce(deal: dict) -> dict:
    """Wrap deal data in Salesforce Outbound Message format.

    Salesforce webhooks use sObject field names with the Account
    relationship for related company data.
    """
    return {
        "Id": deal.get("deal_id", ""),
        "Account": {
            "Name": deal.get("company_name", ""),
            "Industry": deal.get("industry", ""),
            "NumberOfEmployees": deal.get("employee_count"),
        },
        "Amount": deal.get("deal_value", 0),
        "CloseDate": str(deal.get("close_date", "")),
        "SLA_Days__c": deal.get("sla_days"),
        "OpportunityLineItems": deal.get("products", []),
        "OpportunityContactRoles": deal.get("contacts", []),
        "Risk_Factors__c": deal.get("risks", []),
        "Success_Metrics__c": deal.get("success_metrics", []),
        "Sales_Transcript__c": deal.get("sales_transcript"),
        "Contract_PDF_URL__c": deal.get("contract_pdf_url"),
        "OwnerId": deal.get("csm_id"),
        # Salesforce event metadata
        "_sf_event": "Opportunity.Closed_Won",
        "_sf_org_id": "00D000000000000",
    }


def emit_hubspot(deal: dict) -> dict:
    """Wrap deal data in HubSpot webhook format.

    HubSpot webhooks nest deal fields under "properties" and
    related objects under "associations".
    """
    return {
        "objectId": deal.get("deal_id", ""),
        "eventType": "deal.propertyChange",
        "propertyName": "dealstage",
        "propertyValue": "closedwon",
        "properties": {
            "hs_object_id": deal.get("deal_id", ""),
            "dealname": deal.get("company_name", ""),
            "amount": str(deal.get("deal_value", 0)),
            "closedate": str(deal.get("close_date", "")),
            "sla_days": deal.get("sla_days"),
            "risk_factors": deal.get("risks", []),
            "success_metrics": deal.get("success_metrics", []),
            "sales_transcript": deal.get("sales_transcript"),
            "contract_pdf_url": deal.get("contract_pdf_url"),
            "hubspot_owner_id": deal.get("csm_id"),
        },
        "associations": {
            "company": {
                "properties": {
                    "name": deal.get("company_name", ""),
                    "industry": deal.get("industry", ""),
                    "numberofemployees": deal.get("employee_count"),
                },
            },
            "line_items": deal.get("products", []),
            "contacts": deal.get("contacts", []),
        },
    }


def emit_dynamics(deal: dict) -> dict:
    """Wrap deal data in Dynamics 365 webhook format.

    Dynamics uses entity-based field names with relationship
    navigation properties for related records.
    """
    return {
        "opportunityid": deal.get("deal_id", ""),
        "customerid_account": {
            "name": deal.get("company_name", ""),
            "industrycode": deal.get("industry", ""),
            "numberofemployees": deal.get("employee_count"),
        },
        "estimatedvalue": deal.get("deal_value", 0),
        "estimatedclosedate": str(deal.get("close_date", "")),
        "new_sladays": deal.get("sla_days"),
        "opportunity_products": deal.get("products", []),
        "opportunity_contacts": deal.get("contacts", []),
        "new_riskfactors": deal.get("risks", []),
        "new_successmetrics": deal.get("success_metrics", []),
        "new_salestranscript": deal.get("sales_transcript"),
        "new_contractpdfurl": deal.get("contract_pdf_url"),
        "ownerid": deal.get("csm_id"),
        # Dynamics event metadata
        "_dynamics_event": "Update",
        "_dynamics_entity": "opportunity",
    }


def emit_custom(deal: dict) -> dict:
    """Pass-through emitter — backward compatible with current behavior."""
    return deal


# Registry of emitters
EMITTERS = {
    "salesforce": emit_salesforce,
    "hubspot": emit_hubspot,
    "dynamics": emit_dynamics,
    "custom": emit_custom,
}


def emit_webhook_payload(deal: dict, crm_platform: str = "custom") -> dict:
    """Emit a webhook payload in the format of the specified CRM platform.

    Args:
        deal: The internal deal dict (from the simulator's data model).
        crm_platform: One of "salesforce", "hubspot", "dynamics", "custom".

    Returns:
        Payload formatted as the specified CRM platform would send it.
    """
    emitter = EMITTERS.get(crm_platform, emit_custom)
    return emitter(deal)
