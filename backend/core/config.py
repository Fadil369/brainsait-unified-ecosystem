"""
BrainSAIT Configuration - Utility Components
Following OidTree 5-component pattern
"""

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "BrainSAIT Healthcare Platform"
    app_version: str = "2.2.0"
    debug: bool = False
    
    # Database
    database_path: str = "healthcare_platform.db"
    db_type: str = "sqlite"
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "brainsait_healthcare"
    db_user: str = "brainsait_admin"
    db_pass: str = ""
    
    # Security
    secret_key: str = "your-secret-key-here"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Twilio (if available)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # OpenAI (if available)
    openai_api_key: str = ""
    
    # NPHIES
    nphies_client_id: str = ""
    nphies_client_secret: str = ""
    nphies_base_url: str = "https://nphies.sa"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


def get_settings() -> Settings:
    """Get application settings singleton"""
    return Settings()