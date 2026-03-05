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

CLAWDVIEW_TERMS = [
    "1. MASTER SUBSCRIPTION AGREEMENT",
    "This Master Subscription Agreement ('Agreement') is entered into by and between ClawdView, Inc. ('ClawdView') and the Customer.",
    "",
    "2. PROVISION OF PURCHASED SERVICES",
    "ClawdView will (a) make the Services available to Customer pursuant to this Agreement, and the applicable Order Forms, (b) provide applicable ClawdView standard support.",
    "",
    "3. USE OF SERVICES AND CONTENT",
    "Customer will (a) be responsible for Users' compliance with this Agreement, (b) be responsible for the accuracy, quality and legality of Customer Data.",
    "",
    "4. FEES AND PAYMENT",
    "Customer will pay all fees specified in Order Forms. Except as otherwise specified herein or in an Order Form, (i) fees are based on Services and Content subscriptions purchased and not actual usage."
]


PRODUCT_CLAUSES = {
    "agileplace": [
        "AgilePlace includes enterprise Kanban, team planning, and portfolio rollups.",
        "Customer will designate an Agile Coach and provide 2 hours/week for working sessions during rollout."
    ],
    "portfolios": [
        "Portfolios includes portfolio hierarchy, investment planning, and strategic alignment reporting.",
        "Executive dashboards will be delivered using standard templates unless custom requirements are documented in Exhibit B."
    ],
    "hub": [
        "Hub includes bidirectional integrations and field mapping configuration.",
        "Customer will provide sandbox credentials for connected systems and approve mapping rules prior to production sync."
    ],
    "ppm-pro": [
        "PPM Pro includes project intake, resource planning, and time-phased financials.",
        "Resource planning accuracy depends on timely updates by project managers and functional leads."
    ],
}


def _product_key(name: str) -> str:
    n = (name or "").lower()
    if "agileplace" in n:
        return "agileplace"
    if "portfolios" in n:
        return "portfolios"
    if " hub" in n or n.endswith("hub"):
        return "hub"
    if "ppm" in n:
        return "ppm-pro"
    return "generic"


def _add_title(pdf: FPDF, title: str, subtitle: str | None = None):
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    if subtitle:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, subtitle, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)


def _add_h2(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 7, text=text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _add_paragraph(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, text=text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _add_bullets(pdf: FPDF, bullets: list[str]):
    pdf.set_font("Helvetica", "", 10)
    for b in bullets:
        pdf.multi_cell(0, 5, text=f"• {b}", new_x="LMARGIN", new_y="NEXT")
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
    _add_h2(pdf, "Standard Terms & Conditions")
    pdf.set_font("Helvetica", "", 10)
    for line in CLAWDVIEW_TERMS:
        if line:
            _add_paragraph(pdf, line)
        else:
            pdf.ln(2)

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
