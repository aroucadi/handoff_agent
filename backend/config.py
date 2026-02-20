"""Handoff Backend — Configuration Module.

Reads configuration from environment variables.
In production, secrets are pulled from GCP Secret Manager.
"""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # GCP
    project_id: str = field(default_factory=lambda: os.environ.get("PROJECT_ID", "handoff-dev"))
    region: str = field(default_factory=lambda: os.environ.get("REGION", "us-central1"))

    # Gemini API
    gemini_api_key: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))

    # Storage
    skill_graphs_bucket: str = field(
        default_factory=lambda: os.environ.get(
            "SKILL_GRAPHS_BUCKET",
            f"{os.environ.get('PROJECT_ID', 'handoff-dev')}-skill-graphs",
        )
    )
    uploads_bucket: str = field(
        default_factory=lambda: os.environ.get(
            "UPLOADS_BUCKET",
            f"{os.environ.get('PROJECT_ID', 'handoff-dev')}-handoff-uploads",
        )
    )

    # CRM Simulator
    crm_simulator_url: str = field(
        default_factory=lambda: os.environ.get("CRM_SIMULATOR_URL", "http://localhost:8001")
    )

    # Server
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.environ.get("PORT", "8000")))
    environment: str = field(default_factory=lambda: os.environ.get("ENVIRONMENT", "dev"))

    # Gemini Model IDs
    graph_gen_model: str = "gemini-3.1-pro-preview"
    graph_gen_model_tools: str = "gemini-3.1-pro-preview-customtools"
    live_agent_model: str = "gemini-2.5-flash-native-audio-preview"
    embedding_model: str = "gemini-embedding-001"
    summary_model: str = "gemini-3.0-flash"
    embedding_dims: int = 768  # hackathon: 768, production: 3072


config = Config()
