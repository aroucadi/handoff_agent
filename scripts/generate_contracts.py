"""Contract Generator — Synapse Data Enrichment.

Generates multi-page PDF contracts (using FPDF) for demo deals.
Uploads contracts via the CRM Simulator API so the CRM remains the source of truth
for contract URIs used by the Graph Generator.
"""

import argparse
import sys
from pathlib import Path

import httpx
from fpdf import FPDF

# Add crm-simulator to path to import deals
crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))

from seed_data import DEMO_DEALS

CLAWDVIEW_MSA = [
    ("1. DEFINITIONS", [
        "'Affiliate' means any entity that is controlled by, under common control with, or controls a party.",
        "'Customer Data' means electronic data and information submitted by or for Customer to the Services.",
        "'Services' means the ClawdView products and services ordered by Customer under an Order Form."
    ]),
    ("2. PROVISION OF SERVICES", [
        "ClawdView will (a) make the Services available to Customer pursuant to this Agreement and the applicable Order Forms, (b) provide standard support for the Services at no additional charge, and (c) use commercially reasonable efforts to make the online Services available 24 hours a day, 7 days a week.",
        "The Services are subject to usage limits, including, for example, the quantities specified in Order Forms."
    ]),
    ("3. PROPRIETARY RIGHTS AND LICENSES", [
        "ClawdView reserves all rights, title and interest in and to the Services and Content, including all related intellectual property rights.",
        "Customer grants ClawdView a worldwide, limited-term license to host, copy, transmit and display Customer Data as necessary for ClawdView to provide the Services."
    ]),
    ("4. CONFIDENTIALITY", [
        "'Confidential Information' means all information disclosed by a party to the other party that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information.",
        "The receiving party will use the same degree of care that it uses to protect the confidentiality of its own confidential information (but not less than reasonable care)."
    ]),
    ("5. LIMITATION OF LIABILITY", [
        "IN NO EVENT SHALL THE AGGREGATE LIABILITY OF EACH PARTY ARISING OUT OF OR RELATED TO THIS AGREEMENT EXCEED THE TOTAL AMOUNT PAID BY CUSTOMER HEREUNDER FOR THE SERVICES GIVING RISE TO THE LIABILITY IN THE TWELVE MONTHS PRECEDING THE FIRST INCIDENT OUT OF WHICH THE LIABILITY AROSE."
    ]),
    ("6. TERM AND TERMINATION", [
        "This Agreement commences on the date Customer first accepts it and continues until all subscriptions hereunder have expired or have been terminated.",
        "Either party may terminate this Agreement for cause (i) upon 30 days written notice to the other party of a material breach if such breach remains uncured at the expiration of such period."
    ])
]


PRODUCT_CLAUSES = {
    "agileplace": [
        "AgilePlace Enterprise Subscription includes unlimited Kanban boards, portfolio rollups, and cross-team dependency tracking.",
        "Rollout Support: Customer will designate one (1) 'Agile Champion' per business unit to serve as the primary point of contact for ClawdView's implementation team.",
        "Methodology Alignment: ClawdView provides standard templates for SAFe, Scrum, and Kanban; custom schema modifications are subject to the Professional Services SOW."
    ],
    "portfolios": [
        "Portfolios Strategic Tier includes investment prioritization, capacity planning, and executive 'What-If' scenario modeling.",
        "Data Accuracy: Portfolio health scores depend on the accuracy of underlying project metadata provided from connected systems via ClawdView Hub.",
        "Strategic Alignment: Customer is responsible for defining the 'Strategic Drivers' and 'Themes' used in the prioritization engine."
    ],
    "hub": [
        "ClawdView Hub Enterprise Gateway includes high-concurrency ETL workers and real-time webhook propagation.",
        "Sandbox Access: Customer must provide ClawdView with persistent access to non-production versions of external CRM/ERP systems for mapping verification.",
        "Mapping Governance: Hub mapping rules must be signed off by Customer's Data Architect prior to enabling 'Production Sync' mode."
    ],
    "ppm-pro": [
        "PPM Pro Core includes project intake workflows, resource request management, and time-phased financial planning.",
        "Resource Leveling: Automated resource leveling suggestions are based on 100% allocation defaults unless individual calendars are configured.",
        "Financial Integration: CSV or API-based export of financial actuals follows the ClawdView Standard Financial Schema (v4.2)."
    ],
}


