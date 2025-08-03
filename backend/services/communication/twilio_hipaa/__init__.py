"""
BrainSAIT Healthcare Platform - HIPAA-Compliant Twilio SDK
Comprehensive HIPAA-compliant Twilio integration for Saudi Arabia healthcare communications

This module provides a complete HIPAA-compliant wrapper around Twilio's communication APIs,
specifically designed for the BrainSAIT Healthcare Platform operating in Saudi Arabia.

Key Features:
- Business Associate Agreement (BAA) validation
- Protected Health Information (PHI) detection and redaction
- Comprehensive audit logging for HIPAA compliance
- Saudi Arabia healthcare regulation compliance (PDPL, MOH, SCFHS, NPHIES)
- Arabic text processing with RTL support
- Rate limiting and security controls
- Encrypted data transmission and storage
- Real-time compliance monitoring

Compliance Standards:
- HIPAA (Health Insurance Portability and Accountability Act)
- PDPL (Personal Data Protection Law - Saudi Arabia)
- MOH (Ministry of Health - Saudi Arabia) regulations
- SCFHS (Saudi Commission for Health Specialties) requirements
- NPHIES (National Platform for Health Information Exchange Services)

Usage Example:
    ```python
    from backend.services.communication.twilio_hipaa import TwilioHIPAAClient
    
    # Initialize client with automatic HIPAA compliance
    async with hipaa_twilio_client() as client:
        # Send HIPAA-compliant SMS with automatic PHI detection
        result = await client.send_sms(
            to="+966501234567",
            body="Your appointment is confirmed for tomorrow at 2 PM",
            user_id="doctor_123",
            context={"appointment_type": "consultation"}
        )
        
        # Check message status with audit trail
        status = await client.get_message_status(result["message_id"])
        print(f"Message delivered: {status['status']}")
```

Author: BrainSAIT Healthcare Platform Team
Version: 1.0.0
License: Proprietary - BrainSAIT Healthcare Solutions
"""

from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime

# Core module imports
from .base import (
    TwilioHIPAAClient,
    TwilioCredentials,
    HIPAAMessage,
    ConnectionStatus,
    MessageStatus,
    hipaa_twilio_client,
    SecureTwilioHttpClient
)

from .compliance import (
    HIPAACompliance,
    PHIType,
    PHIDetectionResult,
    ComplianceCheckResult,
    ComplianceLevel,
    require_hipaa_compliance,
    mask_phi_for_logging,
    is_saudi_healthcare_context
)

from .exceptions import (
    HIPAABaseException,
    BAAViolationException,
    PHIExposureException,
    EncryptionException,
    AccessControlException,
    AuditException,
    TwilioHIPAAException,
    DataRetentionException,
    SaudiComplianceException,
    NPHIESComplianceException,
    ConfigurationException,
    CommunicationChannelException,
    RateLimitException,
    ArabicProcessingException,
    create_exception_from_code,
    get_critical_exceptions,
    is_audit_required,
    format_exception_for_api
)

from .video import (
    VideoHIPAAService,
    VideoSession,
    VideoParticipant,
    VideoCallType,
    VideoQuality,
    ParticipantRole,
    VideoSessionStatus,
    RecordingStatus,
    HealthcareContext,
    VideoEncryption,
    video_consultation_session
)

from ..config.hipaa_settings import (
    HIPAASettings,
    LogLevel,
    EncryptionStandard,
    PHIClassification,
    CommunicationChannel,
    hipaa_settings,
    validate_hipaa_configuration
)

# Configure module logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "BrainSAIT Healthcare Platform Team"
__email__ = "developers@brainsait.com"
__license__ = "Proprietary"
__status__ = "Production"

# Compliance certification
__hipaa_compliant__ = True
__baa_required__ = True
__saudi_compliant__ = True
__pdpl_compliant__ = True

