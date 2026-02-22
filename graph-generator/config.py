"""Graph Generator — Configuration."""

import os
from dataclasses import dataclass, field


@dataclass
class GeneratorConfig:
    """Configuration for the Graph Generator service."""

    # GCP
    project_id: str = field(default_factory=lambda: os.environ.get("PROJECT_ID", "handoff-dev"))
    region: str = field(default_factory=lambda: os.environ.get("REGION", "us-central1"))

    # Gemini
    gemini_api_key: str = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY", ""))
    gen_model: str = "gemini-3.1-pro-preview"
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 768
    fallback_model: str = "gemini-3.0-flash"

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

    # Synapse backend URL (for status callbacks)
    backend_url: str = field(
        default_factory=lambda: os.environ.get("BACKEND_URL", "http://localhost:8000")
    )


config = GeneratorConfig()
