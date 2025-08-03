# BrainSAIT Healthcare Platform Configuration
# Centralized configuration management for all services
from typing import List, Optional, Any, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    """
    Comprehensive configuration for BrainSAIT Healthcare Unification Platform
    Supports BOT model deployment across BUILD-OPERATE-TRANSFER phases
    """
    
    # Application
    APP_NAME: str = "BrainSAIT Healthcare Unification Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./healthcare_unified.db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "brainsait_healthcare"
    DB_USER: str = "brainsait_admin"
    DB_PASS: str = "brainsait_healthcare_2025!"
    
    # Redis Configuration
    REDIS_ENABLED: bool = False  # Disable for development
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BCRYPT_ROUNDS: int = 12
    
    # NPHIES Integration
    NPHIES_BASE_URL: str = "https://api.nphies.sa"
    NPHIES_CLIENT_ID: str = "brainsait_client_id"
    NPHIES_CLIENT_SECRET: str = "brainsait_client_secret"
    NPHIES_SCOPE: str = "eligibility preauth claims provider"
    NPHIES_TIMEOUT: int = 30
    
    # Saudi Compliance
    PDPL_COMPLIANCE_ENABLED: bool = True
    SCFHS_INTEGRATION_ENABLED: bool = True
    MOH_REPORTING_ENABLED: bool = True
    SAUDI_DATA_RESIDENCY: bool = True
    
    # AI Services
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL: str = "gpt-4"
    ARABIC_NLP_MODEL_PATH: str = "./models/arabic_medical_nlp"
    FRAUD_DETECTION_THRESHOLD: float = 0.8
    DUPLICATE_DETECTION_THRESHOLD: float = 0.9
    
    # Operations Centers
    OPERATIONS_CENTERS: List[str] = ["riyadh", "jeddah", "dammam"]
    PRIMARY_CENTER: str = "riyadh"
    SHIFT_DURATION_HOURS: int = 8
    REQUIRED_STAFF_PER_SHIFT: int = 50
    
    # Performance Targets (BOT KPIs)
    TARGET_FIRST_PASS_RATE: float = 95.0
    TARGET_DENIAL_RATE: float = 2.0
    TARGET_COLLECTION_DAYS: int = 30
    TARGET_ACCURACY_RATE: float = 98.5
    TARGET_CERTIFICATION_PASS_RATE: float = 85.0
    
    # Training Platform
    TRAINING_PROGRAMS_ENABLED: bool = True
    MAX_STUDENTS_PER_PROGRAM: int = 50
    CERTIFICATION_VALIDITY_YEARS: int = 2
    CONTINUING_EDUCATION_HOURS: int = 40
    
    # BOT Configuration
    BOT_PHASES_ENABLED: bool = True
    BUILD_PHASE_DURATION_MONTHS: int = 12
    OPERATE_PHASE_DURATION_MONTHS: int = 24
    TRANSFER_PHASE_DURATION_MONTHS: int = 12
    KNOWLEDGE_TRANSFER_REQUIRED: bool = True
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MEDICAL_DOCUMENTS_DIR: str = "./medical_docs"
    CERTIFICATES_DIR: str = "./certificates"
    AUDIT_LOGS_DIR: str = "./audit_logs"
    MAX_FILE_SIZE_MB: int = 10
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "notifications@brainsait.com"
    SMTP_PASSWORD: str = "email-password"
    EMAIL_FROM: str = "BrainSAIT Healthcare <notifications@brainsait.com>"
    
    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 60
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:4200",
        "https://healthcare.brainsait.com"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200
    
    # Arabic Language Support
    ARABIC_SUPPORT_ENABLED: bool = True
    RTL_LAYOUT_DEFAULT: bool = True
    ARABIC_FONTS: List[str] = ["Noto Sans Arabic", "Cairo", "Tajawal"]
    
    # Healthcare Standards
    FHIR_VERSION: str = "R4"
    HL7_VERSION: str = "2.8"
    ICD10_VERSION: str = "2023"
    SNOMED_VERSION: str = "International Edition"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Handle comma-separated string format
            if v.startswith('[') and v.endswith(']'):
                # Already in list format string
                return json.loads(v)
            else:
                # Comma-separated format
                return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator('OPERATIONS_CENTERS', mode='before')
    @classmethod
    def validate_operations_centers(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip().lower() for i in v.split(",")]
        return [center.lower() for center in v]
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()