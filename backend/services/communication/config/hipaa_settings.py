"""
BrainSAIT Healthcare Platform - HIPAA Configuration Settings
Comprehensive HIPAA compliance configuration for Twilio communications
Supports Saudi Arabia healthcare regulations and PDPL compliance
"""

import os
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from enum import Enum
import json


class LogLevel(str, Enum):
    """Audit logging levels for HIPAA compliance"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class EncryptionStandard(str, Enum):
    """HIPAA-approved encryption standards"""
    AES_256_GCM = "AES-256-GCM"
    RSA_4096 = "RSA-4096"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"


class PHIClassification(str, Enum):
    """PHI data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class CommunicationChannel(str, Enum):
    """Supported HIPAA-compliant communication channels"""
    SMS = "sms"
    VOICE = "voice"
    EMAIL = "email"
    SECURE_MESSAGING = "secure_messaging"
    VIDEO = "video"


class HIPAASettings(BaseSettings):
    """
    HIPAA compliance configuration for BrainSAIT healthcare communications
    Designed for Saudi Arabia healthcare environment with Arabic support
    """
    
    # === TWILIO CONFIGURATION ===
    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio Auth Token")
    TWILIO_WORKSPACE_SID: str = Field(..., description="Twilio Workspace SID for TaskRouter")
    
    # HIPAA-compliant Twilio phone numbers
    TWILIO_PHONE_NUMBER: str = Field(..., description="Primary Twilio phone number")
    TWILIO_VOICE_NUMBER: str = Field(..., description="Voice-specific Twilio number")
    TWILIO_SMS_NUMBER: str = Field(..., description="SMS-specific Twilio number")
    
    # Twilio API configuration
    TWILIO_API_VERSION: str = Field(default="2010-04-01", description="Twilio API version")
    TWILIO_TIMEOUT: int = Field(default=30, description="Twilio API timeout in seconds")
    TWILIO_RETRY_ATTEMPTS: int = Field(default=3, description="Number of retry attempts")
    
    # Twilio Video API configuration
    TWILIO_API_KEY: str = Field(default="", description="Twilio API Key for Video")
    TWILIO_API_SECRET: str = Field(default="", description="Twilio API Secret for Video")
    
    # === HIPAA COMPLIANCE ===
    
    # Business Associate Agreement (BAA) settings
    BAA_SIGNED: bool = Field(default=False, description="BAA agreement status with Twilio")
    BAA_EFFECTIVE_DATE: Optional[str] = Field(default=None, description="BAA effective date")
    BAA_EXPIRY_DATE: Optional[str] = Field(default=None, description="BAA expiry date")
    BAA_DOCUMENT_PATH: Optional[str] = Field(default=None, description="Path to BAA document")
    
    # Encryption requirements
    ENCRYPTION_AT_REST: EncryptionStandard = Field(
        default=EncryptionStandard.AES_256_GCM,
        description="Encryption standard for data at rest"
    )
    ENCRYPTION_IN_TRANSIT: EncryptionStandard = Field(
        default=EncryptionStandard.AES_256_GCM,
        description="Encryption standard for data in transit"
    )
    
    # Data retention policies
    MESSAGE_RETENTION_DAYS: int = Field(default=2555, description="7 years in days")  # HIPAA requirement
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=2555, description="Audit log retention")
    VOICE_RECORDING_RETENTION_DAYS: int = Field(default=2555, description="Voice recording retention")
    
    # Access controls
    REQUIRE_TWO_FACTOR_AUTH: bool = Field(default=True, description="Require 2FA for access")
    SESSION_TIMEOUT_MINUTES: int = Field(default=15, description="Session timeout in minutes")
    MAX_LOGIN_ATTEMPTS: int = Field(default=3, description="Maximum login attempts")
    
    # === PHI DETECTION AND CLASSIFICATION ===
    
    # PHI detection patterns (Saudi-specific)
    PHI_PATTERNS: Dict[str, List[str]] = Field(
        default={
            "saudi_national_id": [r"\b\d{10}\b", r"\b\d{4}-\d{4}-\d{2}\b"],
            "saudi_iqama": [r"\b[12]\d{9}\b"],
            "phone_saudi": [r"\+966[0-9]{8,9}", r"05[0-9]{8}"],
            "medical_record": [r"MR[N]?\d{6,10}", r"MRN-\d{6,10}"],
            "insurance_id": [r"INS-\d{8,12}", r"NPHIES-\d{10}"],
            "email": [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"],
            "arabic_name": [r"[\u0600-\u06FF\s]{3,}"]
        }
    )
    
    # Content classification thresholds
    PHI_DETECTION_THRESHOLD: float = Field(default=0.8, description="PHI detection confidence threshold")
    AUTO_REDACT_ENABLED: bool = Field(default=True, description="Auto-redact detected PHI")
    MANUAL_REVIEW_REQUIRED: bool = Field(default=True, description="Require manual review for PHI")
    
    # === AUDIT AND LOGGING ===
    
    # Audit logging configuration
    AUDIT_LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Audit logging level")
    AUDIT_LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Audit log format"
    )
    AUDIT_LOG_PATH: str = Field(default="./logs/hipaa_audit.log", description="Audit log file path")
    
    # Required audit events
    AUDIT_EVENTS: Set[str] = Field(
        default={
            "phi_access", "phi_modification", "phi_deletion", "phi_export",
            "message_sent", "message_received", "voice_call_initiated", 
            "voice_call_completed", "authentication_attempt", "authorization_granted",
            "encryption_event", "decryption_event", "baa_verification",
            "compliance_violation", "data_breach_detected"
        }
    )
    
    # === SAUDI ARABIA SPECIFIC ===
    
    # PDPL (Personal Data Protection Law) compliance
    PDPL_COMPLIANCE_ENABLED: bool = Field(default=True, description="Enable PDPL compliance")
    DATA_RESIDENCY_SAUDI: bool = Field(default=True, description="Keep data within Saudi Arabia")
    CROSS_BORDER_TRANSFER_ALLOWED: bool = Field(default=False, description="Allow cross-border data transfer")
    
    # Arabic language support
    ARABIC_SUPPORT_ENABLED: bool = Field(default=True, description="Enable Arabic text support")
    RTL_SUPPORT_ENABLED: bool = Field(default=True, description="Enable RTL text support")
    ARABIC_TRANSLITERATION: bool = Field(default=True, description="Enable Arabic transliteration")
    
    # Healthcare authority integration
    MOH_INTEGRATION_ENABLED: bool = Field(default=True, description="Enable MOH integration")
    SCFHS_REPORTING_ENABLED: bool = Field(default=True, description="Enable SCFHS reporting")
    NPHIES_COMPLIANCE_MODE: bool = Field(default=True, description="Enable NPHIES compliance mode")
    
    # === COMMUNICATION CHANNELS ===
    
    # Channel-specific settings
    ENABLED_CHANNELS: List[CommunicationChannel] = Field(
        default=[
            CommunicationChannel.SMS,
            CommunicationChannel.VOICE,
            CommunicationChannel.SECURE_MESSAGING,
            CommunicationChannel.VIDEO
        ]
    )
    
    # SMS configuration
    SMS_CHARACTER_LIMIT: int = Field(default=160, description="SMS character limit")
    SMS_MULTIPART_ENABLED: bool = Field(default=True, description="Enable multipart SMS")
    SMS_DELIVERY_REPORTS: bool = Field(default=True, description="Request SMS delivery reports")
    SMS_PHI_ALLOWED: bool = Field(default=False, description="Allow PHI in SMS")
    
    # Voice configuration
    VOICE_RECORDING_ENABLED: bool = Field(default=True, description="Enable voice recording")
    VOICE_TRANSCRIPTION_ENABLED: bool = Field(default=True, description="Enable voice transcription")
    VOICE_QUALITY_MONITORING: bool = Field(default=True, description="Enable voice quality monitoring")
    VOICE_PHI_DETECTION: bool = Field(default=True, description="Enable PHI detection in voice")
    
    # Video configuration
    VIDEO_ENABLED: bool = Field(default=True, description="Enable video consultations")
    VIDEO_RECORDING_ENABLED: bool = Field(default=True, description="Enable video recording")
    VIDEO_AUTO_RECORD: bool = Field(default=True, description="Auto-start recording for video sessions")
    VIDEO_MAX_PARTICIPANTS: int = Field(default=10, description="Maximum participants per video session")
    VIDEO_SESSION_TIMEOUT_HOURS: int = Field(default=2, description="Video session timeout in hours")
    VIDEO_QUALITY_DEFAULT: str = Field(default="standard", description="Default video quality setting")
    VIDEO_ENCRYPTION_REQUIRED: bool = Field(default=True, description="Require video encryption")
    VIDEO_WAITING_ROOM_ENABLED: bool = Field(default=True, description="Enable waiting room for video calls")
    VIDEO_SCREEN_SHARING_ENABLED: bool = Field(default=True, description="Enable screen sharing")
    VIDEO_CHAT_ENABLED: bool = Field(default=True, description="Enable chat during video calls")
    VIDEO_PHI_DETECTION: bool = Field(default=True, description="Enable PHI detection in video chat")
    VIDEO_RECORDING_RETENTION_DAYS: int = Field(default=2555, description="Video recording retention in days")  # 7 years
    
    # === SECURITY CONTROLS ===
    
    # Access control matrix
    ROLE_PERMISSIONS: Dict[str, List[str]] = Field(
        default={
            "patient": ["view_own_messages", "send_secure_message"],
            "nurse": ["view_patient_messages", "send_patient_message", "view_medical_alerts"],
            "doctor": ["view_all_patient_data", "send_medical_communications", "access_phi"],
            "admin": ["manage_users", "audit_access", "configure_system"],
            "compliance_officer": ["audit_all_activities", "generate_reports", "manage_policies"]
        }
    )
    
    # Rate limiting for security
    RATE_LIMIT_PER_USER_MINUTE: int = Field(default=10, description="Rate limit per user per minute")
    RATE_LIMIT_PER_IP_MINUTE: int = Field(default=100, description="Rate limit per IP per minute")
    RATE_LIMIT_BURST_SIZE: int = Field(default=20, description="Rate limit burst size")
    
    # === MONITORING AND ALERTING ===
    
    # Health monitoring
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    PERFORMANCE_MONITORING: bool = Field(default=True, description="Enable performance monitoring")
    SECURITY_MONITORING: bool = Field(default=True, description="Enable security monitoring")
    
    # Alert thresholds
    ALERT_ON_PHI_DETECTION: bool = Field(default=True, description="Alert on PHI detection")
    ALERT_ON_FAILED_AUTH: bool = Field(default=True, description="Alert on failed authentication")
    ALERT_ON_UNUSUAL_ACTIVITY: bool = Field(default=True, description="Alert on unusual activity")
    
    # Notification settings
    SECURITY_ALERT_EMAIL: str = Field(default="security@brainsait.com", description="Security alert email")
    COMPLIANCE_ALERT_EMAIL: str = Field(default="compliance@brainsait.com", description="Compliance alert email")
    TECHNICAL_ALERT_EMAIL: str = Field(default="ops@brainsait.com", description="Technical alert email")
    
    @validator('BAA_SIGNED')
    def validate_baa_requirement(cls, v):
        """Ensure BAA is signed for HIPAA compliance"""
        if not v:
            raise ValueError("Business Associate Agreement (BAA) must be signed for HIPAA compliance")
        return v
    
    @validator('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')
    def validate_twilio_credentials(cls, v):
        """Validate Twilio credentials format"""
        if not v or len(v) < 30:
            raise ValueError("Twilio credentials must be properly configured")
        return v
    
    @validator('PHI_DETECTION_THRESHOLD')
    def validate_phi_threshold(cls, v):
        """Validate PHI detection threshold"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("PHI detection threshold must be between 0.0 and 1.0")
        return v
    
    @validator('ENABLED_CHANNELS')
    def validate_channels(cls, v):
        """Ensure at least one communication channel is enabled"""
        if not v:
            raise ValueError("At least one communication channel must be enabled")
        return v
    
    def get_channel_config(self, channel: CommunicationChannel) -> Dict:
        """Get configuration for a specific communication channel"""
        base_config = {
            "enabled": channel in self.ENABLED_CHANNELS,
            "encryption": self.ENCRYPTION_IN_TRANSIT.value,
            "audit_required": True,
            "phi_detection": True
        }
        
        if channel == CommunicationChannel.SMS:
            base_config.update({
                "character_limit": self.SMS_CHARACTER_LIMIT,
                "multipart_enabled": self.SMS_MULTIPART_ENABLED,
                "delivery_reports": self.SMS_DELIVERY_REPORTS,
                "phi_allowed": self.SMS_PHI_ALLOWED
            })
        elif channel == CommunicationChannel.VOICE:
            base_config.update({
                "recording_enabled": self.VOICE_RECORDING_ENABLED,
                "transcription_enabled": self.VOICE_TRANSCRIPTION_ENABLED,
                "quality_monitoring": self.VOICE_QUALITY_MONITORING,
                "phi_detection": self.VOICE_PHI_DETECTION
            })
        elif channel == CommunicationChannel.VIDEO:
            base_config.update({
                "recording_enabled": self.VIDEO_RECORDING_ENABLED,
                "auto_record": self.VIDEO_AUTO_RECORD,
                "max_participants": self.VIDEO_MAX_PARTICIPANTS,
                "session_timeout_hours": self.VIDEO_SESSION_TIMEOUT_HOURS,
                "default_quality": self.VIDEO_QUALITY_DEFAULT,
                "encryption_required": self.VIDEO_ENCRYPTION_REQUIRED,
                "waiting_room_enabled": self.VIDEO_WAITING_ROOM_ENABLED,
                "screen_sharing_enabled": self.VIDEO_SCREEN_SHARING_ENABLED,
                "chat_enabled": self.VIDEO_CHAT_ENABLED,
                "phi_detection": self.VIDEO_PHI_DETECTION,
                "recording_retention_days": self.VIDEO_RECORDING_RETENTION_DAYS
            })
        
        return base_config
    
    def is_baa_valid(self) -> bool:
        """Check if BAA is currently valid"""
        if not self.BAA_SIGNED:
            return False
        
        if self.BAA_EXPIRY_DATE:
            from datetime import datetime
            try:
                expiry = datetime.fromisoformat(self.BAA_EXPIRY_DATE)
                return datetime.now() < expiry
            except ValueError:
                return False
        
        return True
    
    def get_saudi_compliance_config(self) -> Dict:
        """Get Saudi Arabia specific compliance configuration"""
        return {
            "pdpl_enabled": self.PDPL_COMPLIANCE_ENABLED,
            "data_residency": self.DATA_RESIDENCY_SAUDI,
            "cross_border_allowed": self.CROSS_BORDER_TRANSFER_ALLOWED,
            "moh_integration": self.MOH_INTEGRATION_ENABLED,
            "scfhs_reporting": self.SCFHS_REPORTING_ENABLED,
            "nphies_compliance": self.NPHIES_COMPLIANCE_MODE,
            "arabic_support": self.ARABIC_SUPPORT_ENABLED,
            "rtl_support": self.RTL_SUPPORT_ENABLED
        }
    
    class Config:
        env_file = ".env"
        env_prefix = "HIPAA_"
        case_sensitive = True


class DevelopmentHIPAASettings(HIPAASettings):
    """Development-friendly HIPAA settings that bypass strict validations"""
    
    class Config:
        env_file = ".env"
        env_prefix = "HIPAA_"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in development
    
    @validator('BAA_SIGNED')
    def validate_baa_requirement_dev(cls, v):
        """Allow development without BAA for testing"""
        # In development mode, don't enforce BAA requirement
        import os
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            return v  # Allow False for development
        # In production, enforce the requirement
        if not v:
            raise ValueError("Business Associate Agreement (BAA) must be signed for HIPAA compliance")
        return v
    
    @validator('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN')
    def validate_twilio_credentials_dev(cls, v):
        """Allow development credentials for testing"""
        import os
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            # Allow any value in development mode
            if not v:
                raise ValueError("Twilio credentials must be provided even in development")
            return v
        # In production, enforce strict validation
        if not v or len(v) < 30:
            raise ValueError("Twilio credentials must be properly configured")
        return v


# Global HIPAA settings instance
try:
    import os
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if environment == 'development':
        # Use development-friendly settings
        hipaa_settings = DevelopmentHIPAASettings(
            TWILIO_ACCOUNT_SID=os.getenv('TWILIO_ACCOUNT_SID', 'development_account_sid'),
            TWILIO_AUTH_TOKEN=os.getenv('TWILIO_AUTH_TOKEN', 'development_auth_token'),
            TWILIO_WORKSPACE_SID=os.getenv('TWILIO_WORKSPACE_SID', 'development_workspace_sid'),
            TWILIO_PHONE_NUMBER=os.getenv('TWILIO_PHONE_NUMBER', '+966501234567'),
            TWILIO_VOICE_NUMBER=os.getenv('TWILIO_VOICE_NUMBER', '+966501234567'),
            TWILIO_SMS_NUMBER=os.getenv('TWILIO_SMS_NUMBER', '+966501234567'),
            BAA_SIGNED=os.getenv('BAA_SIGNED', 'false').lower() == 'true'
        )
    else:
        # Use production settings
        hipaa_settings = HIPAASettings()
        
except Exception as e:
    # Ultimate fallback for testing
    print(f"Warning: Could not load HIPAA settings, using minimal test configuration: {e}")
    hipaa_settings = DevelopmentHIPAASettings(
        TWILIO_ACCOUNT_SID="test_account_sid",
        TWILIO_AUTH_TOKEN="test_auth_token", 
        TWILIO_WORKSPACE_SID="test_workspace_sid",
        TWILIO_PHONE_NUMBER="+966501234567",
        TWILIO_VOICE_NUMBER="+966501234567",
        TWILIO_SMS_NUMBER="+966501234567",
        BAA_SIGNED=False
    )


# Configuration validation helper
def validate_hipaa_configuration() -> List[str]:
    """
    Validate HIPAA configuration and return list of issues
    Returns empty list if configuration is valid
    """
    issues = []
    
    try:
        settings = HIPAASettings()
        
        # Check critical requirements
        if not settings.is_baa_valid():
            issues.append("Business Associate Agreement (BAA) is not valid or has expired")
        
        if not settings.ENCRYPTION_AT_REST or not settings.ENCRYPTION_IN_TRANSIT:
            issues.append("Encryption must be configured for both at-rest and in-transit data")
        
        if settings.SESSION_TIMEOUT_MINUTES > 30:
            issues.append("Session timeout exceeds HIPAA recommended maximum of 30 minutes")
        
        if not settings.AUDIT_LOG_LEVEL:
            issues.append("Audit logging must be enabled for HIPAA compliance")
        
        if settings.DATA_RESIDENCY_SAUDI and settings.CROSS_BORDER_TRANSFER_ALLOWED:
            issues.append("Cross-border transfer conflicts with Saudi data residency requirement")
        
        # Check Saudi-specific requirements
        if settings.NPHIES_COMPLIANCE_MODE and not settings.MOH_INTEGRATION_ENABLED:
            issues.append("NPHIES compliance requires MOH integration to be enabled")
        
    except Exception as e:
        issues.append(f"Configuration validation error: {str(e)}")
    
    return issues


# Export main configuration
__all__ = [
    "HIPAASettings",
    "DevelopmentHIPAASettings",
    "LogLevel",
    "EncryptionStandard", 
    "PHIClassification",
    "CommunicationChannel",
    "hipaa_settings",
    "validate_hipaa_configuration"
]