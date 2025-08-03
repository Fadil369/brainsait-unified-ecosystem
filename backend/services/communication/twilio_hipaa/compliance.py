"""
BrainSAIT Healthcare Platform - HIPAA Compliance Utilities
Comprehensive HIPAA compliance utilities including PHI detection and data protection
Supports Saudi Arabia healthcare regulations with Arabic text processing
"""

import re
import hashlib
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import logging
from functools import wraps
import arabic_reshaper
from bidi.algorithm import get_display

from .exceptions import (
    PHIExposureException, BAAViolationException, EncryptionException,
    AuditException, ConfigurationException, SaudiComplianceException,
    ArabicProcessingException
)
from ..config.hipaa_settings import hipaa_settings, PHIClassification


# Configure logging for compliance module
compliance_logger = logging.getLogger(__name__)


class PHIType(str, Enum):
    """Types of Protected Health Information"""
    SAUDI_NATIONAL_ID = "saudi_national_id"
    SAUDI_IQAMA = "saudi_iqama"
    PHONE_NUMBER = "phone_number"
    EMAIL_ADDRESS = "email_address"
    MEDICAL_RECORD_NUMBER = "medical_record_number"
    INSURANCE_ID = "insurance_id"
    ARABIC_PERSONAL_NAME = "arabic_personal_name"
    ENGLISH_PERSONAL_NAME = "english_personal_name"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    BIOMETRIC_ID = "biometric_id"
    HEALTH_PLAN_NUMBER = "health_plan_number"
    SOCIAL_SECURITY = "social_security"
    DEVICE_IDENTIFIER = "device_identifier"
    WEB_URL = "web_url"
    IP_ADDRESS = "ip_address"
    LICENSE_NUMBER = "license_number"
    VEHICLE_IDENTIFIER = "vehicle_identifier"


