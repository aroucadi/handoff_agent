import requests
import json

url = "https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed"
payload = {
    "deal_id": "OPP-2026-PM005",
    "company_name": "PrecisionMetal Ltd",
    "deal_value": 1200000,
    "industry": "manufacturing",
    "contacts": [{"name": "Sarah Chen", "role": "champion"}],
    "sales_transcript": "PrecisionMetal is looking to migrate their legacy SAP setup to Synapse for faster quoting."
}

print(f"Triggering webhook at {url}...")
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