SLA_TIERS = [
    ("Critical", "30 Minutes", "24/7", "Complete loss of service for all users"),
    ("High", "2 Hours", "24/7", "Significant degradation of key product features"),
    ("Medium", "8 Business Hours", "9am-5pm EST", "Minor functional issues / usability requests"),
    ("Low", "24 Business Hours", "9am-5pm EST", "General questions or documentation requests")
]


def _product_key(name: str) -> str:
    n = (name or "").lower()
    if "agileplace" in n:
        return "agileplace"
    if "portfolios" in n:
        return "portfolios"
    if "hub" in n:
        return "hub"
    if "ppm" in n:
        return "ppm-pro"
    return "generic"


def _clean_text(text: str) -> str:
    """Sanitize text for FPDF Helvetica (Latin-1)."""
    if not text:
        return ""
    # Map common problematic characters to Latin-1 compatible ones
    replacements = {
        "\u2022": "-",  # Bullet
        "\u2013": "-",  # En-dash
        "\u2014": "--", # Em-dash
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2026": "...", # Ellipsis
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Encode to latin-1 and ignore what's left to avoid FPDF errors
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def _add_title(pdf: FPDF, title: str, subtitle: str | None = None):
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _clean_text(title), new_x="LMARGIN", new_y="NEXT", align="C")
    if subtitle:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, _clean_text(subtitle), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)