class ComplianceLevel(str, Enum):
    """Compliance validation levels"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


@dataclass
class PHIDetectionResult:
    """Result of PHI detection analysis"""
    phi_detected: bool
    phi_types: List[PHIType]
    confidence_score: float
    detected_patterns: List[Dict[str, Any]]
    redacted_content: Optional[str] = None
    risk_level: str = "LOW"
    recommendations: List[str] = None
    arabic_detected: bool = False
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class ComplianceCheckResult:
    """Result of comprehensive compliance check"""
    compliant: bool
    violations: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_score: float
    audit_required: bool
    timestamp: datetime
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


class HIPAACompliance:
    """
    Comprehensive HIPAA compliance utility class
    Handles PHI detection, data classification, and compliance validation
    """
    
    def __init__(self, compliance_level: ComplianceLevel = ComplianceLevel.STRICT):
        self.compliance_level = compliance_level
        self.settings = hipaa_settings
        self.phi_patterns = self._compile_phi_patterns()
        self.arabic_patterns = self._compile_arabic_patterns()
        self.audit_events = []
        
    def _compile_phi_patterns(self) -> Dict[PHIType, List[re.Pattern]]:
        """Compile regular expression patterns for PHI detection"""
        patterns = {}
        
        # Saudi National ID patterns
        patterns[PHIType.SAUDI_NATIONAL_ID] = [
            re.compile(r'\b\d{10}\b'),  # 10-digit format
            re.compile(r'\b\d{4}-\d{4}-\d{2}\b'),  # Formatted with dashes
            re.compile(r'\b\d{4}\s\d{4}\s\d{2}\b'),  # Formatted with spaces
        ]
        
        # Saudi Iqama patterns
        patterns[PHIType.SAUDI_IQAMA] = [
            re.compile(r'\b[12]\d{9}\b'),  # Starts with 1 or 2, 10 digits total
            re.compile(r'\b[12]\d{3}-\d{4}-\d{2}\b'),  # Formatted Iqama
        ]
        
        # Phone number patterns (Saudi-specific)
        patterns[PHIType.PHONE_NUMBER] = [
            re.compile(r'\+966[0-9]{8,9}'),  # International format
            re.compile(r'966[0-9]{8,9}'),    # Country code without +
            re.compile(r'05[0-9]{8}'),       # Local mobile format
            re.compile(r'01[0-9]{7}'),       # Local landline format
            re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),  # General phone format
        ]
        
        # Email patterns
        patterns[PHIType.EMAIL_ADDRESS] = [
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
        ]
        
        # Medical Record Number patterns
        patterns[PHIType.MEDICAL_RECORD_NUMBER] = [
            re.compile(r'\bMR[N]?\d{6,10}\b', re.IGNORECASE),
            re.compile(r'\bMRN[-:]?\d{6,10}\b', re.IGNORECASE),
            re.compile(r'\bMedical Record[:\s]+\d{6,10}\b', re.IGNORECASE),
        ]
        
        # Insurance ID patterns (including NPHIES)
        patterns[PHIType.INSURANCE_ID] = [
            re.compile(r'\bINS[-:]?\d{8,12}\b', re.IGNORECASE),
            re.compile(r'\bNPHIES[-:]?\d{10}\b', re.IGNORECASE),
            re.compile(r'\bPolicy[-:\s]+\d{8,12}\b', re.IGNORECASE),
        ]
        
        # Date of birth patterns
        patterns[PHIType.DATE_OF_BIRTH] = [
            re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'),  # MM/DD/YYYY
            re.compile(r'\b\d{1,2}-\d{1,2}-\d{4}\b'),  # MM-DD-YYYY
            re.compile(r'\b\d{4}-\d{1,2}-\d{1,2}\b'),  # YYYY-MM-DD
            re.compile(r'\bDOB[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', re.IGNORECASE),
        ]
        
        # Credit card patterns
        patterns[PHIType.CREDIT_CARD] = [
            re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),  # 16-digit cards
            re.compile(r'\b\d{4}[\s-]?\d{6}[\s-]?\d{5}\b'),  # 15-digit cards (Amex)
        ]
        
        # IP Address patterns
        patterns[PHIType.IP_ADDRESS] = [
            re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),  # IPv4
            re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),  # IPv6
        ]
        
        return patterns
    
    def _compile_arabic_patterns(self) -> List[re.Pattern]:
        """Compile Arabic text patterns for PHI detection"""
        return [
            # Arabic name patterns
            re.compile(r'[\u0600-\u06FF\s]{3,}'),  # Arabic Unicode range
            # Common Arabic medical terms
            re.compile(r'(مريض|طبيب|ممرض|دكتور|أستاذ دكتور)[\u0600-\u06FF\s]+', re.IGNORECASE),
            # Arabic phone indicators
            re.compile(r'(هاتف|جوال|رقم)[\u0600-\u06FF\s:]*\d+'),
            # Arabic address indicators
            re.compile(r'(عنوان|منزل|شارع|حي)[\u0600-\u06FF\s]+'),
        ]
    
    async def detect_phi(
        self,
        content: str,
        context: Optional[str] = None,
        auto_redact: bool = None
    ) -> PHIDetectionResult:
        """
        Detect Protected Health Information in content
        
        Args:
            content: Text content to analyze
            context: Context information for better detection
            auto_redact: Whether to automatically redact detected PHI
        
        Returns:
            PHIDetectionResult with detection analysis
        """
        if auto_redact is None:
            auto_redact = self.settings.AUTO_REDACT_ENABLED
        
        try:
            # Initialize result
            result = PHIDetectionResult(
                phi_detected=False,
                phi_types=[],
                confidence_score=0.0,
                detected_patterns=[],
                arabic_detected=self._contains_arabic(content)
            )
            
            # Process Arabic text if detected
            processed_content = content
            if result.arabic_detected:
                processed_content = await self._process_arabic_text(content)
            
            # Detect PHI patterns
            await self._detect_phi_patterns(processed_content, result)
            
            # Calculate overall confidence and risk
            result.confidence_score = self._calculate_confidence_score(result)
            result.risk_level = self._assess_risk_level(result)
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # Auto-redact if enabled and PHI detected
            if auto_redact and result.phi_detected:
                result.redacted_content = await self._redact_phi(content, result)
            
            # Audit logging
            await self._audit_phi_detection(result, context)
            
            return result
            
        except Exception as e:
            compliance_logger.error(f"PHI detection error: {str(e)}")
            raise PHIExposureException(
                message=f"PHI detection failed: {str(e)}",
                phi_type="UNKNOWN",
                exposure_context=context
            )
    
    async def _detect_phi_patterns(self, content: str, result: PHIDetectionResult):
        """Detect specific PHI patterns in content"""
        for phi_type, patterns in self.phi_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    result.phi_detected = True
                    if phi_type not in result.phi_types:
                        result.phi_types.append(phi_type)
                    
                    result.detected_patterns.append({
                        "type": phi_type.value,
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": self._calculate_pattern_confidence(phi_type, match.group())
                    })
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_range = re.compile(r'[\u0600-\u06FF]')
        return bool(arabic_range.search(text))
    
    async def _process_arabic_text(self, text: str) -> str:
        """Process Arabic text for better PHI detection"""
        try:
            # Reshape Arabic text for proper processing
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidi algorithm for RTL text
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            compliance_logger.warning(f"Arabic processing error: {str(e)}")
            raise ArabicProcessingException(
                message=f"Arabic text processing failed: {str(e)}",
                processing_stage="reshape_and_bidi",
                text_sample=text[:100]
            )
    
    def _calculate_pattern_confidence(self, phi_type: PHIType, match: str) -> float:
        """Calculate confidence score for a specific pattern match"""
        base_confidence = 0.7
        
        # Adjust confidence based on PHI type
        confidence_adjustments = {
            PHIType.SAUDI_NATIONAL_ID: 0.95,
            PHIType.SAUDI_IQAMA: 0.95,
            PHIType.EMAIL_ADDRESS: 0.9,
            PHIType.PHONE_NUMBER: 0.85,
            PHIType.MEDICAL_RECORD_NUMBER: 0.9,
            PHIType.INSURANCE_ID: 0.88,
            PHIType.CREDIT_CARD: 0.92,
            PHIType.DATE_OF_BIRTH: 0.75,
        }
        
        return confidence_adjustments.get(phi_type, base_confidence)
    
    def _calculate_confidence_score(self, result: PHIDetectionResult) -> float:
        """Calculate overall confidence score for PHI detection"""
        if not result.detected_patterns:
            return 0.0
        
        total_confidence = sum(pattern["confidence"] for pattern in result.detected_patterns)
        return min(total_confidence / len(result.detected_patterns), 1.0)
    
    def _assess_risk_level(self, result: PHIDetectionResult) -> str:
        """Assess risk level based on detected PHI"""
        if not result.phi_detected:
            return "NONE"
        
        high_risk_types = {
            PHIType.SAUDI_NATIONAL_ID,
            PHIType.SAUDI_IQAMA,
            PHIType.MEDICAL_RECORD_NUMBER,
            PHIType.CREDIT_CARD,
            PHIType.INSURANCE_ID
        }
        
        if any(phi_type in high_risk_types for phi_type in result.phi_types):
            return "HIGH"
        elif len(result.phi_types) > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, result: PHIDetectionResult) -> List[str]:
        """Generate recommendations based on PHI detection"""
        recommendations = []
        
        if result.phi_detected:
            recommendations.append("PHI detected - consider using secure communication channel")
            recommendations.append("Implement data redaction before transmission")
            recommendations.append("Ensure recipient is authorized to receive PHI")
            
            if result.risk_level == "HIGH":
                recommendations.append("HIGH RISK: Immediate manual review required")
                recommendations.append("Consider alternative communication method")
            
            if result.arabic_detected:
                recommendations.append("Arabic text detected - ensure proper encoding and RTL support")
        
        return recommendations
    
    async def _redact_phi(self, content: str, result: PHIDetectionResult) -> str:
        """Redact detected PHI from content"""
        redacted_content = content
        
        # Sort patterns by position (reverse order to maintain indices)
        sorted_patterns = sorted(
            result.detected_patterns,
            key=lambda x: x["start"],
            reverse=True
        )
        
        for pattern in sorted_patterns:
            start, end = pattern["start"], pattern["end"]
            phi_type = pattern["type"]
            
            # Create redaction placeholder
            redaction_placeholder = f"[{phi_type.upper()}_REDACTED]"
            
            # Replace the detected PHI
            redacted_content = (
                redacted_content[:start] +
                redaction_placeholder +
                redacted_content[end:]
            )
        
        return redacted_content
    
    async def validate_baa_compliance(self, vendor: str = "Twilio") -> bool:
        """
        Validate Business Associate Agreement compliance
        
        Args:
            vendor: Vendor name to validate BAA for
        
        Returns:
            True if BAA is valid and compliant
        """
        try:
            if not self.settings.BAA_SIGNED:
                raise BAAViolationException(
                    message=f"No signed BAA found for vendor: {vendor}",
                    baa_status="NOT_SIGNED",
                    required_action="OBTAIN_SIGNED_BAA"
                )
            
            if not self.settings.is_baa_valid():
                raise BAAViolationException(
                    message=f"BAA has expired for vendor: {vendor}",
                    baa_status="EXPIRED",
                    required_action="RENEW_BAA"
                )
            
            # Audit BAA validation
            await self._audit_event(
                event_type="baa_validation",
                details={
                    "vendor": vendor,
                    "baa_status": "VALID",
                    "validation_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return True
            
        except BAAViolationException:
            raise
        except Exception as e:
            compliance_logger.error(f"BAA validation error: {str(e)}")
            raise BAAViolationException(
                message=f"BAA validation failed: {str(e)}",
                baa_status="VALIDATION_ERROR"
            )
    
    async def check_data_residency_compliance(self, data_location: str) -> bool:
        """
        Check if data location complies with Saudi data residency requirements
        
        Args:
            data_location: Location where data will be stored/processed
        
        Returns:
            True if compliant with Saudi data residency requirements
        """
        if not self.settings.DATA_RESIDENCY_SAUDI:
            return True  # No residency requirement
        
        saudi_compliant_locations = {
            "saudi_arabia", "sa", "riyadh", "jeddah", "dammam",
            "middle_east_saudi", "gcc_saudi"
        }
        
        location_lower = data_location.lower()
        is_compliant = any(loc in location_lower for loc in saudi_compliant_locations)
        
        if not is_compliant and not self.settings.CROSS_BORDER_TRANSFER_ALLOWED:
            raise SaudiComplianceException(
                message=f"Data location '{data_location}' violates Saudi data residency requirements",
                regulation="PDPL - Personal Data Protection Law",
                authority="SDAIA - Saudi Data and AI Authority",
                details={
                    "data_location": data_location,
                    "residency_required": True,
                    "cross_border_allowed": False
                }
            )
        
        return is_compliant
    
    async def comprehensive_compliance_check(
        self,
        content: str,
        channel: str,
        recipient: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceCheckResult:
        """
        Perform comprehensive HIPAA compliance check
        
        Args:
            content: Content to be transmitted
            channel: Communication channel (sms, voice, email)
            recipient: Recipient information
            context: Additional context for compliance check
        
        Returns:
            ComplianceCheckResult with comprehensive analysis
        """
        violations = []
        warnings = []
        recommendations = []
        compliance_score = 100.0
        
        try:
            # PHI Detection
            phi_result = await self.detect_phi(content, context=f"{channel}_transmission")
            
            if phi_result.phi_detected:
                if channel.lower() == "sms" and not self.settings.SMS_PHI_ALLOWED:
                    violations.append({
                        "type": "PHI_IN_SMS",
                        "message": "PHI detected in SMS transmission - not allowed",
                        "severity": "CRITICAL",
                        "phi_types": [t.value for t in phi_result.phi_types]
                    })
                    compliance_score -= 30
                
                if phi_result.risk_level == "HIGH":
                    warnings.append({
                        "type": "HIGH_RISK_PHI",
                        "message": "High-risk PHI detected",
                        "phi_types": [t.value for t in phi_result.phi_types]
                    })
                    compliance_score -= 15
            
            # BAA Compliance
            try:
                await self.validate_baa_compliance()
            except BAAViolationException as e:
                violations.append({
                    "type": "BAA_VIOLATION",
                    "message": str(e),
                    "severity": "CRITICAL"
                })
                compliance_score -= 40
            
            # Channel-specific compliance
            channel_config = self.settings.get_channel_config(channel)
            if not channel_config.get("enabled", False):
                violations.append({
                    "type": "CHANNEL_DISABLED",
                    "message": f"Communication channel '{channel}' is disabled",
                    "severity": "HIGH"
                })
                compliance_score -= 25
            
            # Arabic content validation
            if phi_result.arabic_detected:
                if not self.settings.ARABIC_SUPPORT_ENABLED:
                    warnings.append({
                        "type": "ARABIC_NOT_SUPPORTED",
                        "message": "Arabic content detected but Arabic support is disabled"
                    })
                    compliance_score -= 10
                else:
                    recommendations.append("Ensure proper Arabic text encoding and RTL support")
            
            # Generate final recommendations
            recommendations.extend(phi_result.recommendations)
            if compliance_score < 70:
                recommendations.append("CRITICAL: Manual review required before transmission")
            
            result = ComplianceCheckResult(
                compliant=len(violations) == 0 and compliance_score >= 70,
                violations=violations,
                warnings=warnings,
                recommendations=recommendations,
                compliance_score=compliance_score,
                audit_required=phi_result.phi_detected or len(violations) > 0,
                timestamp=datetime.utcnow()
            )
            
            # Audit compliance check
            await self._audit_compliance_check(result, content, channel, context)
            
            return result
            
        except Exception as e:
            compliance_logger.error(f"Compliance check error: {str(e)}")
            raise ConfigurationException(
                message=f"Compliance check failed: {str(e)}",
                config_parameter="compliance_check_system"
            )
    
    async def _audit_phi_detection(
        self,
        result: PHIDetectionResult,
        context: Optional[str] = None
    ):
        """Audit PHI detection event"""
        await self._audit_event(
            event_type="phi_detection",
            details={
                "phi_detected": result.phi_detected,
                "phi_types": [t.value for t in result.phi_types],
                "confidence_score": result.confidence_score,
                "risk_level": result.risk_level,
                "context": context,
                "arabic_detected": result.arabic_detected,
                "patterns_count": len(result.detected_patterns)
            }
        )
    
    async def _audit_compliance_check(
        self,
        result: ComplianceCheckResult,
        content: str,
        channel: str,
        context: Optional[Dict[str, Any]]
    ):
        """Audit comprehensive compliance check"""
        await self._audit_event(
            event_type="compliance_check",
            details={
                "compliant": result.compliant,
                "compliance_score": result.compliance_score,
                "violations_count": len(result.violations),
                "warnings_count": len(result.warnings),
                "channel": channel,
                "content_length": len(content),
                "context": context,
                "audit_required": result.audit_required
            }
        )
    
    async def _audit_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Record audit event"""
        try:
            audit_record = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "details": details,
                "compliance_module": "HIPAACompliance",
                "version": "1.0.0"
            }
            
            # Store audit record
            self.audit_events.append(audit_record)
            
            # Log to audit logger
            compliance_logger.info(
                f"AUDIT: {event_type}",
                extra={"audit_record": audit_record}
            )
            
        except Exception as e:
            compliance_logger.error(f"Audit logging failed: {str(e)}")
            raise AuditException(
                message=f"Failed to record audit event: {str(e)}",
                audit_event=event_type,
                failure_reason=str(e)
            )


