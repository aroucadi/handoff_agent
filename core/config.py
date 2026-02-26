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
    environment: str = field(default_factory=lambda: os.environ.get("ENVIRONMENT", "dev"))

    # Gemini API
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "").replace("\ufeff", "").strip()
    )

    # Gemini Model Strategy
    gen_model: str = "models/gemini-3.1-pro-preview"
    fallback_model: str = "models/gemini-3-flash-preview"
    summary_model: str = "models/gemini-3-flash-preview"
    # Switch to 2.5-flash-native-audio for Hackathon True Multimodal Vision
    live_agent_model: str = "models/gemini-2.5-flash-native-audio-latest"
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 768  # Hackathon/demo standard

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
        default_factory=lambda: os.environ.get("GRAPH_GENERATOR_URL", "http://localhost:8002/generate")
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