def _add_h2(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 7, text=_clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _add_paragraph(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, text=_clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _add_bullets(pdf: FPDF, bullets: list[str]):
    pdf.set_font("Helvetica", "", 10)
    for b in bullets:
        pdf.multi_cell(0, 5, text=f"- {_clean_text(b)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def generate_pdf_contract(deal, out_file):
    """Generate multi-page PDF contract content tailored to the deal using FPDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    
    pdf.add_page()
    _add_title(pdf, "ClawdView Enterprise Order Form & MSA", subtitle=f"Order Form ID: {deal.deal_id}")
    _add_h2(pdf, "Customer Summary")
    _add_bullets(pdf, [
        f"Customer Name: {deal.company_name}",
        f"Industry: {(deal.industry or 'N/A').upper()}",
        f"Employees: {deal.employee_count or 'N/A'}",
        f"Close Date: {deal.close_date.isoformat() if deal.close_date else 'TBD'}",
    ])

    _add_h2(pdf, "Licensed Modules (Subscriptions)")
    product_lines = []
    for p in deal.products:
        annual = f"${p.annual_value:,.0f}/year" if p.annual_value else "TBD"
        product_lines.append(f"{p.name} — {annual}")
    _add_bullets(pdf, product_lines or ["No products specified"])

    _add_h2(pdf, "Commercials")
    _add_bullets(pdf, [
        f"Total Deal Value: ${deal.deal_value:,.0f} USD",
        f"Contract Term: {getattr(deal, 'contract_length_months', 12) or 12} months",
        f"Implementation SLA: {deal.sla_days} days" if getattr(deal, "sla_days", None) else "Implementation SLA: Standard (as agreed in SOW)",
    ])

    pdf.add_page()
    _add_title(pdf, "Master Subscription Agreement (MSA)")
    _add_h2(pdf, "Confidentiality & Terms")
    for section_title, bullets in CLAWDVIEW_MSA:
        _add_h2(pdf, section_title)
        _add_bullets(pdf, bullets)
        pdf.ln(1)

    pdf.add_page()
    _add_title(pdf, "Exhibit A — Data Processing, Security & SLA Addendums")
    _add_h2(pdf, "Data Processing Addendum")
    industry = (deal.industry or "").lower()
    if industry == "manufacturing":
        _add_bullets(pdf, [
            "Data residency requirements apply for EU subsidiaries as documented by Customer.",
            "Telemetry and audit logs must be retained for 12 months.",
        ])
    elif industry == "tech":
        _add_bullets(pdf, [
            "Customer requires SSO integration (SAML/OIDC) prior to go-live.",
            "Customer requests staging and production environments with separate integration keys.",
        ])
    elif industry == "financial-services":
        _add_bullets(pdf, [
            "Customer requires SOC2-aligned controls for access logging and change management.",
            "Customer may request exportable audit logs for compliance review.",
        ])
    elif industry in ("aerospace-defense", "aerospace", "defense"):
        _add_bullets(pdf, [
            "Customer requires strict access controls and US-only data handling for regulated programs.",
            "Customer requires written approval for any subcontractors accessing Customer data.",
        ])
    elif industry == "healthcare":
        _add_bullets(pdf, [
            "Customer requires secure handling of sensitive operational data and documented incident response process.",
            "Customer may require contractual commitments for data access logging and retention.",
        ])
    elif industry == "biotech":
        _add_bullets(pdf, [
            "Customer requires FDA-compliant data lineage and audit trails for all project metadata.",
            "Adherence to GxP (Good Practice) guidelines for digital systems handling research data.",
        ])
    elif industry == "logistics":
        _add_bullets(pdf, [
            "ClawdView Hub will provide real-time status synchronization hooks for primary logistics hubs.",
            "Customer requires 99.9% availability for the Hub integration layer during peak transit windows.",
        ])
    elif industry == "fintech":
        _add_bullets(pdf, [
            "Customer requires PCI-DSS-compliant data handling for any integrated financial metadata.",
            "Enhanced encryption at rest for all strategic portfolio artifacts.",
        ])
    elif industry == "hospitality":
        _add_bullets(pdf, [
            "Multi-site regional access controls for property-specific project visibility.",
            "Integration with legacy property management systems via ClawdView Hub.",
        ])
    elif industry == "e-commerce":
        _add_bullets(pdf, [
            "Quarterly strategic review of peak-season scalability requirements.",
            "Data residency compliance for international consumer market operations.",
        ])
    elif industry == "construction":
        _add_bullets(pdf, [
            "On-site mobile access optimizations for field-based project team members.",
            "Support for large-scale blueprint and site-survey metadata extraction.",
        ])
    else:
        _add_bullets(pdf, [
            "Standard ClawdView data processing terms apply unless superseded by a separate addendum.",
        ])

    _add_h2(pdf, "Implementation & Support SLA")
    if getattr(deal, "sla_days", None):
        _add_bullets(pdf, [
            f"Implementation SLA: Core systems in production within {deal.sla_days} days of signing.",
            "Weekly implementation checkpoints with Customer stakeholders.",
        ])
    else:
        _add_bullets(pdf, [
            "Implementation SLA: Timelines to be confirmed in a Statement of Work (SOW).",
            "Weekly implementation checkpoints with Customer stakeholders.",
        ])

    pdf.add_page()
    _add_title(pdf, "Exhibit B — Product Scope & Clauses")
    _add_h2(pdf, "Product Scope")
    for p in deal.products:
        key = _product_key(p.name)
        _add_h2(pdf, p.name)
        clauses = PRODUCT_CLAUSES.get(key) or ["Product scope is defined by the purchased subscription tier."]
        _add_bullets(pdf, clauses)
    _add_h2(pdf, "Integration Scope")
    _add_bullets(pdf, [
        "Requires configuration of ClawdView Hub mappings for connected systems.",
        "Customer will provide sandbox access and approve mapping rules prior to production sync.",
        "Any custom integration development must be documented in a separate SOW.",
    ])

    pdf.add_page()
    _add_title(pdf, "Exhibit C — Service Level Agreement (SLA)")
    _add_h2(pdf, "1. Uptime Commitment")
    _add_paragraph(pdf, "ClawdView will use commercially reasonable efforts to make the Services available with a System Availability of at least 99.9% during each calendar month.")
    
    _add_h2(pdf, "2. Support Response Times")
    # Small manual table for SLA
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 7, "Severity", border=1, align="C")
    pdf.cell(40, 7, "Target Response", border=1, align="C")
    pdf.cell(40, 7, "Coverage", border=1, align="C")
    pdf.cell(80, 7, "Description", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 8)
    for sev, resp, cov, desc in SLA_TIERS:
        pdf.cell(30, 7, sev, border=1)
        pdf.cell(40, 7, resp, border=1)
        pdf.cell(40, 7, cov, border=1)
        pdf.multi_cell(80, 7, desc, border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()
    _add_title(pdf, "Exhibit D — Commercial Penalties & Termination")
    _add_h2(pdf, "1. Service Credits")
    _add_paragraph(pdf, "In the event of a failure to meet the 99.9% uptime commitment, Customer will be eligible to receive Service Credits as follow:")
    _add_bullets(pdf, [
        "99.0% - 99.9% uptime: 5% of monthly fees credited",
        "95.0% - 99.0% uptime: 15% of monthly fees credited",
        "Below 95.0% uptime: 25% of monthly fees credited"
    ])
    
    _add_h2(pdf, "2. Late Payments & Penalties")
    _add_bullets(pdf, [
        "Late payments are subject to periodic interest at the rate of 1.5% per month.",
        "Termination by Customer for convenience requires 90-day written notice and payment of 50% of remaining contract value as a liquidation fee.",
        "Data export upon termination: ClawdView will provide a JSON/CSV data export for 30 days following termination; thereafter, data will be purged."
    ])

    pdf.add_page()
    _add_title(pdf, "Execution")
    _add_h2(pdf, "Signatures")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, text="By signing below, the parties agree to the terms of this Order Form and the incorporated MSA.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, "ClawdView, Inc. Signature", border="T", align="C")
    pdf.cell(10, 8, "")
    pdf.cell(90, 8, f"{deal.company_name} Signature", border="T", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(out_file))


def main():
    parser = argparse.ArgumentParser(description="Generate multi-page contracts and upload via CRM API")
    parser.add_argument("--crm_url", default="http://localhost:8001")
    parser.add_argument("--no_upload", action="store_true")
    parser.add_argument("--only", nargs="*", help="Optional deal IDs to generate")
    args = parser.parse_args()

    out_dir = Path(__file__).parent.parent / "crm-simulator" / "uploads" / "contracts"
    out_dir.mkdir(parents=True, exist_ok=True)

    deals = [d for d in DEMO_DEALS if not args.only or d.deal_id in set(args.only)]
    print(f"Generating multi-page PDF contracts for {len(deals)} deals...")

    for deal in deals:
        file_name = f"{deal.deal_id}_contract.pdf"
        file_path = out_dir / file_name
        print(f"   Generating PDF: {file_name}")
        generate_pdf_contract(deal, file_path)

        if args.no_upload:
            continue

        upload_url = f"{args.crm_url.rstrip('/')}/api/deals/{deal.deal_id}/upload-contract"
        try:
            with open(file_path, "rb") as f:
                resp = httpx.post(upload_url, files={"file": (file_name, f, "application/pdf")}, timeout=60.0)
            if resp.status_code >= 400:
                raise RuntimeError(f"{resp.status_code} {resp.text[:200]}")
            body = resp.json()
            print(f"   Uploaded via CRM API: {body.get('gcs_uri')}")
        except Exception as e:
            print(f"   Upload failed: {e}")

    print(f"\nContracts generated in: {out_dir}")

if __name__ == "__main__":
    main()
