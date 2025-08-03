"""
BrainSAIT Healthcare Platform - HIPAA Custom Exceptions
Comprehensive exception handling for HIPAA-compliant Twilio communications
Supports Saudi Arabia healthcare regulations and compliance requirements
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class HIPAABaseException(Exception):
    """
    Base exception class for all HIPAA-related errors
    Provides structured error handling with audit trail support
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "HIPAA_ERROR",
        details: Optional[Dict[str, Any]] = None,
        audit_required: bool = True,
        severity: str = "ERROR"
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.audit_required = audit_required
        self.severity = severity
        self.timestamp = datetime.utcnow()
        self.error_id = f"{error_code}_{int(self.timestamp.timestamp())}"
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging and API responses"""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "audit_required": self.audit_required
        }
    
    def to_json(self) -> str:
        """Convert exception to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class BAAViolationException(HIPAABaseException):
    """
    Business Associate Agreement violation exception
    Raised when BAA requirements are not met
    """
    
    def __init__(
        self,
        message: str = "Business Associate Agreement violation detected",
        baa_status: Optional[str] = None,
        required_action: Optional[str] = None,
        **kwargs
    ):
        details = {
            "baa_status": baa_status,
            "required_action": required_action,
            "compliance_impact": "HIGH",
            "immediate_action_required": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="BAA_VIOLATION",
            details=details,
            audit_required=True,
            severity="CRITICAL"
        )


class PHIExposureException(HIPAABaseException):
    """
    Protected Health Information exposure exception
    Raised when PHI is detected in insecure contexts
    """
    
    def __init__(
        self,
        message: str = "Protected Health Information exposure detected",
        phi_type: Optional[str] = None,
        exposure_context: Optional[str] = None,
        auto_redacted: bool = False,
        **kwargs
    ):
        details = {
            "phi_type": phi_type,
            "exposure_context": exposure_context,
            "auto_redacted": auto_redacted,
            "risk_level": "HIGH",
            "requires_breach_assessment": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="PHI_EXPOSURE",
            details=details,
            audit_required=True,
            severity="CRITICAL"
        )


class EncryptionException(HIPAABaseException):
    """
    Encryption/Decryption related exception
    Raised when encryption requirements are not met
    """
    
    def __init__(
        self,
        message: str = "Encryption requirement violation",
        encryption_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "encryption_type": encryption_type,
            "operation": operation,
            "security_impact": "HIGH",
            "data_at_risk": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="ENCRYPTION_ERROR",
            details=details,
            audit_required=True,
            severity="ERROR"
        )


