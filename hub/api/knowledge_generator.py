"""
Synapse Hub — Product Knowledge Generator

Uses Gemini to generate markdown knowledge nodes for each product
in a tenant's catalog. The generated nodes are stored in GCS and
indexed in Firestore, making them available to the Synapse agent
via graph traversal.
"""

from __future__ import annotations

import os
import logging
from textwrap import dedent

from google import genai
from google.cloud import storage, firestore
from google.genai.types import GenerateContentConfig

from models import Product

log = logging.getLogger("hub.knowledge")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SKILL_GRAPHS_BUCKET = os.environ.get("SKILL_GRAPHS_BUCKET", "")
MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)
gcs = storage.Client()
db = firestore.Client()


PRODUCT_KNOWLEDGE_PROMPT = dedent("""\
    You are a B2B SaaS product knowledge architect. Generate a comprehensive
    markdown knowledge node for the following product.

    ## Product Information
    - **Name**: {product_name}
    - **Brand**: {brand_name}
    - **Description**: {product_description}

    ## Instructions
    Generate a single markdown file that serves as a knowledge node for this
    product. The file should include:

    1. **YAML Frontmatter** with:
       - `title`: Product name
       - `node_type`: "product"
       - `brand`: Brand name
       - `tags`: Relevant tags as a list

    2. **Overview** section: What the product does, its core value proposition

    3. **Core Capabilities** section: Bullet points of key features

    4. **Typical Buyer Personas** section: Who purchases this product and why

    5. **Implementation Notes** section: Key considerations for deployment

    6. **Integration Points** section: What other systems or products it connects with

    7. **Common Use Cases** section: 2-3 scenarios where this product excels

    8. **Competitive Positioning** section: How to position against alternatives

    Use wikilinks `[[node-id]]` format for cross-references where appropriate.
    Keep the tone professional and factual. This will be used by a customer
    success AI agent to answer questions about the product.

    Generate ONLY the markdown content, nothing else.
""")


async def generate_product_knowledge(
    tenant_id: str,
    brand_name: str,
    product: Product,
) -> int:
    """
    Generate a product knowledge markdown node using Gemini,
    store it in GCS, and index it in Firestore.

    Returns the number of nodes generated (1 per product).
    """
    log.info(f"Generating knowledge for product: {product.name} (tenant: {tenant_id})")

    prompt = PRODUCT_KNOWLEDGE_PROMPT.format(
        product_name=product.name,
        brand_name=brand_name,
        product_description=product.description or "No description provided.",
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=4096,
        ),
    )

    markdown_content = response.text

    # ── Store in GCS ─────────────────────────────────────────────
    if SKILL_GRAPHS_BUCKET:
        bucket = gcs.bucket(SKILL_GRAPHS_BUCKET)
        blob_path = f"product/{product.node_id}.md"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(markdown_content, content_type="text/markdown")
        log.info(f"Stored knowledge node at gs://{SKILL_GRAPHS_BUCKET}/{blob_path}")

    # ── Index in Firestore ───────────────────────────────────────
    # Store metadata so the graph traversal can discover this node
    node_ref = db.collection("skill_graph_nodes").document(product.node_id)
    node_ref.set({
        "node_id": product.node_id,
        "title": product.name,
        "node_type": "product",
        "brand": brand_name,
        "tenant_id": tenant_id,
        "body_preview": markdown_content[:500],
        "gcs_path": f"product/{product.node_id}.md",
        "created_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
    })
    log.info(f"Indexed knowledge node: {product.node_id}")

    return 1  # 1 node per product