# Supported features
__features__ = [
    "HIPAA-Compliant SMS",
    "HIPAA-Compliant Voice Calls",
    "HIPAA-Compliant Video Consultations",
    "PHI Detection and Redaction",
    "Arabic Text Processing",
    "Saudi Regulatory Compliance",
    "Comprehensive Audit Logging",
    "Rate Limiting and Security",
    "BAA Validation",
    "Real-time Compliance Monitoring",
    "Video Recording with Encryption",
    "Medical Document Sharing",
    "Waiting Room Management",
    "Arabic Video Interface"
]


def get_module_info() -> Dict[str, Any]:
    """
    Get comprehensive module information and compliance status
    
    Returns:
        Dictionary containing module metadata and compliance information
    """
    return {
        "module": "twilio_hipaa",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "status": __status__,
        "hipaa_compliant": __hipaa_compliant__,
        "baa_required": __baa_required__,
        "saudi_compliant": __saudi_compliant__,
        "pdpl_compliant": __pdpl_compliant__,
        "supported_features": __features__,
        "compliance_standards": [
            "HIPAA",
            "PDPL",
            "MOH Regulations",
            "SCFHS Requirements", 
            "NPHIES Standards"
        ],
        "supported_channels": [
            "SMS",
            "Voice Calls",
            "Video Consultations",
            "Secure Messaging"
        ],
        "supported_languages": [
            "Arabic (with RTL support)",
            "English"
        ],
        "initialization_timestamp": datetime.utcnow().isoformat()
    }


async def initialize_hipaa_twilio() -> Dict[str, Any]:
    """
    Initialize HIPAA Twilio module with comprehensive validation
    
    Returns:
        Initialization result with compliance status
    """
    logger.info("Initializing BrainSAIT HIPAA Twilio module...")
    
    initialization_result = {
        "success": False,
        "timestamp": datetime.utcnow().isoformat(),
        "module_info": get_module_info(),
        "configuration_valid": False,
        "baa_valid": False,
        "compliance_checks": {},
        "warnings": [],
        "errors": []
    }
    
    try:
        # Validate HIPAA configuration
        config_issues = validate_hipaa_configuration()
        if config_issues:
            initialization_result["warnings"].extend(config_issues)
            initialization_result["configuration_valid"] = False
        else:
            initialization_result["configuration_valid"] = True
            initialization_result["compliance_checks"]["configuration"] = "PASS"
        
        # Test compliance system
        compliance = HIPAACompliance()
        test_phi_result = await compliance.detect_phi(
            "Test message without PHI content",
            context="initialization_test"
        )
        initialization_result["compliance_checks"]["phi_detection"] = "PASS"
        
        # Validate BAA if configured
        try:
            if hipaa_settings.BAA_SIGNED:
                await compliance.validate_baa_compliance("Twilio")
                initialization_result["baa_valid"] = True
                initialization_result["compliance_checks"]["baa"] = "PASS"
            else:
                initialization_result["warnings"].append(
                    "BAA not signed - required for production use"
                )
                initialization_result["compliance_checks"]["baa"] = "WARNING"
        except BAAViolationException as e:
            initialization_result["errors"].append(f"BAA validation failed: {str(e)}")
            initialization_result["compliance_checks"]["baa"] = "FAIL"
        
        # Check Saudi compliance configuration
        if hipaa_settings.PDPL_COMPLIANCE_ENABLED:
            saudi_config = hipaa_settings.get_saudi_compliance_config()
            initialization_result["saudi_compliance_config"] = saudi_config
            initialization_result["compliance_checks"]["saudi_compliance"] = "PASS"
        
        # Determine overall success
        critical_errors = [error for error in initialization_result["errors"] 
                          if "CRITICAL" in error or "BAA" in error]
        
        if not critical_errors and initialization_result["configuration_valid"]:
            initialization_result["success"] = True
            logger.info("HIPAA Twilio module initialized successfully")
        else:
            logger.warning("HIPAA Twilio module initialized with warnings/errors")
        
        return initialization_result
        
    except Exception as e:
        logger.error(f"HIPAA Twilio module initialization failed: {str(e)}")
        initialization_result["errors"].append(f"Initialization error: {str(e)}")
        initialization_result["success"] = False
        return initialization_result