class AccessControlException(HIPAABaseException):
    """
    Access control violation exception
    Raised when unauthorized access is attempted
    """
    
    def __init__(
        self,
        message: str = "Access control violation",
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = {
            "user_id": user_id,
            "resource": resource,
            "required_permission": required_permission,
            "access_attempt_blocked": True,
            "requires_investigation": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            details=details,
            audit_required=True,
            severity="WARNING"
        )


class AuditException(HIPAABaseException):
    """
    Audit logging related exception
    Raised when audit requirements cannot be met
    """
    
    def __init__(
        self,
        message: str = "Audit logging failure",
        audit_event: Optional[str] = None,
        failure_reason: Optional[str] = None,
        **kwargs
    ):
        details = {
            "audit_event": audit_event,
            "failure_reason": failure_reason,
            "compliance_risk": "MEDIUM",
            "remediation_required": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="AUDIT_FAILURE",
            details=details,
            audit_required=False,  # Avoid recursive audit logging
            severity="ERROR"
        )


class TwilioHIPAAException(HIPAABaseException):
    """
    Twilio-specific HIPAA compliance exception
    Raised when Twilio operations violate HIPAA requirements
    """
    
    def __init__(
        self,
        message: str = "Twilio HIPAA compliance violation",
        twilio_error_code: Optional[str] = None,
        twilio_message: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = {
            "twilio_error_code": twilio_error_code,
            "twilio_message": twilio_message,
            "operation": operation,
            "platform": "Twilio",
            "requires_vendor_escalation": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="TWILIO_HIPAA_ERROR",
            details=details,
            audit_required=True,
            severity="ERROR"
        )


class DataRetentionException(HIPAABaseException):
    """
    Data retention policy violation exception
    Raised when data retention requirements are not met
    """
    
    def __init__(
        self,
        message: str = "Data retention policy violation",
        data_type: Optional[str] = None,
        retention_period: Optional[int] = None,
        current_age: Optional[int] = None,
        **kwargs
    ):
        details = {
            "data_type": data_type,
            "retention_period_days": retention_period,
            "current_age_days": current_age,
            "action_required": "DATA_DISPOSAL" if current_age and retention_period and current_age > retention_period else "POLICY_UPDATE",
            "compliance_deadline": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="DATA_RETENTION_VIOLATION",
            details=details,
            audit_required=True,
            severity="WARNING"
        )


class SaudiComplianceException(HIPAABaseException):
    """
    Saudi Arabia specific compliance exception
    Raised when Saudi healthcare regulations are violated
    """
    
    def __init__(
        self,
        message: str = "Saudi healthcare compliance violation",
        regulation: Optional[str] = None,
        authority: Optional[str] = None,
        **kwargs
    ):
        details = {
            "regulation": regulation,
            "authority": authority,  # MOH, SCFHS, NPHIES, etc.
            "jurisdiction": "Saudi Arabia",
            "local_reporting_required": True,
            "pdpl_impact": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="SAUDI_COMPLIANCE_VIOLATION",
            details=details,
            audit_required=True,
            severity="ERROR"
        )


class NPHIESComplianceException(SaudiComplianceException):
    """
    NPHIES-specific compliance exception
    Raised when NPHIES integration requirements are violated
    """
    
    def __init__(
        self,
        message: str = "NPHIES compliance violation",
        nphies_error_code: Optional[str] = None,
        fhir_resource: Optional[str] = None,
        **kwargs
    ):
        details = {
            "nphies_error_code": nphies_error_code,
            "fhir_resource": fhir_resource,
            "platform": "NPHIES",
            "requires_nphies_escalation": True
        }
        
        super().__init__(
            message=message,
            regulation="NPHIES Integration Standards",
            authority="MOH - Ministry of Health",
            **kwargs
        )
        
        self.error_code = "NPHIES_COMPLIANCE_VIOLATION"
        self.details.update(details)


class ConfigurationException(HIPAABaseException):
    """
    HIPAA configuration related exception
    Raised when system configuration violates HIPAA requirements
    """
    
    def __init__(
        self,
        message: str = "HIPAA configuration violation",
        config_parameter: Optional[str] = None,
        expected_value: Optional[Any] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        details = {
            "config_parameter": config_parameter,
            "expected_value": str(expected_value),
            "actual_value": str(actual_value),
            "configuration_fix_required": True,
            "system_vulnerability": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="CONFIG_VIOLATION",
            details=details,
            audit_required=True,
            severity="ERROR"
        )


class CommunicationChannelException(HIPAABaseException):
    """
    Communication channel related exception
    Raised when communication channel requirements are violated
    """
    
    def __init__(
        self,
        message: str = "Communication channel violation",
        channel: Optional[str] = None,
        violation_type: Optional[str] = None,
        **kwargs
    ):
        details = {
            "channel": channel,
            "violation_type": violation_type,
            "channel_security_compromised": True,
            "alternative_channel_required": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="CHANNEL_VIOLATION",
            details=details,
            audit_required=True,
            severity="WARNING"
        )


class RateLimitException(HIPAABaseException):
    """
    Rate limiting exception for security protection
    Raised when rate limits are exceeded
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit_type: Optional[str] = None,
        current_rate: Optional[int] = None,
        limit_value: Optional[int] = None,
        **kwargs
    ):
        details = {
            "limit_type": limit_type,
            "current_rate": current_rate,
            "limit_value": limit_value,
            "security_measure": True,
            "temporary_restriction": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            audit_required=True,
            severity="WARNING"
        )


class ArabicProcessingException(HIPAABaseException):
    """
    Arabic text processing related exception
    Raised when Arabic text processing fails in healthcare context
    """
    
    def __init__(
        self,
        message: str = "Arabic text processing error",
        processing_stage: Optional[str] = None,
        text_sample: Optional[str] = None,
        **kwargs
    ):
        details = {
            "processing_stage": processing_stage,
            "text_sample": text_sample[:100] if text_sample else None,  # Truncate for security
            "language": "Arabic",
            "rtl_processing": True,
            "medical_context": True
        }
        details.update(kwargs.get('details', {}))
        
        super().__init__(
            message=message,
            error_code="ARABIC_PROCESSING_ERROR",
            details=details,
            audit_required=True,
            severity="ERROR"
        )


# Exception registry for error code mapping
EXCEPTION_REGISTRY = {
    "BAA_VIOLATION": BAAViolationException,
    "PHI_EXPOSURE": PHIExposureException,
    "ENCRYPTION_ERROR": EncryptionException,
    "ACCESS_DENIED": AccessControlException,
    "AUDIT_FAILURE": AuditException,
    "TWILIO_HIPAA_ERROR": TwilioHIPAAException,
    "DATA_RETENTION_VIOLATION": DataRetentionException,
    "SAUDI_COMPLIANCE_VIOLATION": SaudiComplianceException,
    "NPHIES_COMPLIANCE_VIOLATION": NPHIESComplianceException,
    "CONFIG_VIOLATION": ConfigurationException,
    "CHANNEL_VIOLATION": CommunicationChannelException,
    "RATE_LIMIT_EXCEEDED": RateLimitException,
    "ARABIC_PROCESSING_ERROR": ArabicProcessingException,
    "HIPAA_ERROR": HIPAABaseException
}


def create_exception_from_code(
    error_code: str,
    message: str,
    **kwargs
) -> HIPAABaseException:
    """
    Factory function to create exceptions from error codes
    
    Args:
        error_code: The error code to create exception for
        message: The error message
        **kwargs: Additional parameters for the exception
    
    Returns:
        Instance of appropriate HIPAA exception class
    """
    exception_class = EXCEPTION_REGISTRY.get(error_code, HIPAABaseException)
    return exception_class(message=message, **kwargs)


def get_critical_exceptions() -> List[str]:
    """
    Get list of critical exception codes that require immediate attention
    
    Returns:
        List of critical error codes
    """
    return [
        "BAA_VIOLATION",
        "PHI_EXPOSURE",
        "ENCRYPTION_ERROR",
        "SAUDI_COMPLIANCE_VIOLATION",
        "NPHIES_COMPLIANCE_VIOLATION"
    ]


def is_audit_required(exception: HIPAABaseException) -> bool:
    """
    Check if an exception requires audit logging
    
    Args:
        exception: The HIPAA exception instance
    
    Returns:
        True if audit logging is required
    """
    return exception.audit_required


def format_exception_for_api(exception: HIPAABaseException, include_details: bool = False) -> Dict[str, Any]:
    """
    Format exception for API response
    
    Args:
        exception: The HIPAA exception instance
        include_details: Whether to include detailed error information
    
    Returns:
        Dictionary formatted for API response
    """
    response = {
        "error": True,
        "error_code": exception.error_code,
        "message": exception.message,
        "timestamp": exception.timestamp.isoformat()
    }
    
    if include_details:
        response["details"] = exception.details
        response["error_id"] = exception.error_id
    
    return response


# Export all exception classes and utilities
__all__ = [
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
    "EXCEPTION_REGISTRY",
    "create_exception_from_code",
    "get_critical_exceptions",
    "is_audit_required",
    "format_exception_for_api"
]