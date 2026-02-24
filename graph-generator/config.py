"""Graph Generator — Configuration.
Delegates to the shared core config.
"""

from core.config import config

# Re-exporting for compatibility with existing imports
GeneratorConfig = type(config)
