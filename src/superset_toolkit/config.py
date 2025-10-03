"""Configuration management for Superset Toolkit."""

import os
from typing import Optional


class Config:
    """Central configuration for Superset connections and defaults."""
    
    def __init__(
        self,
        superset_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        schema: Optional[str] = None,
        database_name: Optional[str] = None,
    ):
        self.superset_url = superset_url or os.getenv(
            "SUPERSET_URL", "https://your-superset-instance.com"
        )
        self.username = username or os.getenv("SUPERSET_USERNAME")
        self.password = password or os.getenv("SUPERSET_PASSWORD")
        self.schema = schema or os.getenv("SUPERSET_SCHEMA", "reports")
        self.database_name = database_name or os.getenv("SUPERSET_DATABASE_NAME", "Trino")
        
        if not self.username or not self.password:
            raise ValueError(
                "SUPERSET_USERNAME and SUPERSET_PASSWORD must be set via environment "
                "variables or passed to Config constructor"
            )


# Default global config instance - created lazily
default_config = None


def get_default_config() -> Config:
    """Get or create the default configuration."""
    global default_config
    if default_config is None:
        default_config = Config()
    return default_config
