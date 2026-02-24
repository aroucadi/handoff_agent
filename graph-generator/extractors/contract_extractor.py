"""Graph Generator — Contract PDF Extractor.

Uses Gemini 3.1 Pro multimodal to extract structured contract terms from PDF files
stored in GCS. Returns JSON with contracted modules, SLA terms, pricing,
support tiers, and custom clauses.
"""

from __future__ import annotations

import json

from google import genai
from google.genai.types import GenerateContentConfig, Part
from google.cloud import storage as gcs

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import config
from core.llm import generate_content_with_fallback

CONTRACT_EXTRACTION_PROMPT = """You are an expert at analyzing B2B SaaS contracts and service agreements.

Extract the following information from this contract PDF. Return ONLY valid JSON with this exact structure:

{
  "contracted_modules": [
    {
      "module_name": "Module or product name",
      "license_type": "subscription | perpetual | usage-based",
      "user_count": 100,
      "tier": "enterprise | professional | standard"
    }
  ],
  "sla_terms": {
    "go_live_days": 90,
    "uptime_guarantee": "99.9%",
    "support_hours": "24/7 | business hours",
    "response_time_critical": "1 hour",
    "response_time_standard": "4 hours"
  },
  "pricing": {
    "total_deal_value": "$2,000,000",
    "annual_recurring": "$500,000",
    "payment_terms": "Net 30 | quarterly | annual",
    "discount_applied": "15%",
    "price_lock_years": 3
  },
  "support_tiers": {
    "level": "premium | standard | basic",
    "includes_dedicated_csm": true,
    "training_hours_included": 40,
    "professional_services_days": 20
  },
  "custom_clauses": [
    {
      "clause": "Description of any non-standard term",
      "category": "integration | data | sla | termination | liability",
      "risk_level": "high | medium | low",
      "notes": "Why this matters for implementation"
    }
  ],
  "integration_requirements": [
    {
      "system": "SAP | Salesforce | Oracle | etc.",
      "type": "bidirectional | one-way | read-only",
      "scope": "what data flows between systems",
      "deadline": "when integration must be complete"
    }
  ],
  "key_dates": {
    "contract_signed": "date",
    "start_date": "date",
    "go_live_deadline": "date",
    "first_review_date": "date"
  }
}

IMPORTANT:
- Extract ONLY information explicitly stated in the contract
- Do NOT infer or hallucinate terms not present
- If a field has no data, use null or empty array
- Flag any unusual or non-standard clauses that could impact implementation

CONTRACT PDF:
"""


async def extract_from_contract(client_id: str, contract_pdf_url: str | None = None) -> dict | None:
    """Extract structured contract terms from a PDF using Gemini 3.1 Pro multimodal.

    Downloads the PDF from GCS and sends it to Gemini for multimodal analysis.

    Args:
        client_id: Client identifier (used for GCS path lookup).
        contract_pdf_url: Optional direct GCS URI or path. If None, searches
                          the uploads bucket for the client's contract.

    Returns:
        Dictionary with extracted contract terms, or None if no PDF found.
    """
    pdf_bytes = await _download_contract_pdf(client_id, contract_pdf_url)
    if not pdf_bytes:
        print(f"[CONTRACT] No contract PDF found for {client_id}")
        return None

    print(f"[CONTRACT] Extracting terms from PDF ({len(pdf_bytes)} bytes)...")
    try:
        gen_config = GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=8192,
        )

        # Try to detect if it's actually text (for simulator mocks) or a real PDF
        is_pdf = pdf_bytes[:4] == b"%PDF"
        
        if is_pdf:
            pdf_part = Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        else:
            # Fallback for text-based mocks
            pdf_part = Part.from_text(text=pdf_bytes.decode("utf-8", errors="ignore"))

        contents = [
            pdf_part,
            CONTRACT_EXTRACTION_PROMPT,
        ]
        
        raw_text = await generate_content_with_fallback(
            contents=contents,
            gen_config=gen_config,
            primary_model=config.gen_model,
            fallback_model=config.fallback_model,
        )
        if not raw_text:
            return None
    except Exception as e:
        print(f"[CONTRACT] Extractor failed: {e}")
        return None

    # Parse JSON response
    try:
        extracted = json.loads(raw_text)
    except json.JSONDecodeError:
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0].strip()
            extracted = json.loads(json_str)
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0].strip()
            extracted = json.loads(json_str)
        else:
            print(f"[CONTRACT] Failed to parse extraction response: {raw_text[:300]}")
            return None

    print(f"[CONTRACT] Extracted: {len(extracted.get('contracted_modules', []))} modules, "
          f"{len(extracted.get('custom_clauses', []))} custom clauses")
    return extracted


async def _download_contract_pdf(client_id: str, contract_pdf_url: str | None) -> bytes | None:
    """Download contract PDF from GCS.

    Searches in the uploads bucket under contracts/{client_id}/ or uses
    the provided direct URL.
    """
    gcs_client = gcs.Client(project=config.project_id)
    bucket = gcs_client.bucket(config.uploads_bucket)

    # If a direct URL/path is provided, use it
    if contract_pdf_url:
        # Handle gs:// URIs
        if contract_pdf_url.startswith("gs://"):
            parts = contract_pdf_url.replace("gs://", "").split("/", 1)
            if len(parts) == 2:
                bucket = gcs_client.bucket(parts[0])
                blob = bucket.blob(parts[1])
            else:
                return None
        else:
            # Treat as a relative path within uploads bucket
            blob_path = contract_pdf_url.lstrip("/")
            blob = bucket.blob(blob_path)

        if blob.exists():
            return blob.download_as_bytes()
        return None

    # Search for any PDF under contracts/{client_id}/
    prefix = f"contracts/{client_id}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    pdf_blobs = [b for b in blobs if b.name.endswith(".pdf")]

    if pdf_blobs:
        # Use the most recently uploaded PDF
        pdf_blobs.sort(key=lambda b: b.updated, reverse=True)
        return pdf_blobs[0].download_as_bytes()

    return None
