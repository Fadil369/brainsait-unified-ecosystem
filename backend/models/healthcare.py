"""
BrainSAIT Healthcare Models - Data Components
Following OidTree 5-component pattern
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class EntityType(str, Enum):
    """Healthcare entity types supported by BrainSAIT platform"""
    PATIENT = "patient"
    PROVIDER = "provider"
    ORGANIZATION = "organization"
    DEVICE = "device"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    RECORD = "record"
    INSURANCE = "insurance"
    APPOINTMENT = "appointment"
    AI_SERVICE = "ai_service"


class AccessLevel(str, Enum):
    """Security access levels for healthcare data"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealthcareRole(str, Enum):
    """Healthcare professional roles in Saudi Arabian healthcare system"""
    PATIENT = "patient"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"
    RESEARCHER = "researcher"
    AI_ANALYST = "ai_analyst"


class HealthcareIdentity(BaseModel):
    """Healthcare identity model with NPHIES compliance and Arabic support"""
    entity_type: EntityType
    user_id: str = Field(..., description="User or entity identifier")
    name: str = Field(..., description="Name in Arabic and English")
    name_ar: Optional[str] = Field(None, description="Arabic name")
    role: HealthcareRole
    access_level: AccessLevel
    national_id: Optional[str] = Field(None, description="Saudi National ID")
    nphies_id: Optional[str] = Field(None, description="NPHIES identifier")
    organization: Optional[str] = Field(None, description="Healthcare organization")
    department: Optional[str] = Field(None, description="Department or specialty")
    expires: datetime = Field(..., description="Expiration datetime")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration for Arabic text handling"""
        populate_by_name = True
        use_enum_values = True


class NPHIESClaim(BaseModel):
    """NPHIES-compliant healthcare claim model"""
    claim_id: str
    patient_nphies_id: str
    provider_nphies_id: str
    claim_type: str
    amount: float
    currency: str = "SAR"
    diagnosis_codes: List[str] = Field(default_factory=list)
    procedure_codes: List[str] = Field(default_factory=list)
    status: str = "submitted"
    submission_date: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class AIAnalysis(BaseModel):
    """AI analysis model for healthcare data processing"""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True