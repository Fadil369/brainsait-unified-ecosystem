"""
BrainSAIT Communication Models - Data Components
Following OidTree 5-component pattern
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class CommunicationType(str, Enum):
    """Communication channel types supported by BrainSAIT platform"""
    SMS = "sms"
    VOICE = "voice"
    VIDEO = "video"
    EMAIL = "email"


class MessagePriority(str, Enum):
    """Message priority levels for healthcare communications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class CommunicationStatus(str, Enum):
    """Communication delivery status tracking"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class Language(str, Enum):
    """Supported languages with Arabic-first approach"""
    ARABIC = "ar"
    ENGLISH = "en"


class SMSRequest(BaseModel):
    """HIPAA-compliant SMS request model with Arabic support"""
    recipient_phone: str = Field(..., description="Recipient phone number in E.164 format")
    message: str = Field(..., min_length=1, max_length=1600, description="SMS message content")
    patient_id: Optional[str] = Field(None, description="Patient identifier for audit trail")
    priority: MessagePriority = MessagePriority.NORMAL
    language: Language = Language.ARABIC
    scheduled_time: Optional[datetime] = Field(None, description="Schedule message for future delivery")
    encrypt_content: bool = Field(True, description="Encrypt message content for HIPAA compliance")
    
    @validator('recipient_phone')
    def validate_phone_number(cls, v):
        """Validate phone number in E.164 format"""
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format (e.g., +966501234567)')
        return v
    
    @validator('message')
    def validate_message_content(cls, v):
        """Check for potential PHI in message content"""
        phi_patterns = [
            r'\b\d{10}\b',  # National ID patterns
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card patterns
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email patterns
        ]
        for pattern in phi_patterns:
            if re.search(pattern, v):
                logger.warning("Potential PHI detected in message content")
        return v

    class Config:
        use_enum_values = True


class VoiceCallRequest(BaseModel):
    """HIPAA-compliant voice call request model"""
    recipient_phone: str = Field(..., description="Recipient phone number in E.164 format")
    message_content: Optional[str] = Field(None, description="Text-to-speech content")
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    callback_url: Optional[str] = Field(None, description="Webhook URL for call status updates")
    priority: MessagePriority = MessagePriority.NORMAL
    language: Language = Language.ARABIC
    max_duration: int = Field(300, description="Maximum call duration in seconds")
    
    @validator('recipient_phone')
    def validate_phone_number(cls, v):
        """Validate phone number in E.164 format"""
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v

    class Config:
        use_enum_values = True


class VideoSessionRequest(BaseModel):
    """HIPAA-compliant video consultation request model"""
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Healthcare provider identifier")
    session_name: str = Field(..., description="Video consultation session name")
    max_participants: int = Field(4, ge=2, le=50, description="Maximum number of participants")
    recording_enabled: bool = Field(False, description="Enable session recording for compliance")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled consultation time")
    duration_minutes: int = Field(60, ge=15, le=480, description="Expected session duration")

    class Config:
        use_enum_values = True


class CommunicationPreferences(BaseModel):
    """Patient communication preferences with Saudi cultural considerations"""
    patient_id: str
    preferred_language: Language = Language.ARABIC
    sms_enabled: bool = True
    voice_enabled: bool = True
    video_enabled: bool = True
    email_enabled: bool = False
    preferred_contact_time_start: str = Field("09:00", description="Preferred contact time start (HH:MM)")
    preferred_contact_time_end: str = Field("18:00", description="Preferred contact time end (HH:MM)")
    timezone: str = Field("Asia/Riyadh", description="Patient timezone")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact number")

    class Config:
        use_enum_values = True


class WorkflowRequest(BaseModel):
    """Healthcare workflow automation request model"""
    workflow_type: str = Field(..., description="Type of workflow (appointment_reminder, clinical_results, emergency_alert)")
    patient_id: str = Field(..., description="Patient identifier")
    template_data: Dict[str, Any] = Field(default_factory=dict, description="Template variables")
    priority: MessagePriority = MessagePriority.NORMAL
    scheduled_time: Optional[datetime] = Field(None, description="Schedule for future execution")
    communication_types: List[CommunicationType] = Field(default_factory=lambda: [CommunicationType.SMS])

    class Config:
        use_enum_values = True


class ConsentRequest(BaseModel):
    """Digital consent management with Saudi legal compliance"""
    patient_id: str
    consent_type: str = Field(..., description="Type of consent (communication, data_sharing, etc.)")
    consent_given: bool
    consent_date: datetime = Field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = Field(None, description="Consent expiration date")
    digital_signature: Optional[str] = Field(None, description="Digital signature hash")
    witness_id: Optional[str] = Field(None, description="Healthcare provider witness ID")

    class Config:
        use_enum_values = True