# Decorator for automatic compliance checking
def require_hipaa_compliance(
    check_phi: bool = True,
    check_baa: bool = True,
    channel: Optional[str] = None
):
    """
    Decorator to enforce HIPAA compliance on functions
    
    Args:
        check_phi: Whether to check for PHI in function arguments
        check_baa: Whether to validate BAA compliance
        channel: Communication channel for compliance rules
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            compliance = HIPAACompliance()
            
            # Extract content for PHI checking
            content = ""
            if args:
                content = str(args[0]) if args else ""
            if "content" in kwargs:
                content = kwargs["content"]
            if "message" in kwargs:
                content = kwargs["message"]
            
            # Perform compliance checks
            if check_baa:
                await compliance.validate_baa_compliance()
            
            if check_phi and content:
                phi_result = await compliance.detect_phi(content)
                if phi_result.phi_detected and phi_result.risk_level == "HIGH":
                    raise PHIExposureException(
                        message="High-risk PHI detected in function call",
                        phi_type=", ".join([t.value for t in phi_result.phi_types]),
                        exposure_context=func.__name__
                    )
            
            # Execute original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Utility functions
async def mask_phi_for_logging(content: str) -> str:
    """
    Mask PHI in content for safe logging
    
    Args:
        content: Content that may contain PHI
    
    Returns:
        Content with PHI masked for logging
    """
    compliance = HIPAACompliance()
    phi_result = await compliance.detect_phi(content, auto_redact=True)
    
    if phi_result.redacted_content:
        return phi_result.redacted_content
    
    return content


def is_saudi_healthcare_context(context: Optional[Dict[str, Any]]) -> bool:
    """
    Check if context indicates Saudi healthcare environment
    
    Args:
        context: Context information
    
    Returns:
        True if Saudi healthcare context is detected
    """
    if not context:
        return False
    
    saudi_indicators = {
        "saudi", "arabia", "ksa", "riyadh", "jeddah", "dammam",
        "moh", "scfhs", "nphies", "iqama", "national_id"
    }
    
    context_str = json.dumps(context).lower()
    return any(indicator in context_str for indicator in saudi_indicators)


# Export main classes and functions
__all__ = [
    "HIPAACompliance",
    "PHIType",
    "PHIDetectionResult",
    "ComplianceCheckResult",
    "ComplianceLevel",
    "require_hipaa_compliance",
    "mask_phi_for_logging",
    "is_saudi_healthcare_context"
]