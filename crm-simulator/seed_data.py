"""CRM Simulator — Seed Data.

Pre-loaded demo deal: GlobalManufacturing Co. — the scenario from SYNAPSE PRD §3.
This data is used for hackathon demos and is fully realistic.
"""

from datetime import date

from models import (
    Contact,
    Deal,
    DealProduct,
    DealStage,
    Risk,
    SuccessMetric,
)

DEMO_DEALS: list[Deal] = [
    Deal(
        deal_id="OPP-2026-GM001",
        company_name="GlobalManufacturing Co.",
        deal_value=2_000_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="VeloSaaS CPQ", annual_value=1_200_000),
            DealProduct(name="Revenue Cloud", annual_value=800_000),
        ],
        close_date=date(2026, 2, 20),
        sla_days=90,
        csm_id="csm-alex-demo",
        industry="manufacturing",
        employee_count=500,
        contacts=[
            Contact(
                name="Sarah Chen",
                title="VP Sales Operations",
                email="schen@globalmanufacturing.com",
                role="champion",
                pain_point="3-week quote cycle for custom orders costing them deals",
                notes="Internal champion who drove this deal. Very hands-on, expects weekly check-ins.",
            ),
            Contact(
                name="Marcus Webb",
                title="CFO",
                email="mwebb@globalmanufacturing.com",
                role="economic_buyer",
                commitment="6-month payback period",
                notes="Signed off based on ROI analysis. Will be watching renewal metrics closely.",
            ),
            Contact(
                name="Raj Patel",
                title="Director of IT",
                email="rpatel@globalmanufacturing.com",
                role="technical_evaluator",
                pain_point="Legacy SAP ERP integration complexity",
                notes="Concerned about data migration timelines. Has been burned by vendor promises before.",
            ),
        ],
        risks=[
            Risk(
                description="90-day go-live SLA is aggressive — similar manufacturing clients averaged 120 days",
                severity="high",
                source="implementation_analysis",
            ),
            Risk(
                description="Legacy SAP ERP integration not fully scoped in contract — came up in last sales call but wasn't resolved",
                severity="high",
                source="sales_call_Q4_2025",
            ),
            Risk(
                description="Raj Patel (IT Director) is skeptical of vendor timelines based on past experience",
                severity="medium",
                source="stakeholder_analysis",
            ),
        ],
        success_metrics=[
            SuccessMetric(
                metric="Quote cycle time",
                current_value="3 weeks",
                target_value="48 hours",
                timeframe="90 days post go-live",
            ),
            SuccessMetric(
                metric="CPQ adoption across sales team",
                current_value="0%",
                target_value="80%",
                timeframe="60 days post go-live",
            ),
            SuccessMetric(
                metric="Revenue forecast accuracy",
                current_value="65%",
                target_value="90%",
                timeframe="6 months post go-live",
            ),
        ],
        sales_transcript="""
SALES CALL TRANSCRIPT — GlobalManufacturing Co. Final Negotiation
Date: February 15, 2026
Attendees: James Morton (AE, VeloSaaS), Sarah Chen (VP Sales Ops, GMC), Marcus Webb (CFO, GMC), Raj Patel (IT Director, GMC)

JAMES: Thanks everyone for joining. We're excited to finalize the partnership. Sarah, you've been our champion through this process — want to kick us off with where things stand on your side?

SARAH: Absolutely. We've been evaluating CPQ solutions for 8 months now. The 3-week quote cycle is killing us. We had a $450K deal last quarter where the customer went to a competitor because we couldn't turn around a custom quote fast enough. That's the pain point — speed.

MARCUS: From a finance perspective, the ROI model James put together shows a 6-month payback. That's what got my sign-off. But I want to be clear — if we're not seeing measurable improvement by the 6-month mark, the renewal conversation is going to be tough.

SARAH: Agreed. Our target is 48-hour quote turnaround and 80% adoption across the sales team within 60 days of go-live.

RAJ: I need to flag something. The SAP integration is going to be more complex than what's in the current scope. We're running SAP ECC 6.0 with heavy customizations on the SD module. The data mapping alone for product configurations could take 3-4 weeks.

JAMES: That's a great point, Raj. Let me note that we should scope that integration work separately to make sure it's properly resourced.

SARAH: Can we still hit the 90-day go-live?

JAMES: Our typical manufacturing implementation is 90-120 days depending on integration complexity. We'll work with your team to build a realistic timeline once we kick off.

MARCUS: I need the 90-day target. Our board presentation is in June and I committed to showing CPQ ROI by then.

RAJ: I'm supportive but cautious. We've been burned before by vendors who promise 90 days and deliver in 180. I'd rather set realistic expectations upfront.

SARAH: Let's agree on 90 days as the target with a realistic risk assessment from the CSM during kickoff. Sound fair?

ALL: Agreed.

JAMES: Perfect. I'll get the contract over today. Welcome to VeloSaaS.
""",
        webhook_url="https://synapse-graph-generator-uicugotuta-uc.a.run.app/generate",
    ),
    Deal(
        deal_id="OPP-2026-TF002",
        company_name="TechFin Solutions",
        deal_value=850_000,
        stage=DealStage.PROSPECTING,
        products=[
            DealProduct(name="VeloSaaS CPQ", annual_value=850_000),
        ],
        industry="financial-services",
        employee_count=200,
        contacts=[
            Contact(
                name="Lisa Wang",
                title="Head of Operations",
                email="lwang@techfin.com",
                role="champion",
                pain_point="Manual pricing approvals taking 5+ days",
            ),
        ],
        webhook_url="https://synapse-graph-generator-uicugotuta-uc.a.run.app/generate",
    ),
]
