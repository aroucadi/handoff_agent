"""CRM Simulator — Seed Data.

Comprehensive demo dataset covering all 4 roles:
  - CSM: closed_won deals awaiting implementation kickoff
  - Sales: prospecting / qualification / negotiation pipeline deals
  - Support: implemented deals with deployed products
  - Strategy: closed_lost deals for win-back analysis

Each deal is fully enriched with contacts, risks, success_metrics, and transcripts.
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
    # ACCOUNT 1: GlobalManufacturing Co.  (Manufacturing — 15,000 employees)
    # Story: Implemented AgilePlace last year → now upgrading to Portfolios & Hub
    # ══════════════════════════════════════════

    # → Support role: live product, support context
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
            Contact(name="Raj Patel", title="Director of IT", role="technical_evaluator", pain_point="AgilePlace → SAP integration fragile under load"),
        ],
        risks=[
            Risk(description="AgilePlace SAP connector hits memory limits during month-end batch sync", severity="medium", source="support_ticket_#4821"),
            Risk(description="Only 60% team adoption after 10 months — training gap", severity="high", source="qbr_notes"),
        ],
        success_metrics=[
            SuccessMetric(metric="Team Adoption Rate", current_value="60%", target_value="90%", timeframe="next QBR"),
            SuccessMetric(metric="Sprint Velocity Visibility", current_value="partial", target_value="full cross-team view", timeframe="30 days"),
        ],
    ),

    # → Sales role: active negotiation
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
        sla_days=90,
        csm_id="csm-alex-demo",
        industry="manufacturing",
        employee_count=15000,
        contacts=[
            Contact(name="Sarah Chen", title="VP EPMO", role="champion", pain_point="Unable to align R&D spending with strategic objectives"),
            Contact(name="Marcus Webb", title="CFO", role="economic_buyer", commitment="Needs portfolio visibility before Q3 board meeting"),
            Contact(name="Raj Patel", title="Director of IT", role="technical_evaluator", pain_point="Requires integration between AgilePlace and legacy SAP ERP"),
        ],
        risks=[
            Risk(description="Aggressive 90-day implementation timeline requested by CFO", severity="high", source="sales_call_Q1_2026"),
            Risk(description="SAP ERP integration via Hub requires custom mappings", severity="high", source="technical_discovery"),
            Risk(description="Competitor ServiceNow pitching their SPM suite at 30% discount", severity="medium", source="champion_intel"),
        ],
        success_metrics=[
            SuccessMetric(metric="Portfolio Visibility", current_value="0%", target_value="100% of R&D tier-1 projects mapped", timeframe="90 days"),
            SuccessMetric(metric="Budget Alignment", current_value="manual quarterly", target_value="real-time portfolio-to-budget linkage", timeframe="6 months"),
        ],
        sales_transcript='''[MARCUS WEBB - CFO]: 'The AgilePlace rollout last year was a hit for the engineering teams, but as CFO, I'm still flying blind on where our R&D dollars are actually going. I need ClawdView Portfolios rolled out before the Q3 board meeting so I can show strategic alignment.'
[RAJ PATEL - IT DIR]: 'To make that work, we need ClawdView Hub to sync financial actuals from our legacy SAP R/3 system into Portfolios. Our SAP instance is heavily customized, so we need assurance the Hub adapters can handle it.'
[SARAH CHEN - VP EPMO]: 'Exactly. If we can get Hub to connect Jira, AgilePlace, and SAP, we finally have a single source of truth.'
''',
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 2: TechFin Solutions  (Financial Services — 800 employees)
    # Story: Lost a deal 2 years ago → now back in qualification → also a new prospecting deal
    # ══════════════════════════════════════════

    # → Strategy role: lost deal analysis
    Deal(
        deal_id="LOST-2024-TF01",
        company_name="TechFin Solutions",
        deal_value=450_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView Portfolios", annual_value=450_000)],
        industry="financial-services",
        employee_count=800,
        close_date=date(2024, 11, 10),
        contacts=[
            Contact(name="Lisa Wang", title="Head of PMO", role="champion", pain_point="Smartsheet breaking under 200+ projects"),
            Contact(name="Derek Cho", title="VP Finance", role="economic_buyer", pain_point="Budget cycle misalignment — needed approval in Q4 but board meets Q1"),
        ],
        risks=[
            Risk(description="Lost to Status Quo (Excel/Smartsheet) due to high initial cost and complexity", severity="high", source="loss_interview"),
            Risk(description="VP Finance did not see ROI within first-year budget cycle", severity="high", source="exec_debrief"),
        ],
        sales_transcript='''[LISA WANG - PMO]: 'I fought hard for this but Derek needed to see first-year ROI and our budget cycle didn't align. We're still drowning in spreadsheets.'
[DEREK CHO - VP FIN]: 'The product looked good but $450K with a 12-month payback didn't fit our Q4 budget constraints. If you could show faster time-to-value with a smaller initial scope, I'd reconsider.'
''',
    ),

    # → Sales role: re-engaged qualification
    Deal(
        deal_id="OPP-2026-TF02",
        company_name="TechFin Solutions",
        deal_value=180_000,
        stage=DealStage.QUALIFICATION,
        products=[DealProduct(name="ClawdView PPM Pro", annual_value=180_000)],
        industry="financial-services",
        employee_count=800,
        contacts=[
            Contact(name="Lisa Wang", title="Head of PMO", role="champion", pain_point="Smartsheet is breaking under the weight of 200+ active projects"),
            Contact(name="Derek Cho", title="VP Finance", role="economic_buyer", commitment="Open to smaller-scope phased approach"),
        ],
        risks=[
            Risk(description="History of abandoning SaaS projects due to perceived complexity", severity="medium", source="historical_sales_notes"),
            Risk(description="Competitor Monday.com already in trial with marketing team", severity="high", source="champion_intel"),
        ],
        success_metrics=[
            SuccessMetric(metric="Project Visibility", current_value="5% (manual reports)", target_value="100% automated dashboard", timeframe="60 days"),
        ],
        sales_transcript='''[LISA WANG]: 'PPM Pro at $180K is much more digestible. If we can show Derek a quick win in 60 days, he'll approve expansion to Portfolios next fiscal year.'
''',
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 3: CloudScale AI  (Tech — 2,200 employees)
    # Story: Clean $1.5M win → awaiting implementation kickoff
    # ══════════════════════════════════════════

    # → CSM role: big won deal needing implementation kickoff
    Deal(
        deal_id="WON-2025-CS01",
        company_name="CloudScale AI",
        deal_value=1_500_000,
        stage=DealStage.CLOSED_WON,
        products=[
            DealProduct(name="ClawdView AgilePlace", annual_value=800_000),
            DealProduct(name="ClawdView Hub", annual_value=700_000),
        ],
        industry="tech",
        employee_count=2200,
        close_date=date(2025, 10, 15),
        sla_days=60,
        csm_id="csm-alex-demo",
        contacts=[
            Contact(name="Priya Sharma", title="CTO", role="executive_sponsor", commitment="Wants company-wide rollout by Q2 2026"),
            Contact(name="James Liu", title="VP Engineering", role="champion", pain_point="12 engineering teams using 5 different tools with zero cross-visibility"),
            Contact(name="Nina Torres", title="Head of Product", role="technical_evaluator", pain_point="Need Hub to unify Jira, GitHub, and linear into single view"),
        ],
        risks=[
            Risk(description="12 independent eng teams — change management is critical", severity="high", source="sales_discovery"),
            Risk(description="CTO expects 60-day go-live which is aggressive for Hub integrations", severity="high", source="executive_commitment"),
            Risk(description="Internal resistance from teams currently using Linear (they love it)", severity="medium", source="champion_intel"),
        ],
        success_metrics=[
            SuccessMetric(metric="Tool Consolidation", current_value="5 tools", target_value="1 unified platform", timeframe="90 days"),
            SuccessMetric(metric="Cross-Team Visibility", current_value="0%", target_value="100% of teams visible in one dashboard", timeframe="60 days"),
            SuccessMetric(metric="Developer Satisfaction", current_value="62% (survey)", target_value="80%+", timeframe="6 months"),
        ],
        sales_transcript='''[PRIYA SHARMA - CTO]: 'We're scaling from 8 to 20 engineering teams this year. The current chaos of Jira, Linear, GitHub Projects, and spreadsheets is unsustainable. I need a single source of truth before we double in size.'
[JAMES LIU - VP ENG]: 'The AgilePlace demo was impressive — the Kanban views and capacity planning will help us a lot. But the real win is Hub connecting everything. If my teams can stay in their tools but I get unified visibility, everyone wins.'
[NINA TORRES - PRODUCT]: 'I need to see the roadmap mapped to engineering execution. Right now I file a request in Productboard and have no idea when my features actually ship.'
''',
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 4: PrecisionMetal Ltd  (Aerospace/Defense — 4,500 employees)
    # Story: Two past losses (ITAR compliance) → now back with GovCloud offer
    # ══════════════════════════════════════════

    # → Strategy role: first loss
    Deal(
        deal_id="LOST-2023-PM01",
        company_name="PrecisionMetal Ltd",
        deal_value=800_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView Portfolios", annual_value=800_000)],
        industry="aerospace-defense",
        employee_count=4500,
        close_date=date(2023, 6, 12),
        contacts=[
            Contact(name="Frank Iron", title="VP Engineering", role="champion", pain_point="No visibility into cross-program dependencies"),
            Contact(name="Elena Petrova", title="Director of Compliance", role="blocker", pain_point="All vendors must pass ITAR + FedRAMP audit"),
        ],
        risks=[
            Risk(description="Failed vendor security review: No FedRAMP authorization at the time", severity="critical", source="ciso_review"),
            Risk(description="Champion (Frank) fully supportive but compliance team has authority to veto", severity="high", source="deal_debrief"),
        ],
        sales_transcript='''[FRANK IRON]: 'I love the product but Elena's compliance team shut it down. No FedRAMP, no deal.'
[ELENA PETROVA]: 'It's not personal. ITAR data residency is federal law. Until ClawdView has a certified US-only environment, I cannot sign off.'
''',
    ),

    # → Strategy role: second loss
    Deal(
        deal_id="LOST-2024-PM02",
        company_name="PrecisionMetal Ltd",
        deal_value=900_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView Portfolios", annual_value=900_000)],
        industry="aerospace-defense",
        employee_count=4500,
        close_date=date(2024, 8, 20),
        contacts=[
            Contact(name="Frank Iron", title="VP Engineering", role="champion"),
            Contact(name="Elena Petrova", title="Director of Compliance", role="blocker"),
        ],
        risks=[
            Risk(description="Failed export control audit (ITAR data residency requirements not met)", severity="critical", source="compliance_blocker"),
            Risk(description="Competitor Broadcom Rally had FedRAMP Moderate — we did not", severity="high", source="competitive_intel"),
        ],
        sales_transcript='''[ELENA PETROVA]: 'You came back with partial FedRAMP Moderate but we need High. ITAR requires FedRAMP High for controlled unclassified information. Broadcom Rally already has that.'
[FRANK IRON]: 'Elena, we're evaluating Rally anyway but their UX is terrible. If ClawdView ever gets GovCloud with FedRAMP High, call me first.'
''',
    ),

    # → Sales role: third attempt with GovCloud
    Deal(
        deal_id="OPP-2026-PM03",
        company_name="PrecisionMetal Ltd",
        deal_value=1_800_000,
        stage=DealStage.NEGOTIATION,
        products=[DealProduct(name="ClawdView Portfolios (GovCloud)", annual_value=1_800_000)],
        industry="aerospace-defense",
        employee_count=4500,
        contacts=[
            Contact(name="Frank Iron", title="VP Engineering", role="champion", pain_point="Running a $4B aerospace program on sticky notes and isolated Jira instances"),
            Contact(name="Elena Petrova", title="Director of Compliance", role="blocker", pain_point="Strict ITAR and FedRAMP High requirements"),
            Contact(name="Col. Davis Mitchell", title="Program Director (F-35)", role="end_user", pain_point="Needs cross-program dependency tracking for defense contracts"),
        ],
        risks=[
            Risk(description="Must prove GovCloud environment meets all ITAR requirements before signature", severity="high", source="legal_review"),
            Risk(description="Competitor Broadcom Rally still entrenched with 2-year contract, ends Q4 2026", severity="medium", source="champion_intel"),
        ],
        success_metrics=[
            SuccessMetric(metric="ITAR Compliance", current_value="pending audit", target_value="FedRAMP High certified", timeframe="before signature"),
            SuccessMetric(metric="Program Visibility", current_value="0%", target_value="full cross-program dependency view", timeframe="120 days"),
        ],
        sales_transcript='''[FRANK IRON - VP ENG]: 'Look, we desperately need Portfolios. Running a $4B aerospace program on sticky notes and isolated Jira instances is killing us.'
[ELENA PETROVA - COMPLIANCE]: 'Frank, you know the drill. Last two times we tried to buy ClawdView, they failed our ITAR data residency checks. Our defense data cannot leave US soil and cannot be accessed by non-US persons. If your new GovCloud tier actually solves this, I need the architecture diagrams and third-party audit reports sent to my team by Friday.'
[COL. MITCHELL]: 'If this passes Elena's review, I have budget authority for the F-35 program. We need this yesterday.'
''',
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 5: EcoBlue Energy  (Energy & Utilities — 3,000 employees)
    # Story: Won deal → implemented → now a new expansion prospecting deal
    # ══════════════════════════════════════════

    # → Support role: deployed product
    Deal(
        deal_id="IMP-2025-EB01",
        company_name="EcoBlue Energy",
        deal_value=420_000,
        stage=DealStage.IMPLEMENTED,
        products=[
            DealProduct(name="ClawdView PPM Pro", annual_value=420_000),
        ],
        industry="energy",
        employee_count=3000,
        close_date=date(2025, 6, 1),
        webhook_fired=True,
        contacts=[
            Contact(name="Alice Green", title="Director of Operations", role="champion", pain_point="Capital project tracking across 15 solar farms"),
            Contact(name="Tom Reeves", title="IT Manager", role="technical_evaluator", pain_point="SSO integration with Azure AD was tricky"),
        ],
        risks=[
            Risk(description="Azure AD SSO occasionally drops sessions during token refresh", severity="medium", source="support_ticket_#7102"),
            Risk(description="Custom report builder used by only 2 people — training gap for other PMs", severity="low", source="usage_analytics"),
        ],
        success_metrics=[
            SuccessMetric(metric="Capital Project Visibility", current_value="100%", target_value="100%", timeframe="met"),
            SuccessMetric(metric="Reporting Efficiency", current_value="2 hours/week", target_value="30 min/week", timeframe="in progress"),
        ],
    ),

    # → Sales role: expansion opportunity
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
        employee_count=3000,
        contacts=[
            Contact(name="Alice Green", title="Director of Operations", role="champion", commitment="Loved PPM Pro, wants to expand to Portfolios for enterprise view"),
            Contact(name="David Park", title="CFO", role="economic_buyer", pain_point="Needs portfolio-level view of $2B infrastructure pipeline"),
        ],
        risks=[
            Risk(description="CFO is cost-sensitive — $750K is 3x their current spend", severity="medium", source="champion_intel"),
        ],
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 6: NovaMed Healthcare  (Healthcare — 5,000 employees)
    # Story: Won deal (CSM kickoff needed) + a previous loss in a different division
    # ══════════════════════════════════════════

    # → Strategy role: lost deal
    Deal(
        deal_id="LOST-2025-NM01",
        company_name="NovaMed Healthcare",
        deal_value=600_000,
        stage=DealStage.CLOSED_LOST,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=600_000)],
        industry="healthcare",
        employee_count=5000,
        close_date=date(2025, 3, 20),
        contacts=[
            Contact(name="Dr. Aisha Okafor", title="Chief Digital Officer", role="champion", pain_point="Clinical IT team using Trello/SharePoint — no governance"),
            Contact(name="Robert Kim", title="CISO", role="blocker", pain_point="HIPAA BAA requirements for any SaaS handling clinical project data"),
        ],
        risks=[
            Risk(description="CISO blocked deal: ClawdView could not sign HIPAA BAA within evaluation window", severity="critical", source="legal_debrief"),
            Risk(description="Champion frustrated — wants to try again when BAA is available", severity="medium", source="relationship_notes"),
        ],
        sales_transcript='''[DR. OKAFOR]: 'Our clinical IT transformation projects are managed in Trello boards and SharePoint lists. It's embarrassing for a $5B healthcare system. I need AgilePlace.'
[ROBERT KIM - CISO]: 'Aisha, I support this, but any tool touching clinical project metadata needs a signed HIPAA Business Associate Agreement. ClawdView's legal team said BAA execution takes 6 months. We can't wait that long in this eval cycle.'
''',
    ),

    # → CSM role: won deal for a different division
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
        employee_count=5000,
        close_date=date(2026, 1, 10),
        sla_days=45,
        csm_id="csm-alex-demo",
        contacts=[
            Contact(name="Karen Wells", title="VP of Research Operations", role="champion", pain_point="Clinical trial portfolio tracking is completely manual"),
            Contact(name="Dr. Aisha Okafor", title="Chief Digital Officer", role="executive_sponsor", commitment="Authorized non-clinical division rollout to avoid HIPAA scope"),
            Contact(name="Mike Chen", title="IT Director (Research)", role="technical_evaluator", pain_point="Need Hub to connect with REDCap and Veeva"),
        ],
        risks=[
            Risk(description="HIPAA scope creep — research team occasionally handles PHI-adjacent data", severity="high", source="compliance_review"),
            Risk(description="45-day SLA is tight for Hub integrations with REDCap and Veeva", severity="high", source="csm_planning"),
            Risk(description="Previous loss in clinical IT division may create political friction", severity="medium", source="account_history"),
        ],
        success_metrics=[
            SuccessMetric(metric="Trial Portfolio Visibility", current_value="0%", target_value="100% of active trials tracked", timeframe="45 days"),
            SuccessMetric(metric="Grant Utilization", current_value="manual tracking", target_value="automated dashboard", timeframe="90 days"),
            SuccessMetric(metric="Research Tool Consolidation", current_value="4 tools", target_value="1 platform via Hub", timeframe="6 months"),
        ],
        sales_transcript='''[KAREN WELLS]: 'We run 200+ active clinical trials and track them in a monster Excel file. If a PI misses a grant deadline because of our tracking failures, it's millions in lost funding.'
[DR. OKAFOR]: 'After the BAA issue killed the clinical IT deal, I redirected to Research Operations where HIPAA scope is smaller. Karen's team needs this desperately and I can authorize it without Robert's blockers.'
[MIKE CHEN]: 'Hub needs to pull from REDCap for trial data and Veeva for regulatory submissions. If those connectors work, this is a game-changer.'
''',
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),

    # ══════════════════════════════════════════
    # ACCOUNT 7: UrbanLogix  (Logistics/Supply Chain — 1,200 employees)
    # Story: Fully implemented success story + new expansion won deal
    # ══════════════════════════════════════════

    # → Support role: mature implementation
    Deal(
        deal_id="IMP-2024-UL01",
        company_name="UrbanLogix",
        deal_value=280_000,
        stage=DealStage.IMPLEMENTED,
        products=[DealProduct(name="ClawdView AgilePlace", annual_value=280_000)],
        industry="logistics",
        employee_count=1200,
        close_date=date(2024, 3, 1),
        webhook_fired=True,
        contacts=[
            Contact(name="Carlos Mendez", title="Head of Engineering", role="champion", pain_point="Cross-team dependency tracking between warehouse and routing teams"),
            Contact(name="Amy Park", title="Scrum Master Lead", role="end_user", notes="Power user, runs training for new hires"),
        ],
        risks=[
            Risk(description="API rate limits hit during peak holiday season (Black Friday surge)", severity="medium", source="support_ticket_#3401"),
            Risk(description="Custom workflow automations fragile — built by a contractor who left", severity="high", source="support_escalation"),
        ],
        success_metrics=[
            SuccessMetric(metric="Team Adoption", current_value="95%", target_value="95%", timeframe="met"),
            SuccessMetric(metric="Sprint Predictability", current_value="78%", target_value="85%", timeframe="ongoing"),
        ],
    ),

    # → CSM role: expansion won deal
    Deal(
        deal_id="WON-2026-UL02",
        company_name="UrbanLogix",
        deal_value=520_000,
        stage=DealStage.CLOSED_WON,
        products=[
            DealProduct(name="ClawdView Portfolios", annual_value=320_000),
            DealProduct(name="ClawdView Hub", annual_value=200_000),
        ],
        industry="logistics",
        employee_count=1200,
        close_date=date(2026, 2, 1),
        sla_days=75,
        csm_id="csm-alex-demo",
        contacts=[
            Contact(name="Carlos Mendez", title="Head of Engineering", role="champion", commitment="Wants Portfolios to give C-suite visibility into tech investments"),
            Contact(name="Sandra Wright", title="COO", role="executive_sponsor", pain_point="Cannot see total IT spend across 8 product lines"),
            Contact(name="Amy Park", title="Scrum Master Lead", role="end_user", pain_point="Needs Hub to connect AgilePlace with their Notion docs and Slack"),
        ],
        risks=[
            Risk(description="COO expects executive dashboard within 30 days — before board meeting", severity="high", source="sales_handoff"),
            Risk(description="Notion and Slack Hub connectors are in beta — may hit stability issues", severity="medium", source="product_team_advisory"),
        ],
        success_metrics=[
            SuccessMetric(metric="Executive Dashboard", current_value="none", target_value="real-time Portfolios view for C-suite", timeframe="30 days"),
            SuccessMetric(metric="IT Spend Visibility", current_value="quarterly manual", target_value="automated monthly via Hub integrations", timeframe="75 days"),
        ],
        sales_transcript='''[SANDRA WRIGHT - COO]: 'Carlos's AgilePlace rollout was the most successful tech deployment we've had. But I still can't see the forest for the trees — I need Portfolios to show the board where our tech dollars go.'
[CARLOS MENDEZ]: 'Portfolios and Hub are the logical next step. Our AgilePlace data is clean, so the foundation is solid. Just make sure Hub's Notion connector actually works — our PMs live in Notion.'
''',
        webhook_fired=True,
        webhook_url=WEBHOOK_URL,
    ),
]
