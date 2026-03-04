"""Contract Generator — Synapse Data Enrichment.

Generates realistic PDF contracts (using FPDF) for all demo deals and saves them in temp_contracts.
Simulates Planview enterprise software agreements (Portfolios, PPM Pro, AgilePlace).
"""

import sys
import os
from pathlib import Path
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

def generate_pdf_contract(deal, out_file):
    """Generate realistic PDF content tailored to the deal using FPDF."""
    
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"ClawdView Enterprise Order Form & MSA", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Customer Details
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Customer Name: {deal.company_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Order Form ID: {deal.deal_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Industry: {deal.industry.upper()} | Employees: {deal.employee_count or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Products
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Licensed Modules (Subscriptions)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    for p in deal.products:
        annual = f"${p.annual_value:,.2f}" if p.annual_value else "TBD"
        pdf.cell(0, 6, f" - {p.name}: {annual} USD/Year", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Total Deal Value: ${deal.deal_value:,.2f} USD", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Standard Terms
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Standard Terms & Conditions", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for line in CLAWDVIEW_TERMS:
        if not line:
            pdf.ln(2)
        else:
            pdf.multi_cell(0, 5, text=line, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    
    # Custom SLAs based on industry
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Custom Data Processing & SLA Addendums", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    
    if deal.industry == "manufacturing":
        pdf.multi_cell(0, 5, text="- GDPR Addendum: All telemetry data from EU plants must remain within isolated Frankfurt environments.", new_x="LMARGIN", new_y="NEXT")
    elif deal.industry == "tech":
        pdf.multi_cell(0, 5, text="- Multi-cloud Residency Addendum: Customer requires parallel persistence across AWS US-East and GCP US-Central.", new_x="LMARGIN", new_y="NEXT")
    elif deal.industry == "financial-services":
        pdf.multi_cell(0, 5, text="- SOC2 & SEC Rule 17a-4 Addendum: ClawdView must provide WORM (Write Once Read Many) storage compliance for all portfolio models.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.multi_cell(0, 5, text="- Standard ClawdView Data Processing Addendum applies.", new_x="LMARGIN", new_y="NEXT")

    if getattr(deal, "sla_days", None):
        pdf.multi_cell(0, 5, text=f"- Implementation SLA: Core systems must be in production within {deal.sla_days} days of signing.", new_x="LMARGIN", new_y="NEXT")
    
    # Required Integration
    pdf.ln(5)
    pdf.multi_cell(0, 5, text="- Integration Scope: Requires deployment of ClawdView Hub for bidirectional flow with existing ERP and Developer tools (Jira/ADO).", new_x="LMARGIN", new_y="NEXT")
    
    # Signatures
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, "ClawdView, Inc. Signature", border="T", align="C")
    pdf.cell(10, 8, "") # Spacer
    pdf.cell(90, 8, f"{deal.company_name} Signature", border="T", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(out_file))

def main():
    print(f"Generating realistic PDF contracts for {len(DEMO_DEALS)} seeded deals...")
    out_dir = Path(__file__).parent.parent / "crm-simulator" / "uploads" / "contracts"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure config and storage are available for upload
    sys.path.append(str(Path(__file__).parent.parent))
    from core.config import config
    from google.cloud import storage
    
    client = storage.Client(project=config.project_id)
    bucket = client.bucket(config.uploads_bucket)
    
    for deal in DEMO_DEALS:
        file_name = f"{deal.deal_id}_contract.pdf"
        file_path = out_dir / file_name
        print(f"   Generating PDF: {file_name}")
        generate_pdf_contract(deal, file_path)
        
        # Upload directly to GCS so it's ready for webhook
        blob = bucket.blob(f"contracts/{file_name}")
        blob.upload_from_filename(str(file_path))
        print(f"   Uploaded to gs://{config.uploads_bucket}/contracts/{file_name}")
        
    print(f"\nSuccessfully generated and uploaded {len(DEMO_DEALS)} PDFs.")

if __name__ == "__main__":
    main()
