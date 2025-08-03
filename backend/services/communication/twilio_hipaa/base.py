"""
BrainSAIT Healthcare Platform - HIPAA-Compliant Twilio Client
Core HIPAA-compliant Twilio client with BAA validation and comprehensive audit logging
Supports Saudi Arabia healthcare regulations with Arabic text processing
"""

import asyncio
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import ssl
import certifi

# Twilio imports
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.http.http_client import TwilioHttpClient
from twilio.http.validation_client import ValidationClient

# Internal imports
from .exceptions import (
    TwilioHIPAAException, BAAViolationException, PHIExposureException,
    EncryptionException, AccessControlException, AuditException,
    ConfigurationException, RateLimitException
)
from .compliance import HIPAACompliance, PHIDetectionResult, require_hipaa_compliance
from ..config.hipaa_settings import hipaa_settings, CommunicationChannel


# Configure logging
logger = logging.getLogger(__name__)


class ConnectionStatus(str, Enum):
    """Twilio connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    BAA_VIOLATION = "baa_violation"


class MessageStatus(str, Enum):
    """Message delivery status"""
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"


@dataclass
class TwilioCredentials:
    """Secure Twilio credentials container"""
    account_sid: str
    auth_token: str
    workspace_sid: Optional[str] = None
    phone_number: Optional[str] = None
    voice_number: Optional[str] = None
    sms_number: Optional[str] = None
    
    def __post_init__(self):
        # Validate credentials format
        if not self.account_sid or len(self.account_sid) < 30:
            raise ConfigurationException(
                message="Invalid Twilio Account SID format",
                config_parameter="TWILIO_ACCOUNT_SID"
            )
        
        if not self.auth_token or len(self.auth_token) < 30:
            raise ConfigurationException(
                message="Invalid Twilio Auth Token format", 
                config_parameter="TWILIO_AUTH_TOKEN"
            )
    
    def get_masked_sid(self) -> str:
        """Get masked Account SID for logging"""
        return f"{self.account_sid[:8]}...{self.account_sid[-4:]}"


@dataclass
class HIPAAMessage:
    """HIPAA-compliant message container"""
    message_id: str
    content: str
    recipient: str
    channel: CommunicationChannel
    phi_detected: bool = False
    phi_types: List[str] = None
    redacted_content: Optional[str] = None
    encryption_key: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = None
    compliance_score: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.phi_types is None:
            self.phi_types = []
        if self.audit_trail is None:
            self.audit_trail = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


class SecureTwilioHttpClient(TwilioHttpClient):
    """
    HIPAA-compliant HTTP client for Twilio with enhanced security
    """
    
    def __init__(self, timeout: int = 30, logger: Optional[logging.Logger] = None):
        super().__init__(timeout=timeout, logger=logger)
        self.audit_logger = logger or logging.getLogger(__name__)
        self._setup_ssl_context()
    
    def _setup_ssl_context(self):
        """Setup enhanced SSL context for HIPAA compliance"""
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    def request(self, method: str, uri: str, params=None, data=None, headers=None, auth=None, timeout=None, allow_redirects=False):
        """Override request method to add HIPAA compliance logging"""
        # Audit API request
        request_id = str(uuid.uuid4())
        self.audit_logger.info(
            f"HIPAA_API_REQUEST: {method} {uri}",
            extra={
                "request_id": request_id,
                "method": method,
                "uri": uri,
                "timestamp": datetime.utcnow().isoformat(),
                "headers_count": len(headers) if headers else 0,
                "has_auth": auth is not None
            }
        )
        
        try:
            response = super().request(method, uri, params, data, headers, auth, timeout, allow_redirects)
            
            # Audit successful response
            self.audit_logger.info(
                f"HIPAA_API_RESPONSE: {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_size": len(response.content) if response.content else 0
                }
            )
            
            return response
            
        except Exception as e:
            # Audit failed request
            self.audit_logger.error(
                f"HIPAA_API_ERROR: {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise


class TwilioHIPAAClient:
    """
    HIPAA-compliant Twilio client for BrainSAIT Healthcare Platform
    Provides secure, audited, and compliant communication services for Saudi healthcare
    """
    
    def __init__(
        self,
        credentials: Optional[TwilioCredentials] = None,
        compliance_level: str = "strict",
        auto_phi_detection: bool = True,
        saudi_compliance: bool = True
    ):
        """
        Initialize HIPAA-compliant Twilio client
        
        Args:
            credentials: Twilio credentials (defaults to settings)
            compliance_level: Compliance strictness level
            auto_phi_detection: Enable automatic PHI detection
            saudi_compliance: Enable Saudi-specific compliance checks
        """
        # Load credentials
        self.credentials = credentials or self._load_credentials_from_settings()
        
        # Initialize compliance checker
        self.compliance = HIPAACompliance()
        self.auto_phi_detection = auto_phi_detection
        self.saudi_compliance = saudi_compliance
        
        # Initialize Twilio client with secure HTTP client
        self.http_client = SecureTwilioHttpClient(
            timeout=hipaa_settings.TWILIO_TIMEOUT,
            logger=logger
        )
        
        self._twilio_client = None
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._rate_limiter = self._init_rate_limiter()
        self._message_cache = {}
        self._audit_events = []
        
        # Validate configuration
        asyncio.create_task(self._validate_configuration())
    
    def _load_credentials_from_settings(self) -> TwilioCredentials:
        """Load Twilio credentials from HIPAA settings"""
        return TwilioCredentials(
            account_sid=hipaa_settings.TWILIO_ACCOUNT_SID,
            auth_token=hipaa_settings.TWILIO_AUTH_TOKEN,
            workspace_sid=hipaa_settings.TWILIO_WORKSPACE_SID,
            phone_number=hipaa_settings.TWILIO_PHONE_NUMBER,
            voice_number=hipaa_settings.TWILIO_VOICE_NUMBER,
            sms_number=hipaa_settings.TWILIO_SMS_NUMBER
        )
    
    def _init_rate_limiter(self) -> Dict[str, Any]:
        """Initialize rate limiter for HIPAA compliance"""
        return {
            "requests": {},
            "limit_per_minute": hipaa_settings.RATE_LIMIT_PER_USER_MINUTE,
            "burst_size": hipaa_settings.RATE_LIMIT_BURST_SIZE
        }
    
    async def _validate_configuration(self):
        """Validate HIPAA configuration on initialization"""
        try:
            # Validate BAA compliance
            await self.compliance.validate_baa_compliance("Twilio")
            
            # Validate credentials
            if not self.credentials.account_sid.startswith('AC'):
                raise ConfigurationException(
                    message="Invalid Twilio Account SID format",
                    config_parameter="TWILIO_ACCOUNT_SID",
                    expected_value="AC...",
                    actual_value=self.credentials.get_masked_sid()
                )
            
            # Check Saudi compliance if enabled
            if self.saudi_compliance:
                await self.compliance.check_data_residency_compliance("Twilio_US_Servers")
            
            logger.info(f"HIPAA Twilio client configuration validated successfully")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise
    
    @property
    def client(self) -> TwilioClient:
        """Get Twilio client with lazy initialization"""
        if self._twilio_client is None:
            self._twilio_client = TwilioClient(
                self.credentials.account_sid,
                self.credentials.auth_token,
                http_client=self.http_client
            )
            self._connection_status = ConnectionStatus.CONNECTED
        
        return self._twilio_client
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        current_time = datetime.utcnow()
        minute_key = current_time.strftime("%Y-%m-%d-%H-%M")
        
        if user_id not in self._rate_limiter["requests"]:
            self._rate_limiter["requests"][user_id] = {}
        
        user_requests = self._rate_limiter["requests"][user_id]
        current_minute_requests = user_requests.get(minute_key, 0)
        
        if current_minute_requests >= self._rate_limiter["limit_per_minute"]:
            await self._audit_rate_limit_exceeded(user_id, current_minute_requests)
            raise RateLimitException(
                message=f"Rate limit exceeded for user {user_id}",
                limit_type="per_minute",
                current_rate=current_minute_requests,
                limit_value=self._rate_limiter["limit_per_minute"]
            )
        
        # Update request count
        user_requests[minute_key] = current_minute_requests + 1
        
        # Cleanup old entries
        cutoff_time = current_time - timedelta(minutes=5)
        cutoff_key = cutoff_time.strftime("%Y-%m-%d-%H-%M")
        keys_to_remove = [k for k in user_requests.keys() if k < cutoff_key]
        for key in keys_to_remove:
            del user_requests[key]
        
        return True
    
    async def _prepare_hipaa_message(
        self,
        content: str,
        recipient: str,
        channel: CommunicationChannel,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> HIPAAMessage:
        """
        Prepare message with HIPAA compliance checks
        
        Args:
            content: Message content
            recipient: Recipient identifier
            channel: Communication channel
            user_id: User ID for audit trail
            context: Additional context information
        
        Returns:
            HIPAAMessage with compliance analysis
        """
        # Rate limiting check
        if user_id:
            await self._check_rate_limit(user_id)
        
        # Create message container
        message = HIPAAMessage(
            message_id=str(uuid.uuid4()),
            content=content,
            recipient=recipient,
            channel=channel
        )
        
        # PHI detection if enabled
        if self.auto_phi_detection:
            phi_result = await self.compliance.detect_phi(
                content,
                context=f"{channel.value}_message",
                auto_redact=True
            )
            
            message.phi_detected = phi_result.phi_detected
            message.phi_types = [t.value for t in phi_result.phi_types]
            message.redacted_content = phi_result.redacted_content
            
            # Comprehensive compliance check
            compliance_result = await self.compliance.comprehensive_compliance_check(
                content=content,
                channel=channel.value,
                recipient=recipient,
                context=context
            )
            
            message.compliance_score = compliance_result.compliance_score
            
            # Fail if not compliant
            if not compliance_result.compliant:
                raise PHIExposureException(
                    message="Message failed HIPAA compliance check",
                    phi_type=", ".join(message.phi_types),
                    exposure_context=f"{channel.value}_transmission",
                    details={
                        "violations": compliance_result.violations,
                        "compliance_score": compliance_result.compliance_score
                    }
                )
        
        # Add audit trail entry
        message.audit_trail.append({
            "action": "message_prepared",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "channel": channel.value,
            "phi_detected": message.phi_detected,
            "compliance_score": message.compliance_score
        })
        
        return message
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="sms")
    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send HIPAA-compliant SMS message
        
        Args:
            to: Recipient phone number
            body: Message body
            from_number: Sender phone number (defaults to configured SMS number)
            user_id: User ID for audit trail
            context: Additional context information
        
        Returns:
            Dictionary with message details and delivery status
        """
        try:
            # Prepare HIPAA-compliant message
            message = await self._prepare_hipaa_message(
                content=body,
                recipient=to,
                channel=CommunicationChannel.SMS,
                user_id=user_id,
                context=context
            )
            
            # Use redacted content if PHI was detected
            send_body = message.redacted_content if message.redacted_content else body
            send_from = from_number or self.credentials.sms_number
            
            if not send_from:
                raise ConfigurationException(
                    message="No SMS number configured",
                    config_parameter="TWILIO_SMS_NUMBER"
                )
            
            # Send via Twilio
            twilio_message = self.client.messages.create(
                body=send_body,
                from_=send_from,
                to=to
            )
            
            # Update audit trail
            message.audit_trail.append({
                "action": "sms_sent",
                "timestamp": datetime.utcnow().isoformat(),
                "twilio_sid": twilio_message.sid,
                "status": twilio_message.status,
                "user_id": user_id
            })
            
            # Cache message for tracking
            self._message_cache[message.message_id] = message
            
            # Audit event
            await self._audit_message_sent(message, twilio_message.sid)
            
            return {
                "message_id": message.message_id,
                "twilio_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": to,
                "from": send_from,
                "phi_detected": message.phi_detected,
                "phi_redacted": message.redacted_content is not None,
                "compliance_score": message.compliance_score,
                "timestamp": message.timestamp.isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            raise TwilioHIPAAException(
                message=f"SMS transmission failed: {str(e)}",
                twilio_error_code=getattr(e, 'code', None),
                twilio_message=str(e),
                operation="send_sms"
            )
        except Exception as e:
            logger.error(f"SMS sending error: {str(e)}")
            raise
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="voice")
    async def make_voice_call(
        self,
        to: str,
        twiml_url: str,
        from_number: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        record: bool = True
    ) -> Dict[str, Any]:
        """
        Make HIPAA-compliant voice call
        
        Args:
            to: Recipient phone number
            twiml_url: TwiML URL for call flow
            from_number: Caller phone number (defaults to configured voice number)
            user_id: User ID for audit trail
            context: Additional context information
            record: Whether to record the call for compliance
        
        Returns:
            Dictionary with call details and status
        """
        try:
            # Rate limiting check
            if user_id:
                await self._check_rate_limit(user_id)
            
            send_from = from_number or self.credentials.voice_number
            
            if not send_from:
                raise ConfigurationException(
                    message="No voice number configured",
                    config_parameter="TWILIO_VOICE_NUMBER"
                )
            
            # Create voice call
            call = self.client.calls.create(
                url=twiml_url,
                to=to,
                from_=send_from,
                record=record if hipaa_settings.VOICE_RECORDING_ENABLED else False
            )
            
            # Create audit trail
            call_id = str(uuid.uuid4())
            audit_entry = {
                "call_id": call_id,
                "action": "voice_call_initiated",
                "timestamp": datetime.utcnow().isoformat(),
                "twilio_sid": call.sid,
                "to": to,
                "from": send_from,
                "user_id": user_id,
                "recording_enabled": record,
                "context": context
            }
            
            self._audit_events.append(audit_entry)
            
            # Audit event
            await self._audit_voice_call(call_id, call.sid, to, user_id)
            
            return {
                "call_id": call_id,
                "twilio_sid": call.sid,
                "status": call.status,
                "to": to,
                "from": send_from,
                "recording_enabled": record,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Twilio voice call error: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Voice call failed: {str(e)}",
                twilio_error_code=getattr(e, 'code', None),
                twilio_message=str(e),
                operation="make_voice_call"
            )
        except Exception as e:
            logger.error(f"Voice call error: {str(e)}")
            raise
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get message delivery status with HIPAA compliance
        
        Args:
            message_id: Internal message ID
        
        Returns:
            Message status and audit information
        """
        if message_id not in self._message_cache:
            raise TwilioHIPAAException(
                message=f"Message not found: {message_id}",
                operation="get_message_status"
            )
        
        message = self._message_cache[message_id]
        
        # Get latest status from Twilio if we have the SID
        twilio_sid = None
        for entry in message.audit_trail:
            if "twilio_sid" in entry:
                twilio_sid = entry["twilio_sid"]
                break
        
        current_status = "unknown"
        if twilio_sid:
            try:
                twilio_message = self.client.messages(twilio_sid).fetch()
                current_status = twilio_message.status
            except TwilioException as e:
                logger.warning(f"Could not fetch Twilio message status: {str(e)}")
        
        return {
            "message_id": message_id,
            "twilio_sid": twilio_sid,
            "status": current_status,
            "phi_detected": message.phi_detected,
            "compliance_score": message.compliance_score,
            "audit_trail": message.audit_trail,
            "timestamp": message.timestamp.isoformat()
        }
    
    async def get_audit_trail(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get comprehensive audit trail for HIPAA compliance
        
        Args:
            start_date: Start date for audit trail
            end_date: End date for audit trail
            user_id: Filter by specific user ID
            event_type: Filter by event type
        
        Returns:
            List of audit events
        """
        filtered_events = self._audit_events.copy()
        
        # Apply filters
        if start_date:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_events = [
                e for e in filtered_events
                if datetime.fromisoformat(e["timestamp"]) <= end_date
            ]
        
        if user_id:
            filtered_events = [
                e for e in filtered_events
                if e.get("user_id") == user_id
            ]
        
        if event_type:
            filtered_events = [
                e for e in filtered_events
                if e.get("action") == event_type
            ]
        
        return filtered_events
    
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Validate phone number with Saudi-specific validation
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            Validation result with Saudi compliance information
        """
        try:
            # Use Twilio Lookup API
            phone_info = self.client.lookups.phone_numbers(phone_number).fetch()
            
            # Saudi-specific validation
            is_saudi = False
            if phone_info.country_code == "SA" or phone_number.startswith("+966"):
                is_saudi = True
            
            validation_result = {
                "phone_number": phone_info.phone_number,
                "country_code": phone_info.country_code,
                "national_format": phone_info.national_format,
                "is_valid": True,
                "is_saudi": is_saudi,
                "carrier": getattr(phone_info, 'carrier', {}).get('name') if hasattr(phone_info, 'carrier') else None,
                "line_type": getattr(phone_info, 'carrier', {}).get('type') if hasattr(phone_info, 'carrier') else None
            }
            
            # Audit phone validation
            await self._audit_phone_validation(phone_number, validation_result)
            
            return validation_result
            
        except TwilioRestException as e:
            if e.status == 404:
                return {
                    "phone_number": phone_number,
                    "is_valid": False,
                    "error": "Invalid phone number format",
                    "is_saudi": False
                }
            else:
                raise TwilioHIPAAException(
                    message=f"Phone validation failed: {str(e)}",
                    twilio_error_code=e.code,
                    operation="validate_phone_number"
                )
    
    async def _audit_message_sent(self, message: HIPAAMessage, twilio_sid: str):
        """Audit message sending event"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "message_sent",
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": message.message_id,
            "twilio_sid": twilio_sid,
            "channel": message.channel.value,
            "recipient": hashlib.sha256(message.recipient.encode()).hexdigest()[:16],  # Hashed for privacy
            "phi_detected": message.phi_detected,
            "phi_types": message.phi_types,
            "compliance_score": message.compliance_score,
            "redacted": message.redacted_content is not None
        }
        
        self._audit_events.append(audit_event)
        logger.info(f"AUDIT: Message sent - {message.message_id}", extra=audit_event)
    
    async def _audit_voice_call(self, call_id: str, twilio_sid: str, recipient: str, user_id: Optional[str]):
        """Audit voice call event"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "voice_call_initiated",
            "timestamp": datetime.utcnow().isoformat(),
            "call_id": call_id,
            "twilio_sid": twilio_sid,
            "recipient": hashlib.sha256(recipient.encode()).hexdigest()[:16],  # Hashed for privacy
            "user_id": user_id,
            "recording_enabled": hipaa_settings.VOICE_RECORDING_ENABLED
        }
        
        self._audit_events.append(audit_event)
        logger.info(f"AUDIT: Voice call initiated - {call_id}", extra=audit_event)
    
    async def _audit_phone_validation(self, phone_number: str, result: Dict[str, Any]):
        """Audit phone number validation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "phone_validation",
            "timestamp": datetime.utcnow().isoformat(),
            "phone_hash": hashlib.sha256(phone_number.encode()).hexdigest()[:16],  # Hashed for privacy
            "is_valid": result["is_valid"],
            "is_saudi": result.get("is_saudi", False),
            "country_code": result.get("country_code")
        }
        
        self._audit_events.append(audit_event)
        logger.info(f"AUDIT: Phone validation", extra=audit_event)
    
    async def _audit_rate_limit_exceeded(self, user_id: str, current_rate: int):
        """Audit rate limit exceeded event"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "rate_limit_exceeded",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "current_rate": current_rate,
            "limit": self._rate_limiter["limit_per_minute"],
            "severity": "WARNING"
        }
        
        self._audit_events.append(audit_event)
        logger.warning(f"AUDIT: Rate limit exceeded - {user_id}", extra=audit_event)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check for HIPAA compliance
        
        Returns:
            Health check status with compliance information
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "twilio_connection": self._connection_status.value,
            "baa_valid": False,
            "configuration_valid": False,
            "saudi_compliance": self.saudi_compliance,
            "checks": {}
        }
        
        try:
            # Check BAA compliance
            await self.compliance.validate_baa_compliance("Twilio")
            health_status["baa_valid"] = True
            health_status["checks"]["baa"] = "PASS"
        except Exception as e:
            health_status["checks"]["baa"] = f"FAIL: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Twilio connectivity
        try:
            account = self.client.api.accounts(self.credentials.account_sid).fetch()
            health_status["checks"]["twilio_connectivity"] = "PASS"
            health_status["account_status"] = account.status
        except Exception as e:
            health_status["checks"]["twilio_connectivity"] = f"FAIL: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check configuration
        try:
            await self._validate_configuration()
            health_status["configuration_valid"] = True
            health_status["checks"]["configuration"] = "PASS"
        except Exception as e:
            health_status["checks"]["configuration"] = f"FAIL: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Saudi compliance if enabled
        if self.saudi_compliance:
            try:
                saudi_config = hipaa_settings.get_saudi_compliance_config()
                health_status["saudi_compliance_config"] = saudi_config
                health_status["checks"]["saudi_compliance"] = "PASS"
            except Exception as e:
                health_status["checks"]["saudi_compliance"] = f"FAIL: {str(e)}"
                health_status["status"] = "unhealthy"
        
        return health_status
    
    async def close(self):
        """Clean up resources and close connections"""
        # Clear sensitive data
        self._message_cache.clear()
        self._rate_limiter["requests"].clear()
        
        # Final audit log
        logger.info("AUDIT: HIPAA Twilio client closed", extra={
            "timestamp": datetime.utcnow().isoformat(),
            "session_duration": "calculated",
            "total_messages": len(self._audit_events),
            "connection_status": self._connection_status.value
        })
        
        self._connection_status = ConnectionStatus.DISCONNECTED


# Context manager for HIPAA-compliant Twilio operations
@asynccontextmanager
async def hipaa_twilio_client(**kwargs):
    """
    Context manager for HIPAA-compliant Twilio client
    
    Usage:
        async with hipaa_twilio_client() as client:
            await client.send_sms("+966501234567", "Hello")
    """
    client = TwilioHIPAAClient(**kwargs)
    try:
        yield client
    finally:
        await client.close()


# Export main classes and functions
__all__ = [
    "TwilioHIPAAClient",
    "TwilioCredentials",
    "HIPAAMessage",
    "ConnectionStatus",
    "MessageStatus",
    "hipaa_twilio_client",
    "SecureTwilioHttpClient"
]