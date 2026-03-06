"""Synapse Core Library — Shared Configuration.

Centralizes configuration logic previously duplicated across the
backend and graph-generator services.
"""

import os
from dataclasses import dataclass, field


@dataclass
class CoreConfig:
    """Unified application configuration."""

    # GCP
    project_id: str = field(default_factory=lambda: os.environ.get("PROJECT_ID", "synapse-488201"))
    region: str = field(default_factory=lambda: os.environ.get("REGION", "us-central1"))
    # Gemini 3.x preview generation models require the global endpoint
    gen_region: str = field(default_factory=lambda: os.environ.get("GEN_REGION", "global"))
    environment: str = field(default_factory=lambda: os.environ.get("ENVIRONMENT", "dev"))

    # Gemini API
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "").replace("\ufeff", "").strip()
    )

    # Gemini Model Strategy — Vertex AI resource names (no "models/" prefix)
    # Queried from: genai.Client(vertexai=True).models.list()
    gen_model: str = "gemini-3.1-flash-lite-preview"
    fallback_model: str = "gemini-2.5-flash"
    summary_model: str = "gemini-3-flash-preview"
    graph_gen_model: str = "gemini-3-flash-preview"  # Used by the text agent in synapse_agent.py
    # Switch to 2.5-flash for Hackathon True Multimodal Vision and Text natively over Vertex AI
    live_agent_model: str = "gemini-live-2.5-flash-native-audio"
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 768  # Hackathon/demo standard

    # Knowledge Center (ClawdView product documentation)
    knowledge_center_url: str = field(
        default_factory=lambda: os.environ.get(
            "KNOWLEDGE_CENTER_URL",
            "http://localhost:8080"   # local dev — gsutil serves on :8080
        )
    )

    # Graph output: "structured" emits entities+edges; "markdown" is legacy 8-node format
    graph_output_format: str = field(
        default_factory=lambda: os.environ.get("GRAPH_OUTPUT_FORMAT", "structured")
    )

    # Storage buckets
    skill_graphs_bucket: str = field(
        default_factory=lambda: os.environ.get(
            "SKILL_GRAPHS_BUCKET",
            f"{os.environ.get('PROJECT_ID', 'synapse-488201')}-synapse-graphs",
        )
    )
    uploads_bucket: str = field(
        default_factory=lambda: os.environ.get(
            "UPLOADS_BUCKET",
            f"{os.environ.get('PROJECT_ID', 'synapse-488201')}-synapse-uploads",
        )
    )

    # Simulator URLs (for local dev callbacks)
    graph_generator_url: str = field(
        default_factory=lambda: os.environ.get("GRAPH_GENERATOR_URL", "http://localhost:8002")
    )
    crm_simulator_url: str = field(
        default_factory=lambda: os.environ.get("CRM_SIMULATOR_URL", "http://localhost:8001")
    )
    backend_url: str = field(
        default_factory=lambda: os.environ.get("BACKEND_URL", "http://localhost:8000")
    )

    # Server Bindings (mainly for backend/main.py and graph-generator/main.py)
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.environ.get("PORT", "8000")))


# Singleton config instance
config = CoreConfig()
