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
    # --- ACTIVE PIPELINE: NEGOTIATION ---
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
        employee_count=5000,
        contacts=[
            Contact(name="Sarah Chen", title="VP Sales Operations", role="champion", pain_point="3-week quote cycle costing them deals"),
            Contact(name="Marcus Webb", title="CFO", role="economic_buyer", commitment="6-month payback period"),
            Contact(name="Raj Patel", title="Director of IT", role="technical_evaluator", pain_point="Legacy SAP integration complexity"),
        ],
        risks=[
            Risk(description="90-day go-live SLA is aggressive", severity="high", source="implementation_analysis"),
            Risk(description="Legacy SAP ERP integration not fully scoped", severity="high", source="sales_call_Q4_2025"),
        ],
        success_metrics=[
            SuccessMetric(metric="Quote cycle time", current_value="3 weeks", target_value="48 hours", timeframe="90 days"),
            SuccessMetric(metric="System Availability", current_value="98.5%", target_value="99.99%", timeframe="Year 1"),
        ],
        sales_transcript="""
[MARCUS WEBB - CFO]: 'We need to see a 6-month payback period. Our current manual process is leaking 15% of our top-line revenue due to slow quoting.'
[RAJ PATEL - IT DIR]: 'Technical feasibility hinges on the SAP R/3 (v4.7) integration. We don't have a modern OData layer; you'll need to hit the RFCs directly. Also, data sovereignty is a massive point for our German plants - we need an EU-only storage policy for those regions.'
[SARAH CHEN - VP SALES]: 'The 90-day go-live is non-negotiable. If we miss the Q3 cycle, the project will be shelved until 2027.'
""",
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-CS004",
        company_name="CloudScale AI",
        deal_value=1_500_000,
        stage=DealStage.NEGOTIATION,
        products=[DealProduct(name="Synapse Orchestrator", annual_value=1_500_000)],
        industry="tech",
        close_date=date(2026, 3, 10),
        contacts=[
            Contact(name="David Miller", title="CTO", role="technical_evaluator"),
            Contact(name="Emily Blunt", title="VP Product", role="champion"),
        ],
        risks=[Risk(description="Multi-cloud data residency concerns", severity="medium", source="Discovery Call")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-PM005",
        company_name="PrecisionMetal Ltd",
        deal_value=750_000,
        stage=DealStage.NEGOTIATION,
        products=[DealProduct(name="Revenue Cloud", annual_value=750_000)],
        industry="manufacturing",
        contacts=[
            Contact(name="Frank Iron", title="Head of Supply Chain", role="champion", pain_point="Inventory misalignment with current sales projections"),
            Contact(name="Elena Petrova", title="Director of Compliance", role="technical_evaluator", pain_point="Export control (ITAR) requirements for aerospace components"),
        ],
        risks=[
            Risk(description="Legacy AS400 middleware layer is unstable", severity="high", source="IT Audit 2025"),
            Risk(description="Reliance on single-point-of-failure for VPN connection", severity="medium", source="Discovery Call"),
        ],
        sales_transcript="""
[FRANK IRON]: 'Our supply chain is blind to real-time sales. We're overproducing widgets that aren't selling.'
[ELENA PETROVA]: 'Any solution MUST handle ITAR compliance. If data about our aerospace parts leaves the US-secured zone, we face federal fines. Does Synapse have a data-isolation mode?'
""",
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),

    # --- ACTIVE PIPELINE: QUALIFICATION ---
    Deal(
        deal_id="OPP-2026-TF002",
        company_name="TechFin Solutions",
        deal_value=850_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="VeloSaaS CPQ", annual_value=850_000)],
        industry="financial-services",
        employee_count=200,
        contacts=[Contact(name="Lisa Wang", title="Head of Operations", role="champion", pain_point="Manual pricing approvals")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-RT003",
        company_name="RetailKing Group",
        deal_value=450_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="Revenue Cloud", annual_value=450_000)],
        industry="retail",
        employee_count=12000,
        contacts=[Contact(name="Kevin Hart", title="Chief Digital Officer", role="champion")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-MS006",
        company_name="MayoSystems",
        deal_value=1_200_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="Synapse Health Tier", annual_value=1_200_000)],
        industry="healthcare",
        contacts=[Contact(name="Dr. Jane Smith", title="Medical Director", role="economic_buyer")],
        risks=[Risk(description="HIPAA compliance audit required", severity="high", source="Compliance Team")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-SD007",
        company_name="ShieldDefend",
        deal_value=600_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="Orchestrator Core", annual_value=600_000)],
        industry="cybersecurity",
        contacts=[Contact(name="Bob Security", title="CISO", role="technical_evaluator")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-HA008",
        company_name="HarvestAnalytics",
        deal_value=320_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="Revenue Cloud", annual_value=320_000)],
        industry="agtech",
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),

    # --- ACTIVE PIPELINE: PROSPECTING ---
    Deal(
        deal_id="OPP-2026-VP009",
        company_name="Vanguard Payments",
        deal_value=1_800_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="Synapse Suite", annual_value=1_800_000)],
        industry="financial-services",
        contacts=[Contact(name="Alice Coin", title="Head of Payments", role="champion")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-SS010",
        company_name="ShopSphere Group",
        deal_value=950_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="Orchestrator Core", annual_value=950_000)],
        industry="retail",
        contacts=[Contact(name="Charlie Shop", title="E-commerce Manager", role="champion")],
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-GT011",
        company_name="GlobalTrack Fleet",
        deal_value=480_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="Logistics Cloud", annual_value=480_000)],
        industry="logistics",
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),
    Deal(
        deal_id="OPP-2026-ES012",
        company_name="EduStream University",
        deal_value=250_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="LMS Integration", annual_value=250_000)],
        industry="education",
        webhook_url="https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed",
    ),

    # --- CLOSED WON (Historical Memory) ---
    Deal(
        deal_id="WON-2025-AX001",
        company_name="Acme Corp",
        deal_value=1_250_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="VeloSaaS CPQ", annual_value=1_250_000)],
        industry="manufacturing",
        webhook_fired=True,
        close_date=date(2025, 11, 15),
    ),
    Deal(
        deal_id="WON-2025-UL002",
        company_name="UltraLogistics",
        deal_value=600_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="Revenue Cloud", annual_value=600_000)],
        industry="transportation",
        webhook_fired=True,
        close_date=date(2025, 12, 1),
    ),
    Deal(
        deal_id="WON-2026-BY003",
        company_name="ByteDance Global",
        deal_value=3_400_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="Complete Synapse Suite", annual_value=3_400_000)],
        industry="tech",
        webhook_fired=True,
        close_date=date(2026, 1, 10),
    ),
    Deal(
        deal_id="WON-2026-PH004",
        company_name="PharmaNext Ltd",
        deal_value=900_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="VeloSaaS CPQ", annual_value=900_000)],
        industry="healthcare",
        webhook_fired=True,
        close_date=date(2026, 1, 25),
    ),
    Deal(
        deal_id="WON-2026-EB005",
        company_name="EcoBlue Energy",
        deal_value=550_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="Revenue Cloud", annual_value=550_000)],
        industry="energy",
        webhook_fired=True,
        close_date=date(2026, 2, 5),
    ),

    # --- CLOSED LOST (Historical Context) ---
    Deal(
        deal_id="LOST-2025-SC001",
        company_name="SolarCity Systems",
        deal_value=720_000,
        stage=DealStage.CLOSED_LOST,
        industry="energy",
        close_date=date(2025, 10, 20),
        contacts=[Contact(name="Tom Brady", title="Director of Purchasing", role="economic_buyer")],
        risks=[Risk(description="Lost to competitor (Conga) on pricing", severity="high", source="exit_interview")],
    ),
    Deal(
        deal_id="LOST-2025-NM002",
        company_name="NeoMedics Inc",
        deal_value=1_100_000,
        stage=DealStage.CLOSED_LOST,
        industry="healthcare",
        close_date=date(2025, 12, 10),
        risks=[Risk(description="Budget pull-back in Q4", severity="high", source="internal_memo")],
    ),
    Deal(
        deal_id="LOST-2026-GR003",
        company_name="GreenRoads Freight",
        deal_value=300_000,
        stage=DealStage.CLOSED_LOST,
        industry="logistics",
        close_date=date(2026, 1, 30),
        risks=[Risk(description="Technical mismatch with legacy mainframe", severity="high", source="CTO_review")],
    ),
]
