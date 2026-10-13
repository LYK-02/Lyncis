"""
Lyncis API Configuration
Validated settings loaded from environment or defaults.
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "local"
    ADMIN_TOKEN: str = "lyncis_admin_secret_token"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # DB & Replay paths
    DATABASE_URL: str = "sqlite:///data/lyncis.db"
    SANCTIONS_DB_PATH: str = "data/sanctions/sanctions.db"
    REPLAY_DIR: str = "data/replay"
    DEFAULT_SCENARIO: str = "golden_scenario.jsonl"
    
    # Feature Flags
    FEATURE_AEROTHERMAL: bool = False
    FEATURE_SHADOWTRACE: bool = False
    
    # AISStream Key
    AIS_API_KEY: str = ""
    AIS_BBOX: str = "[[25.0,56.0],[26.5,58.0]]"

    # LLM Settings
    LLM_PROVIDER: str = "none"
    LLM_API_KEY: str = ""
    LLM_TIMEOUT_S: int = 8

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()
