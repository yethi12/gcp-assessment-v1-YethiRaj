import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    EXECUTION_MODE: str = "mock"  # "mock" or "gcp"
    GCP_PROJECT_ID: str = "northstar-retail-dev"
    GCP_REGION: str = "asia-south1"
    GCS_LANDING_BUCKET: str = "northstar-retail-landing-zone"
    GCS_PROCESSED_BUCKET: str = "northstar-retail-processed-zone"
    BIGQUERY_DATASET: str = "northstar_retail_mart"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    LOG_LEVEL: str = "INFO"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    RAW_DIR: Path = BASE_DIR / "data" / "raw"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure local directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
settings.RAW_DIR.mkdir(parents=True, exist_ok=True)
