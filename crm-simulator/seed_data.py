"""CRM Simulator — Seed Data.

Comprehensive demo dataset covering all scenarios:
  - New accounts
  - Lost accounts
  - Win back accounts (many deals won, implemented, lost, ongoing)
  - Prospecting / Negotiation
  - Missing contracts
  - Different industries, sizes, products.
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

WEBHOOK_URL = "https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed"

DEMO_DEALS: list[Deal] = [

    # ══════════════════════════════════════════
    # ACCOUNT 1: RetailGiant Corp (Retail — 25,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="IMP-2022-RG01",
        company_name="RetailGiant Corp",
        deal_value=400_000,
        stage=DealStage.IMPLEMENTED,
        products=[DealProduct(name="ClawdView Base", annual_value=400_000)],
        industry="retail",
        employee_count=25000,
        close_date=date(2022, 5, 10),
        contacts=[Contact(name="John Doe", title="VP IT", role="champion")],
        webhook_fired=True,
    ),
    Deal(
        deal_id="LOST-2023-RG02",
        company_name="RetailGiant Corp",
        deal_value=600_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView Analytics", annual_value=600_000)],
        industry="retail",
        employee_count=25000,
        close_date=date(2023, 8, 15),
        risks=[Risk(description="Budget cuts", severity="high", source="Q3 meeting")],
        contacts=[Contact(name="Jane Smith", title="CFO", role="economic_buyer")],
    ),
    Deal(
        deal_id="OPP-2026-RG04",
        company_name="RetailGiant Corp",
        deal_value=2_500_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="ClawdView Enterprise Suite", annual_value=2_000_000),
            DealProduct(name="ClawdView AI Add-on", annual_value=500_000),
        ],
        industry="retail",
        employee_count=25000,
        close_date=date(2026, 6, 30),
        contacts=[
            Contact(name="John Doe", title="VP IT", role="champion", pain_point="System fragmentation"),
            Contact(name="Jane Smith", title="CFO", role="economic_buyer", commitment="Ready to consolidate if ROI is proven"),
        ],
        risks=[Risk(description="High pricing scrutiny", severity="high", source="pricing call")],
        sales_transcript="[JANE SMITH]: We need to consolidate 15 tools into ClawdView to justify this $2.5M spend.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 2: EduTech Global (Education — 450 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-EDU01",
        company_name="EduTech Global",
        deal_value=120_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=120_000)],
        industry="education",
        employee_count=450,
        close_date=date(2026, 9, 15),
        contacts=[
            Contact(name="Alice Warner", title="Director of EdTech", role="champion", pain_point="Scaling curriculum development teams"),
        ],
        sales_transcript="[ALICE WARNER]: We are just starting our search for a better project management tool.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 3: GlobalManufacturing Co. (Manufacturing — 15,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="IMP-2025-GM01",
        company_name="GlobalManufacturing Co.",
        deal_value=350_000,
        stage=DealStage.IMPLEMENTED,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=350_000)],
        industry="manufacturing",
        employee_count=15000,
        close_date=date(2025, 4, 15),
        webhook_fired=True,
        contacts=[
            Contact(name="Sarah Chen", title="VP EPMO", role="champion", pain_point="Engineering backlog visibility remains limited"),
        ],
        risks=[
            Risk(description="Only 60% team adoption after 10 months", severity="high", source="qbr_notes"),
        ],
    ),
    Deal(
        deal_id="OPP-2026-GM02",
        company_name="GlobalManufacturing Co.",
        deal_value=1_200_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=900_000),
            DealProduct(name="ClawdView Hub", annual_value=300_000),
        ],
        close_date=date(2026, 3, 20),
        industry="manufacturing",
        contacts=[
            Contact(name="Sarah Chen", title="VP EPMO", role="champion"),
            Contact(name="Marcus Webb", title="CFO", role="economic_buyer"),
        ],
        sales_transcript="[MARCUS WEBB]: I need ClawdView Portfolios rolled out before the Q3 board meeting.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 4: TechFin Solutions (Financial Services — 800 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="LOST-2024-TF01",
        company_name="TechFin Solutions",
        deal_value=450_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView Portfolios", annual_value=450_000)],
        industry="financial-services",
        employee_count=800,
        close_date=date(2024, 11, 10),
        contacts=[Contact(name="Lisa Wang", title="Head of PMO", role="champion")],
    ),
    Deal(
        deal_id="OPP-2026-TF02",
        company_name="TechFin Solutions",
        deal_value=180_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="ClawdView PPM Pro", annual_value=180_000)],
        industry="financial-services",
        employee_count=800,
        contacts=[Contact(name="Lisa Wang", title="Head of PMO", role="champion")],
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 5: BioSynth Labs (Biotech — 1,200 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="WON-2025-BSL01",
        company_name="BioSynth Labs",
        deal_value=850_000,
        stage=DealStage.CLOSED_WON,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=850_000)],
        industry="biotech",
        employee_count=1200,
        close_date=date(2025, 12, 5),
        contacts=[Contact(name="Dr. Aris Thorne", title="Chief Scientist", role="champion")],
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),
    Deal(
        deal_id="OPP-2026-BSL02",
        company_name="BioSynth Labs",
        deal_value=1_400_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=1_000_000),
            DealProduct(name="ClawdView Hub", annual_value=400_000),
        ],
        industry="biotech",
        employee_count=1200,
        close_date=date(2026, 8, 20),
        contacts=[
            Contact(name="Dr. Aris Thorne", title="Chief Scientist", role="champion"),
            Contact(name="Elena Vance", title="Director of R&D Operations", role="economic_buyer"),
        ],
        sales_transcript="[ELENA VANCE]: We need to map our entire CRISPR pipeline into ClawdView to maintain FDA compliance tracking.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 6: Logistics360 (Global Logistics — 8,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="IMP-2024-L360-01",
        company_name="Logistics360",
        deal_value=1_200_000,
        stage=DealStage.IMPLEMENTED,
        products=[
            DealProduct(name="ClawdView Hub", annual_value=600_000),
            DealProduct(name="ClawdView AgilePlace", annual_value=600_000),
        ],
        industry="logistics",
        employee_count=8000,
        close_date=date(2024, 3, 15),
        contacts=[Contact(name="David Miller", title="Head of Supply Chain", role="champion")],
        webhook_fired=True,
    ),
    Deal(
        deal_id="OPP-2026-L360-02",
        company_name="Logistics360",
        deal_value=2_800_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="ClawdView Enterprise Suite", annual_value=2_800_000),
        ],
        industry="logistics",
        employee_count=8000,
        close_date=date(2026, 11, 1),
        contacts=[
            Contact(name="Victoria Sterling", title="COO", role="economic_buyer"),
            Contact(name="David Miller", title="Head of Supply Chain", role="champion"),
        ],
        risks=[Risk(description="Highly complex ERP integration requirements", severity="critical")],
        sales_transcript="[VICTORIA STERLING]: If ClawdView can't handle real-time fleet synchronization data, this deal is off.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 7: LuxStay Hotels (Hospitality — 12,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="LOST-2023-LUX01",
        company_name="LuxStay Hotels",
        deal_value=300_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=300_000)],
        industry="hospitality",
        employee_count=12000,
        close_date=date(2023, 1, 10),
        contacts=[Contact(name="Mark Branson", title="Regional Director", role="blocker")],
    ),
    Deal(
        deal_id="OPP-2026-LUX02",
        company_name="LuxStay Hotels",
        deal_value=1_500_000,
        stage=DealStage.PROSPECTING,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=1_000_000),
            DealProduct(name="ClawdView Insights", annual_value=500_000),
        ],
        industry="hospitality",
        employee_count=12000,
        contacts=[Contact(name="Sarah Jenkins", title="VP Digital Transformation", role="champion")],
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 8: SecureBank Int (Fintech — 3,500 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="WON-2025-SBI01",
        company_name="SecureBank Int",
        deal_value=2_200_000,
        stage=DealStage.CLOSED_WON,
        products=[
            DealProduct(name="ClawdView Enterprise Suite", annual_value=2_200_000),
        ],
        industry="fintech",
        employee_count=3500,
        close_date=date(2025, 11, 20),
        contacts=[Contact(name="Kevin Hart", title="CISO", role="technical_evaluator")],
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),
    Deal(
        deal_id="OPP-2026-SBI02",
        company_name="SecureBank Int",
        deal_value=600_000,
        stage=DealStage.QUALIFICATION,
        products=[
            DealProduct(name="ClawdView AI Shield", annual_value=600_000),
        ],
        industry="fintech",
        contacts=[Contact(name="Kevin Hart", title="CISO", role="champion")],
        sales_transcript="[KEVIN HART]: We are looking to overlay ClawdView's AI security layer across our entire portfolio management.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 9: OmniRetail (E-commerce — 5,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-OMNI01",
        company_name="OmniRetail",
        deal_value=950_000,
        stage=DealStage.NEGOTIATION,
        products=[
            DealProduct(name="ClawdView Hub", annual_value=450_000),
            DealProduct(name="ClawdView AgilePlace", annual_value=500_000),
        ],
        industry="e-commerce",
        employee_count=5000,
        close_date=date(2026, 12, 1),
        contacts=[Contact(name="Jason Wu", title="Director of Engineering", role="champion")],
        sales_transcript="[JASON WU]: We need ClawdView to bridge the gap between our warehouse automation and our customer-facing web teams.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 10: PrecisionMetal Ltd (Aerospace/Defense — 4,500 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-PM03",
        company_name="PrecisionMetal Ltd",
        deal_value=1_800_000,
        stage=DealStage.NEGOTIATION,
        products=[DealProduct(name="ClawdView Portfolios (GovCloud)", annual_value=1_800_000)],
        industry="aerospace-defense",
        employee_count=4500,
        contacts=[
            Contact(name="Frank Iron", title="VP Engineering", role="champion"),
            Contact(name="Elena Petrova", title="Director of Compliance", role="blocker"),
        ],
        sales_transcript="[ELENA PETROVA]: If your GovCloud tier actually solves the ITAR residency, I need architecture diagrams by Friday.",
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 11: EcoBlue Energy (Energy — 3,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="IMP-2025-EB01",
        company_name="EcoBlue Energy",
        deal_value=420_000,
        stage=DealStage.IMPLEMENTED,
        products=[DealProduct(name="ClawdView PPM Pro", annual_value=420_000)],
        industry="energy",
        close_date=date(2025, 6, 1),
        webhook_fired=True,
    ),
    Deal(
        deal_id="OPP-2026-EB02",
        company_name="EcoBlue Energy",
        deal_value=750_000,
        stage=DealStage.PROSPECTING,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=500_000),
            DealProduct(name="ClawdView Hub", annual_value=250_000),
        ],
        industry="energy",
        contacts=[Contact(name="Alice Green", title="Director of Operations", role="champion")],
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 12: NovaMed Healthcare (Healthcare — 5,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="WON-2026-NM02",
        company_name="NovaMed Healthcare",
        deal_value=900_000,
        stage=DealStage.CLOSED_WON,
        products=[
            DealProduct(name="ClawdView PPM Pro", annual_value=550_000),
            DealProduct(name="ClawdView Hub", annual_value=350_000),
        ],
        industry="healthcare",
        close_date=date(2026, 1, 10),
        contacts=[Contact(name="Karen Wells", title="VP of Research Operations", role="champion")],
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 13: QuantumDynamic (High Tech — 200 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-QD01",
        company_name="QuantumDynamic",
        deal_value=50_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=50_000)],
        industry="tech",
        contacts=[Contact(name="Sam Alt", title="CEO", role="champion")],
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 14: FoodFlow Logistics (Food & Beverage — 6,000 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-FFL01",
        company_name="FoodFlow Logistics",
        deal_value=1_100_000,
        stage=DealStage.PROSPECTING,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=700_000),
            DealProduct(name="ClawdView Hub", annual_value=400_000),
        ],
        industry="logistics",
        contacts=[Contact(name="Maria Garcia", title="Sr. Director of Logistics", role="champion")],
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 15: UrbanConstruct (Construction — 2,500 employees)
    # ══════════════════════════════════════════
    Deal(
        deal_id="OPP-2026-UC01",
        company_name="UrbanConstruct",
        deal_value=350_000,
        stage=DealStage.PROSPECTING,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=350_000)],
        industry="construction",
        contacts=[Contact(name="Bob the Builder", title="Foreman", role="champion")],
    ),
]
