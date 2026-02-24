"""Contract Generator — Synapse Data Enrichment.

Generates realistic markdown contracts for all 20 demo deals and uploads them to GCS.
This ensures that every 'Won' event results in high-density node generation.
"""

import sys
import os
from pathlib import Path

# Add project root to path for core access
# Add crm-simulator to path
crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))

from seed_data import DEMO_DEALS

def generate_contract_text(deal):
    """Generate realistic contract content tailored to the deal's industry and value."""
    
    # Tailor based on industry
    industry_clause = ""
    if deal.industry == "manufacturing":
        industry_clause = "- **GDPR & Sovereignty**: All telemetry data from EU plants must remain within German-hosted Synapse instances."
    elif deal.industry == "healthcare":
        industry_clause = "- **HIPAA Compliance**: Business Associate Agreement (BAA) is signed as Appendix C. Total encryption at rest."
    elif deal.industry == "financial-services":
        industry_clause = "- **Regulatory Audit**: Synapse must provide monthly security posture reports to the Internal Audit team."
    
    modules_text = "\n".join([f"- {p.name} ({p.annual_value:,} USD/year)" for p in deal.products])
    
    contract_content = f"""# Master Service Agreement (MSA) — {deal.company_name}
## ID: {deal.deal_id}

### 1. Contracted Services
The client is hereby licensed to access the following Synapse modules:
{modules_text}

### 2. Service Level Agreement (SLA)
- **Uptime**: 99.95% monthly uptime guarantee.
- **Support**: 24/7 Premium Support Tier.
- **Response Time**: 
    - Critical (P0): 1 hr
    - Standard (P2): 4 hrs

### 3. Financial Terms
- **Total Deal Value**: {deal.deal_value:,} USD
- **Payment Terms**: Net 30, Annual Advance.
- **Price Lock**: 3 years.

### 4. Custom Clauses & Requirements
{industry_clause}
- **Integration**: Required bidirectional sync with client's legacy systems (SAP, Oracle, or proprietary CRM).
- **Go-Live Deadline**: 90 days from signature.

### 5. Signature
- **Hans Schmidt**, CTO (Decision Maker)
- **Sarah Chen**, VP Sales Operations (Champion)
"""
    return contract_content

def main():
    print(f"📦 Generating high-fidelity contracts for {len(DEMO_DEALS)} deals...")
    out_dir = Path("temp_contracts")
    out_dir.mkdir(exist_ok=True)
    
    for deal in DEMO_DEALS:
        content = generate_contract_text(deal)
        file_path = out_dir / f"{deal.deal_id}.pdf" # Naming it .pdf for extractor logic
        
        print(f"   📝 Generating: {file_path}")
        file_path.write_text(content, encoding="utf-8")
        
    print("\n✨ Local contract generation complete! Use gcloud to sync to GCS.")

if __name__ == "__main__":
    main()
