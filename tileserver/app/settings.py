"""settings.

app/settings.py

"""
import os

from pydantic_settings import BaseSettings
from typing import Optional


class CacheSettings(BaseSettings):
    """Cache settings"""

    endpoint: Optional[str] = os.environ.get('CACHE_ENDPOINT', '')
    ttl: int = int(os.environ.get('CACHE_TTL', 3600))
    namespace: str = os.environ.get('CACHE_NAMESPACE', '')

    class Config:
        """model config"""

        env_file = ".env"
        env_prefix = "CACHE_"


cache_setting = CacheSettings()