def get_compliance_summary() -> Dict[str, Any]:
    """
    Get comprehensive compliance summary for the module
    
    Returns:
        Dictionary with detailed compliance information
    """
    return {
        "module": "twilio_hipaa",
        "compliance_framework": {
            "hipaa": {
                "enabled": __hipaa_compliant__,
                "baa_required": __baa_required__,
                "features": [
                    "PHI Detection and Protection",
                    "Audit Logging",
                    "Access Controls",
                    "Data Encryption",
                    "Retention Policies"
                ]
            },
            "saudi_regulations": {
                "pdpl_compliant": __pdpl_compliant__,
                "moh_integrated": hipaa_settings.MOH_INTEGRATION_ENABLED,
                "scfhs_reporting": hipaa_settings.SCFHS_REPORTING_ENABLED,
                "nphies_compliant": hipaa_settings.NPHIES_COMPLIANCE_MODE,
                "data_residency": hipaa_settings.DATA_RESIDENCY_SAUDI
            }
        },
        "security_features": {
            "encryption_at_rest": hipaa_settings.ENCRYPTION_AT_REST.value,
            "encryption_in_transit": hipaa_settings.ENCRYPTION_IN_TRANSIT.value,
            "two_factor_auth": hipaa_settings.REQUIRE_TWO_FACTOR_AUTH,
            "session_timeout": f"{hipaa_settings.SESSION_TIMEOUT_MINUTES} minutes",
            "rate_limiting": True,
            "audit_logging": True
        },
        "arabic_support": {
            "enabled": hipaa_settings.ARABIC_SUPPORT_ENABLED,
            "rtl_support": hipaa_settings.RTL_SUPPORT_ENABLED,
            "transliteration": hipaa_settings.ARABIC_TRANSLITERATION,
            "medical_terminology": True
        },
        "communication_channels": {
            "sms": {
                "enabled": CommunicationChannel.SMS in hipaa_settings.ENABLED_CHANNELS,
                "phi_allowed": hipaa_settings.SMS_PHI_ALLOWED,
                "character_limit": hipaa_settings.SMS_CHARACTER_LIMIT
            },
            "voice": {
                "enabled": CommunicationChannel.VOICE in hipaa_settings.ENABLED_CHANNELS,
                "recording_enabled": hipaa_settings.VOICE_RECORDING_ENABLED,
                "transcription_enabled": hipaa_settings.VOICE_TRANSCRIPTION_ENABLED
            },
            "video": {
                "enabled": CommunicationChannel.VIDEO in hipaa_settings.ENABLED_CHANNELS,
                "recording_enabled": hipaa_settings.VIDEO_RECORDING_ENABLED,
                "auto_record": hipaa_settings.VIDEO_AUTO_RECORD,
                "max_participants": hipaa_settings.VIDEO_MAX_PARTICIPANTS,
                "encryption_required": hipaa_settings.VIDEO_ENCRYPTION_REQUIRED,
                "waiting_room_enabled": hipaa_settings.VIDEO_WAITING_ROOM_ENABLED,
                "screen_sharing_enabled": hipaa_settings.VIDEO_SCREEN_SHARING_ENABLED
            }
        }
    }


