"""Synapse Backend — Configuration.
Delegates to the shared core config.
"""

from core.config import config

# Re-exporting for compatibility with existing imports
Config = type(config)