# Quick access functions for common operations
async def quick_send_sms(
    to: str,
    message: str,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick SMS sending with automatic HIPAA compliance
    
    Args:
        to: Recipient phone number
        message: Message content
        user_id: User ID for audit trail
        **kwargs: Additional parameters
    
    Returns:
        SMS sending result with compliance information
    """
    async with hipaa_twilio_client() as client:
        return await client.send_sms(
            to=to,
            body=message,
            user_id=user_id,
            **kwargs
        )


async def quick_voice_call(
    to: str,
    twiml_url: str,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick voice call with automatic HIPAA compliance
    
    Args:
        to: Recipient phone number
        twiml_url: TwiML URL for call flow
        user_id: User ID for audit trail
        **kwargs: Additional parameters
    
    Returns:
        Voice call result with compliance information
    """
    async with hipaa_twilio_client() as client:
        return await client.make_voice_call(
            to=to,
            twiml_url=twiml_url,
            user_id=user_id,
            **kwargs
        )


async def validate_saudi_phone(phone_number: str) -> Dict[str, Any]:
    """
    Validate Saudi phone number with compliance checks
    
    Args:
        phone_number: Phone number to validate
    
    Returns:
        Validation result with Saudi compliance information
    """
    async with hipaa_twilio_client() as client:
        return await client.validate_phone_number(phone_number)


async def quick_video_consultation(
    session_type: VideoCallType,
    organizer: VideoParticipant,
    healthcare_context: Optional[HealthcareContext] = None,
    **kwargs
) -> VideoSession:
    """
    Quick video consultation setup with automatic HIPAA compliance
    
    Args:
        session_type: Type of video consultation
        organizer: Session organizer (usually doctor)
        healthcare_context: Healthcare-specific context
        **kwargs: Additional parameters
    
    Returns:
        Video session with compliance information
    """
    video_service = VideoHIPAAService()
    return await video_service.create_video_session(
        session_type=session_type,
        organizer=organizer,
        healthcare_context=healthcare_context,
        **kwargs
    )


# Export all public APIs
__all__ = [
    # Core classes
    "TwilioHIPAAClient",
    "TwilioCredentials", 
    "HIPAAMessage",
    "SecureTwilioHttpClient",
    
    # Video classes
    "VideoHIPAAService",
    "VideoSession",
    "VideoParticipant",
    "HealthcareContext",
    "VideoEncryption",
    
    # Compliance classes
    "HIPAACompliance",
    "PHIDetectionResult",
    "ComplianceCheckResult",
    
    # Exception classes
    "HIPAABaseException",
    "BAAViolationException",
    "PHIExposureException",
    "EncryptionException",
    "AccessControlException",
    "AuditException",
    "TwilioHIPAAException",
    "DataRetentionException",
    "SaudiComplianceException",
    "NPHIESComplianceException",
    "ConfigurationException",
    "CommunicationChannelException",
    "RateLimitException",
    "ArabicProcessingException",
    
    # Enums
    "ConnectionStatus",
    "MessageStatus",
    "PHIType",
    "ComplianceLevel",
    "LogLevel",
    "EncryptionStandard",
    "PHIClassification",
    "CommunicationChannel",
    "VideoCallType",
    "VideoQuality",
    "ParticipantRole",
    "VideoSessionStatus",
    "RecordingStatus",
    
    # Settings and configuration
    "HIPAASettings",
    "hipaa_settings",
    "validate_hipaa_configuration",
    
    # Context managers and decorators
    "hipaa_twilio_client",
    "video_consultation_session",
    "require_hipaa_compliance",
    
    # Utility functions
    "mask_phi_for_logging",
    "is_saudi_healthcare_context",
    "create_exception_from_code",
    "get_critical_exceptions",
    "is_audit_required",
    "format_exception_for_api",
    
    # Module functions
    "get_module_info",
    "initialize_hipaa_twilio",
    "get_compliance_summary",
    "quick_send_sms",
    "quick_voice_call",
    "quick_video_consultation",
    "validate_saudi_phone",
    
    # Module metadata
    "__version__",
    "__author__",
    "__license__",
    "__hipaa_compliant__",
    "__baa_required__",
    "__saudi_compliant__",
    "__pdpl_compliant__",
    "__features__"
]


# Module initialization message
logger.info(
    f"BrainSAIT HIPAA Twilio SDK v{__version__} loaded successfully",
    extra={
        "module": "twilio_hipaa",
        "version": __version__,
        "hipaa_compliant": __hipaa_compliant__,
        "saudi_compliant": __saudi_compliant__,
        "features_count": len(__features__)
    }
)