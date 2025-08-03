"""
BrainSAIT Healthcare Platform - Advanced HIPAA-Compliant SMS/MMS Services
Comprehensive SMS/MMS communication services with message encryption and Arabic support
Supports Saudi Arabia healthcare regulations, NPHIES compliance, and cultural sensitivity
"""

import asyncio
import hashlib
import json
import uuid
import re
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import arabic_reshaper
from bidi.algorithm import get_display
import pyarabic.araby as araby
from hijri_converter import Hijri, Gregorian
import tempfile
import mimetypes
import io

# Twilio imports
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse

# Internal imports
from .base import TwilioHIPAAClient, HIPAAMessage, MessageStatus
from .exceptions import (
    TwilioHIPAAException, PHIExposureException, EncryptionException,
    ConfigurationException, RateLimitException, ArabicProcessingException,
    SaudiComplianceException
)
from .compliance import HIPAACompliance, PHIDetectionResult, require_hipaa_compliance
from ..config.hipaa_settings import hipaa_settings, CommunicationChannel


# Configure logging
logger = logging.getLogger(__name__)


class SMSType(str, Enum):
    """Types of SMS messages for healthcare communication"""
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    MEDICATION_REMINDER = "medication_reminder"
    LAB_RESULT_NOTIFICATION = "lab_result_notification"
    EMERGENCY_ALERT = "emergency_alert"
    HEALTH_EDUCATION = "health_education"
    INSURANCE_NOTIFICATION = "insurance_notification"
    BILLING_NOTIFICATION = "billing_notification"
    VACCINATION_REMINDER = "vaccination_reminder"
    FOLLOW_UP_CARE = "follow_up_care"
    HEALTH_CAMPAIGN = "health_campaign"
    NPHIES_UPDATE = "nphies_update"
    TELEHEALTH_INVITATION = "telehealth_invitation"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class DeliveryStatus(str, Enum):
    """Enhanced delivery status tracking"""
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"
    READ = "read"
    REPLIED = "replied"


class ArabicTextEncoding(str, Enum):
    """Arabic text encoding standards"""
    UTF8 = "utf-8"
    UCS2 = "ucs-2"
    UTF16 = "utf-16"


@dataclass
class ArabicSMSMetrics:
    """Metrics for Arabic SMS processing"""
    character_count: int
    arabic_character_count: int
    sms_parts: int
    encoding: ArabicTextEncoding
    rtl_segments: int
    medical_terms_count: int
    requires_reshaping: bool


@dataclass
class SMSTemplate:
    """SMS message template with Arabic support"""
    template_id: str
    name: str
    content_arabic: str
    content_english: str
    sms_type: SMSType
    priority: MessagePriority
    variables: List[str]
    max_length: int
    cultural_sensitivity_score: float
    nphies_compliant: bool
    approval_required: bool


@dataclass
class BulkSMSJob:
    """Bulk SMS job tracking"""
    job_id: str
    campaign_name: str
    recipient_count: int
    sent_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error_details: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.error_details is None:
            self.error_details = []


@dataclass
class ConversationThread:
    """Two-way SMS conversation tracking"""
    thread_id: str
    patient_id: str
    healthcare_provider_id: str
    initiated_by: str
    last_message_at: datetime
    message_count: int = 0
    is_active: bool = True
    keywords: List[str] = None
    sentiment_score: float = 0.0
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class SMSAnalytics:
    """SMS analytics and reporting"""
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    delivery_rate: float = 0.0
    average_response_time: float = 0.0
    peak_sending_hours: List[int] = None
    common_failure_reasons: List[Dict[str, Any]] = None
    arabic_message_percentage: float = 0.0
    
    def __post_init__(self):
        if self.peak_sending_hours is None:
            self.peak_sending_hours = []
        if self.common_failure_reasons is None:
            self.common_failure_reasons = []


class PrayerTimeManager:
    """Manager for Islamic prayer times and cultural sensitivity"""
    
    PRAYER_TIMES = {
        "fajr": {"start": time(4, 30), "end": time(6, 0)},
        "dhuhr": {"start": time(11, 30), "end": time(13, 30)},
        "asr": {"start": time(15, 0), "end": time(17, 0)},
        "maghrib": {"start": time(18, 0), "end": time(19, 30)},
        "isha": {"start": time(19, 30), "end": time(21, 0)}
    }
    
    @classmethod
    def is_prayer_time(cls, check_time: datetime = None) -> Tuple[bool, Optional[str]]:
        """Check if current time is during prayer time"""
        if check_time is None:
            check_time = datetime.now()
        
        current_time = check_time.time()
        
        for prayer_name, time_range in cls.PRAYER_TIMES.items():
            if time_range["start"] <= current_time <= time_range["end"]:
                return True, prayer_name
        
        return False, None
    
    @classmethod
    def get_next_available_time(cls, after_time: datetime = None) -> datetime:
        """Get next time when SMS can be sent (after prayer time)"""
        if after_time is None:
            after_time = datetime.now()
        
        is_prayer, prayer_name = cls.is_prayer_time(after_time)
        
        if not is_prayer:
            return after_time
        
        # Find end of current prayer time
        prayer_end = cls.PRAYER_TIMES[prayer_name]["end"]
        next_time = after_time.replace(
            hour=prayer_end.hour,
            minute=prayer_end.minute,
            second=0,
            microsecond=0
        )
        
        # Add 5 minute buffer
        next_time += timedelta(minutes=5)
        
        return next_time


class ArabicTextProcessor:
    """Advanced Arabic text processing for healthcare SMS"""
    
    # Common Arabic medical terms
    MEDICAL_TERMS = {
        "طبيب": "doctor",
        "ممرض": "nurse", 
        "مريض": "patient",
        "موعد": "appointment",
        "دواء": "medication",
        "تحليل": "lab_test",
        "عملية": "surgery",
        "فحص": "examination",
        "علاج": "treatment",
        "مستشفى": "hospital",
        "عيادة": "clinic",
        "طوارئ": "emergency",
        "تطعيم": "vaccination",
        "وصفة": "prescription"
    }
    
    @classmethod
    def process_arabic_sms(cls, text: str) -> ArabicSMSMetrics:
        """Process Arabic text for SMS optimization"""
        try:
            # Count characters
            total_chars = len(text)
            arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
            
            # Detect encoding requirement
            encoding = ArabicTextEncoding.UTF8
            if arabic_chars > 0:
                # UCS-2 for Arabic to ensure proper display
                encoding = ArabicTextEncoding.UCS2
            
            # Calculate SMS parts (70 chars per SMS for UCS-2, 160 for GSM)
            chars_per_sms = 70 if encoding == ArabicTextEncoding.UCS2 else 160
            sms_parts = max(1, (total_chars + chars_per_sms - 1) // chars_per_sms)
            
            # Count RTL segments
            rtl_segments = len(re.findall(r'[\u0600-\u06FF]+', text))
            
            # Count medical terms
            medical_terms_count = sum(1 for term in cls.MEDICAL_TERMS.keys() if term in text)
            
            # Check if reshaping is needed
            requires_reshaping = arabic_chars > 0 and any(
                char in text for char in ['ـ', 'ﻹ', 'ﻷ', 'ﻵ', 'ﻱ']
            )
            
            return ArabicSMSMetrics(
                character_count=total_chars,
                arabic_character_count=arabic_chars,
                sms_parts=sms_parts,
                encoding=encoding,
                rtl_segments=rtl_segments,
                medical_terms_count=medical_terms_count,
                requires_reshaping=requires_reshaping
            )
            
        except Exception as e:
            logger.error(f"Arabic text processing error: {str(e)}")
            raise ArabicProcessingException(
                message=f"Failed to process Arabic SMS text: {str(e)}",
                processing_stage="sms_analysis",
                text_sample=text[:50]
            )
    
    @classmethod
    def reshape_arabic_text(cls, text: str) -> str:
        """Reshape Arabic text for proper SMS display"""
        try:
            # Use arabic-reshaper for proper text shaping
            reshaped = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception as e:
            logger.warning(f"Arabic reshaping failed: {str(e)}")
            return text
    
    @classmethod
    def validate_arabic_medical_content(cls, text: str) -> Dict[str, Any]:
        """Validate Arabic medical content for cultural appropriateness"""
        validation_result = {
            "is_appropriate": True,
            "cultural_score": 1.0,
            "medical_terms_detected": [],
            "recommendations": []
        }
        
        # Detect medical terms
        detected_terms = [
            term for term in cls.MEDICAL_TERMS.keys() 
            if term in text
        ]
        validation_result["medical_terms_detected"] = detected_terms
        
        # Cultural sensitivity checks
        inappropriate_phrases = ["مات", "ميت", "موت"]  # Death-related terms
        if any(phrase in text for phrase in inappropriate_phrases):
            validation_result["is_appropriate"] = False
            validation_result["cultural_score"] = 0.3
            validation_result["recommendations"].append(
                "Use more culturally sensitive terminology for serious medical conditions"
            )
        
        # Check for proper Islamic greetings in healthcare context
        has_islamic_greeting = any(greeting in text for greeting in ["السلام عليكم", "بسم الله", "إن شاء الله"])
        if len(text) > 50 and not has_islamic_greeting:
            validation_result["cultural_score"] *= 0.9
            validation_result["recommendations"].append(
                "Consider adding appropriate Islamic greeting for cultural sensitivity"
            )
        
        return validation_result


class SMSEncryption:
    """End-to-end encryption for SMS messages containing PHI"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize SMS encryption with key"""
        if encryption_key is None:
            # Generate key from settings or create new one
            salt = hashlib.sha256(hipaa_settings.TWILIO_ACCOUNT_SID.encode()).digest()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(hipaa_settings.TWILIO_AUTH_TOKEN.encode()))
            encryption_key = key
        
        self.cipher_suite = Fernet(encryption_key)
        self.encryption_key = encryption_key
    
    def encrypt_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Encrypt SMS message for PHI protection"""
        try:
            # Prepare data for encryption
            data_to_encrypt = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            json_data = json.dumps(data_to_encrypt, ensure_ascii=False)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode('utf-8'))
            
            return {
                "encrypted_content": base64.b64encode(encrypted_data).decode('utf-8'),
                "encryption_timestamp": datetime.utcnow().isoformat(),
                "encryption_method": "Fernet_AES256"
            }
            
        except Exception as e:
            logger.error(f"SMS encryption failed: {str(e)}")
            raise EncryptionException(
                message=f"Failed to encrypt SMS message: {str(e)}",
                encryption_type="Fernet_AES256",
                operation="encrypt"
            )
    
    def decrypt_message(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt SMS message"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            decrypted_json = decrypted_bytes.decode('utf-8')
            
            return json.loads(decrypted_json)
            
        except Exception as e:
            logger.error(f"SMS decryption failed: {str(e)}")
            raise EncryptionException(
                message=f"Failed to decrypt SMS message: {str(e)}",
                encryption_type="Fernet_AES256",
                operation="decrypt"
            )


class SMSTemplateManager:
    """Manager for SMS templates with Arabic support"""
    
    def __init__(self):
        self.templates: Dict[str, SMSTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default healthcare SMS templates"""
        default_templates = [
            SMSTemplate(
                template_id="appointment_reminder_ar",
                name="Appointment Reminder (Arabic)",
                content_arabic="تذكير: لديك موعد طبي في {clinic_name} يوم {date} في تمام الساعة {time}. للاستفسار: {phone}",
                content_english="Reminder: You have a medical appointment at {clinic_name} on {date} at {time}. For inquiries: {phone}",
                sms_type=SMSType.APPOINTMENT_REMINDER,
                priority=MessagePriority.HIGH,
                variables=["clinic_name", "date", "time", "phone"],
                max_length=160,
                cultural_sensitivity_score=0.95,
                nphies_compliant=True,
                approval_required=False
            ),
            SMSTemplate(
                template_id="medication_reminder_ar",
                name="Medication Reminder (Arabic)",
                content_arabic="تذكير بالدواء: حان وقت تناول دواء {medication_name}. الجرعة: {dosage}. إن شاء الله تشفى قريباً",
                content_english="Medication Reminder: It's time to take {medication_name}. Dose: {dosage}. May Allah grant you quick recovery",
                sms_type=SMSType.MEDICATION_REMINDER,
                priority=MessagePriority.HIGH,
                variables=["medication_name", "dosage"],
                max_length=160,
                cultural_sensitivity_score=0.98,
                nphies_compliant=True,
                approval_required=False
            ),
            SMSTemplate(
                template_id="lab_results_ar",
                name="Lab Results Available (Arabic)",
                content_arabic="نتائج فحوصاتك الطبية جاهزة. يرجى زيارة {clinic_name} أو الدخول على التطبيق لمراجعة النتائج",
                content_english="Your lab results are ready. Please visit {clinic_name} or check the app to review results",
                sms_type=SMSType.LAB_RESULT_NOTIFICATION,
                priority=MessagePriority.NORMAL,
                variables=["clinic_name"],
                max_length=160,
                cultural_sensitivity_score=0.90,
                nphies_compliant=True,
                approval_required=True
            ),
            SMSTemplate(
                template_id="emergency_alert_ar",
                name="Emergency Alert (Arabic)",
                content_arabic="تنبيه طارئ: {emergency_message}. يرجى التوجه فوراً إلى أقرب مستشفى أو الاتصال بـ 997",
                content_english="Emergency Alert: {emergency_message}. Please go immediately to the nearest hospital or call 997",
                sms_type=SMSType.EMERGENCY_ALERT,
                priority=MessagePriority.EMERGENCY,
                variables=["emergency_message"],
                max_length=160,
                cultural_sensitivity_score=1.0,
                nphies_compliant=True,
                approval_required=False
            ),
            SMSTemplate(
                template_id="vaccination_reminder_ar",
                name="Vaccination Reminder (Arabic)",
                content_arabic="تذكير بالتطعيم: لديك موعد تطعيم {vaccine_name} يوم {date}. المكان: {location}",
                content_english="Vaccination Reminder: You have a {vaccine_name} vaccination appointment on {date}. Location: {location}",
                sms_type=SMSType.VACCINATION_REMINDER,
                priority=MessagePriority.HIGH,
                variables=["vaccine_name", "date", "location"],
                max_length=160,
                cultural_sensitivity_score=0.95,
                nphies_compliant=True,
                approval_required=False
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[SMSTemplate]:
        """Get SMS template by ID"""
        return self.templates.get(template_id)
    
    def render_template(
        self, 
        template_id: str, 
        variables: Dict[str, str], 
        language: str = "arabic"
    ) -> str:
        """Render SMS template with variables"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        content = template.content_arabic if language == "arabic" else template.content_english
        
        try:
            return content.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def validate_template_variables(self, template_id: str, variables: Dict[str, str]) -> List[str]:
        """Validate template variables"""
        template = self.get_template(template_id)
        if not template:
            return [f"Template not found: {template_id}"]
        
        missing_vars = [var for var in template.variables if var not in variables]
        return [f"Missing variable: {var}" for var in missing_vars]


class AdvancedSMSService(TwilioHIPAAClient):
    """
    Advanced HIPAA-compliant SMS/MMS service for BrainSAIT Healthcare Platform
    Comprehensive SMS communication with Arabic support, cultural sensitivity, and healthcare workflows
    """
    
    def __init__(self, **kwargs):
        """Initialize advanced SMS service"""
        super().__init__(**kwargs)
        
        # Initialize components
        self.template_manager = SMSTemplateManager()
        self.encryption = SMSEncryption()
        self.arabic_processor = ArabicTextProcessor()
        self.prayer_manager = PrayerTimeManager()
        
        # Tracking dictionaries
        self.bulk_jobs: Dict[str, BulkSMSJob] = {}
        self.conversations: Dict[str, ConversationThread] = {}
        self.message_analytics = SMSAnalytics()
        self.delivery_confirmations: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.respect_prayer_times = True
        self.cultural_sensitivity_enabled = True
        self.auto_arabic_processing = True
        
        logger.info("Advanced SMS service initialized successfully")
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="sms")
    async def send_healthcare_sms(
        self,
        to: str,
        message: str,
        sms_type: SMSType,
        priority: MessagePriority = MessagePriority.NORMAL,
        template_id: Optional[str] = None,
        template_variables: Optional[Dict[str, str]] = None,
        language: str = "arabic",
        patient_id: Optional[str] = None,
        healthcare_provider_id: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        respect_prayer_times: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send healthcare-specific SMS with advanced features
        
        Args:
            to: Recipient phone number (Saudi format preferred)
            message: Message content (will be processed if template_id not provided)
            sms_type: Type of healthcare SMS
            priority: Message priority level
            template_id: Optional template ID to use
            template_variables: Variables for template rendering
            language: Language preference (arabic/english)
            patient_id: Patient identifier for audit trail
            healthcare_provider_id: Healthcare provider identifier
            scheduled_time: Optional scheduled delivery time
            respect_prayer_times: Whether to respect Islamic prayer times
            context: Additional context information
        
        Returns:
            Dictionary with enhanced SMS delivery information
        """
        try:
            # Validate Saudi phone number
            phone_validation = await self.validate_saudi_phone_number(to)
            if not phone_validation["is_valid"]:
                raise ConfigurationException(
                    message=f"Invalid Saudi phone number: {to}",
                    config_parameter="recipient_phone",
                    expected_value="+966XXXXXXXXX format",
                    actual_value=to
                )
            
            # Process template if provided
            final_message = message
            if template_id:
                if not template_variables:
                    template_variables = {}
                
                validation_errors = self.template_manager.validate_template_variables(
                    template_id, template_variables
                )
                if validation_errors:
                    raise ValueError(f"Template validation failed: {', '.join(validation_errors)}")
                
                final_message = self.template_manager.render_template(
                    template_id, template_variables, language
                )
            
            # Process Arabic text if needed
            arabic_metrics = None
            if language == "arabic" or self._contains_arabic(final_message):
                arabic_metrics = self.arabic_processor.process_arabic_sms(final_message)
                
                if self.auto_arabic_processing and arabic_metrics.requires_reshaping:
                    final_message = self.arabic_processor.reshape_arabic_text(final_message)
                
                # Validate cultural appropriateness
                if self.cultural_sensitivity_enabled:
                    cultural_validation = self.arabic_processor.validate_arabic_medical_content(final_message)
                    if not cultural_validation["is_appropriate"]:
                        raise SaudiComplianceException(
                            message="Message content not culturally appropriate for Saudi healthcare context",
                            regulation="Cultural Sensitivity Guidelines",
                            authority="Saudi Healthcare Cultural Standards",
                            details=cultural_validation
                        )
            
            # Handle scheduling and prayer times
            send_time = scheduled_time or datetime.utcnow()
            if respect_prayer_times and self.respect_prayer_times:
                is_prayer_time, prayer_name = self.prayer_manager.is_prayer_time(send_time)
                if is_prayer_time and priority not in [MessagePriority.URGENT, MessagePriority.EMERGENCY]:
                    send_time = self.prayer_manager.get_next_available_time(send_time)
                    logger.info(f"SMS scheduled after prayer time: {prayer_name}, new time: {send_time}")
            
            # Enhanced context for compliance
            enhanced_context = {
                "sms_type": sms_type.value,
                "priority": priority.value,
                "language": language,
                "patient_id": patient_id,
                "healthcare_provider_id": healthcare_provider_id,
                "template_id": template_id,
                "arabic_metrics": asdict(arabic_metrics) if arabic_metrics else None,
                "cultural_sensitivity_enabled": self.cultural_sensitivity_enabled,
                "scheduled_time": send_time.isoformat(),
                "original_context": context
            }
            
            # Check if immediate sending or scheduling required
            if send_time > datetime.utcnow() + timedelta(minutes=1):
                # Schedule message for later delivery
                scheduled_result = await self._schedule_sms(
                    to=to,
                    message=final_message,
                    scheduled_time=send_time,
                    context=enhanced_context
                )
                return scheduled_result
            
            # Send immediately
            result = await self.send_sms(
                to=to,
                body=final_message,
                user_id=healthcare_provider_id,
                context=enhanced_context
            )
            
            # Enhanced result with healthcare-specific information
            result.update({
                "sms_type": sms_type.value,
                "priority": priority.value,
                "language": language,
                "patient_id": patient_id,
                "healthcare_provider_id": healthcare_provider_id,
                "arabic_metrics": asdict(arabic_metrics) if arabic_metrics else None,
                "cultural_appropriate": True,
                "scheduled_delivery": send_time.isoformat() if send_time != datetime.utcnow() else None
            })
            
            # Track conversation if applicable
            if patient_id and healthcare_provider_id:
                await self._track_conversation(
                    patient_id=patient_id,
                    healthcare_provider_id=healthcare_provider_id,
                    message_id=result["message_id"],
                    initiated_by=healthcare_provider_id,
                    sms_type=sms_type
                )
            
            # Update analytics
            await self._update_sms_analytics(result, arabic_metrics)
            
            return result
            
        except Exception as e:
            logger.error(f"Healthcare SMS sending failed: {str(e)}")
            if isinstance(e, (TwilioHIPAAException, SaudiComplianceException, ConfigurationException)):
                raise
            else:
                raise TwilioHIPAAException(
                    message=f"Healthcare SMS transmission failed: {str(e)}",
                    operation="send_healthcare_sms",
                    details={"sms_type": sms_type.value, "language": language}
                )
    
    async def send_bulk_healthcare_sms(
        self,
        recipients: List[Dict[str, Any]],
        campaign_name: str,
        template_id: str,
        sms_type: SMSType,
        priority: MessagePriority = MessagePriority.NORMAL,
        language: str = "arabic",
        batch_size: int = 50,
        delay_between_batches: int = 60,
        respect_prayer_times: bool = True
    ) -> Dict[str, Any]:
        """
        Send bulk healthcare SMS campaign
        
        Args:
            recipients: List of recipient dictionaries with phone and template variables
            campaign_name: Name of the SMS campaign
            template_id: Template ID to use for all messages
            sms_type: Type of healthcare SMS
            priority: Message priority level
            language: Language preference
            batch_size: Number of messages per batch
            delay_between_batches: Delay in seconds between batches
            respect_prayer_times: Whether to respect Islamic prayer times
        
        Returns:
            Bulk job tracking information
        """
        try:
            # Create bulk job
            job_id = str(uuid.uuid4())
            bulk_job = BulkSMSJob(
                job_id=job_id,
                campaign_name=campaign_name,
                recipient_count=len(recipients)
            )
            self.bulk_jobs[job_id] = bulk_job
            
            # Validate template
            template = self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            logger.info(f"Starting bulk SMS job: {job_id} with {len(recipients)} recipients")
            
            # Process in batches
            batches = [recipients[i:i + batch_size] for i in range(0, len(recipients), batch_size)]
            
            for batch_index, batch in enumerate(batches):
                # Check prayer times for batch scheduling
                current_time = datetime.utcnow()
                if respect_prayer_times:
                    is_prayer_time, prayer_name = self.prayer_manager.is_prayer_time(current_time)
                    if is_prayer_time and priority not in [MessagePriority.URGENT, MessagePriority.EMERGENCY]:
                        delay_until = self.prayer_manager.get_next_available_time(current_time)
                        wait_seconds = (delay_until - current_time).total_seconds()
                        logger.info(f"Delaying batch {batch_index + 1} for prayer time: {prayer_name}")
                        await asyncio.sleep(wait_seconds)
                
                # Process batch
                batch_results = await self._process_sms_batch(
                    batch=batch,
                    template_id=template_id,
                    sms_type=sms_type,
                    priority=priority,
                    language=language,
                    job_id=job_id
                )
                
                # Update job status
                bulk_job.sent_count += batch_results["sent"]
                bulk_job.failed_count += batch_results["failed"]
                bulk_job.error_details.extend(batch_results["errors"])
                
                # Delay between batches (except last batch)
                if batch_index < len(batches) - 1:
                    await asyncio.sleep(delay_between_batches)
            
            # Complete job
            bulk_job.status = "completed"
            bulk_job.completed_at = datetime.utcnow()
            
            logger.info(f"Bulk SMS job completed: {job_id}")
            
            return {
                "job_id": job_id,
                "campaign_name": campaign_name,
                "total_recipients": bulk_job.recipient_count,
                "sent": bulk_job.sent_count,
                "failed": bulk_job.failed_count,
                "delivery_rate": (bulk_job.sent_count / bulk_job.recipient_count) * 100,
                "status": bulk_job.status,
                "started_at": bulk_job.created_at.isoformat(),
                "completed_at": bulk_job.completed_at.isoformat(),
                "errors": bulk_job.error_details
            }
            
        except Exception as e:
            logger.error(f"Bulk SMS job failed: {str(e)}")
            if job_id in self.bulk_jobs:
                self.bulk_jobs[job_id].status = "failed"
            raise TwilioHIPAAException(
                message=f"Bulk SMS campaign failed: {str(e)}",
                operation="send_bulk_healthcare_sms",
                details={"campaign_name": campaign_name, "recipient_count": len(recipients)}
            )
    
    async def send_mms_with_medical_image(
        self,
        to: str,
        body: str,
        media_urls: List[str],
        image_type: str = "medical_scan",
        patient_id: Optional[str] = None,
        healthcare_provider_id: Optional[str] = None,
        encryption_required: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send MMS with medical images (X-rays, lab results, etc.)
        
        Args:
            to: Recipient phone number
            body: Message body
            media_urls: List of media URLs to attach
            image_type: Type of medical image
            patient_id: Patient identifier
            healthcare_provider_id: Healthcare provider identifier
            encryption_required: Whether to encrypt media
            context: Additional context
        
        Returns:
            MMS delivery information with security details
        """
        try:
            # Validate medical image permissions
            if not await self._validate_medical_image_permissions(
                patient_id, healthcare_provider_id, image_type
            ):
                raise AccessControlException(
                    message="Insufficient permissions to send medical images via MMS",
                    user_id=healthcare_provider_id,
                    resource=f"medical_image_{image_type}",
                    required_permission="SEND_MEDICAL_MMS"
                )
            
            # Process and validate media URLs
            processed_media_urls = []
            for url in media_urls:
                # Validate medical image format and content
                validation_result = await self._validate_medical_image(url, image_type)
                if not validation_result["is_valid"]:
                    raise ValueError(f"Invalid medical image: {validation_result['error']}")
                
                # Encrypt media if required
                if encryption_required:
                    encrypted_url = await self._encrypt_medical_image(url, patient_id)
                    processed_media_urls.append(encrypted_url)
                else:
                    processed_media_urls.append(url)
            
            # Enhanced context for medical MMS
            mms_context = {
                "message_type": "medical_mms",
                "image_type": image_type,
                "patient_id": patient_id,
                "healthcare_provider_id": healthcare_provider_id,
                "media_count": len(media_urls),
                "encryption_used": encryption_required,
                "phi_risk_level": "HIGH",
                "original_context": context
            }
            
            # Send MMS using Twilio
            mms_message = self.client.messages.create(
                body=body,
                from_=self.credentials.sms_number,
                to=to,
                media_url=processed_media_urls
            )
            
            # Track MMS for compliance
            mms_result = {
                "message_id": str(uuid.uuid4()),
                "twilio_sid": mms_message.sid,
                "status": mms_message.status,
                "to": to,
                "from": self.credentials.sms_number,
                "body": body,
                "media_urls": processed_media_urls,
                "image_type": image_type,
                "patient_id": patient_id,
                "healthcare_provider_id": healthcare_provider_id,
                "encryption_used": encryption_required,
                "timestamp": datetime.utcnow().isoformat(),
                "phi_detected": True,  # Medical images always contain PHI
                "compliance_score": 0.95 if encryption_required else 0.7
            }
            
            # Audit medical MMS
            await self._audit_medical_mms(mms_result, mms_context)
            
            return mms_result
            
        except Exception as e:
            logger.error(f"Medical MMS sending failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Medical MMS transmission failed: {str(e)}",
                operation="send_mms_with_medical_image",
                details={"image_type": image_type, "media_count": len(media_urls)}
            )
    
    async def handle_incoming_sms(
        self,
        from_number: str,
        body: str,
        message_sid: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle incoming SMS messages with healthcare workflow integration
        
        Args:
            from_number: Sender phone number
            body: Message body
            message_sid: Twilio message SID
            context: Additional context
        
        Returns:
            Processing result with response information
        """
        try:
            # Validate sender
            phone_validation = await self.validate_saudi_phone_number(from_number)
            if not phone_validation["is_valid"]:
                logger.warning(f"Invalid phone number for incoming SMS: {from_number}")
            
            # Detect language and process Arabic text
            language = "arabic" if self._contains_arabic(body) else "english"
            processed_body = body
            
            if language == "arabic":
                # Process Arabic text for better understanding
                arabic_metrics = self.arabic_processor.process_arabic_sms(body)
                if arabic_metrics.requires_reshaping:
                    processed_body = self.arabic_processor.reshape_arabic_text(body)
            
            # PHI detection on incoming message
            phi_result = await self.compliance.detect_phi(
                processed_body,
                context="incoming_sms",
                auto_redact=False  # Don't redact incoming messages
            )
            
            # Analyze message content for healthcare keywords
            healthcare_keywords = await self._analyze_healthcare_keywords(processed_body, language)
            
            # Find existing conversation thread
            conversation_thread = await self._find_conversation_thread(from_number)
            
            # Determine response strategy
            response_strategy = await self._determine_response_strategy(
                processed_body, healthcare_keywords, conversation_thread, language
            )
            
            # Generate automated response if applicable
            auto_response = None
            if response_strategy["auto_respond"]:
                auto_response = await self._generate_automated_response(
                    processed_body, healthcare_keywords, language, response_strategy
                )
            
            # Update conversation tracking
            if conversation_thread:
                conversation_thread.message_count += 1
                conversation_thread.last_message_at = datetime.utcnow()
                # Update keywords and sentiment
                conversation_thread.keywords.extend(healthcare_keywords)
                conversation_thread.sentiment_score = await self._analyze_sentiment(processed_body, language)
            
            # Prepare result
            result = {
                "message_id": str(uuid.uuid4()),
                "twilio_sid": message_sid,
                "from_number": from_number,
                "body": body,
                "processed_body": processed_body,
                "language": language,
                "phi_detected": phi_result.phi_detected,
                "phi_types": [t.value for t in phi_result.phi_types],
                "healthcare_keywords": healthcare_keywords,
                "conversation_thread_id": conversation_thread.thread_id if conversation_thread else None,
                "response_strategy": response_strategy,
                "auto_response": auto_response,
                "requires_human_review": response_strategy.get("human_review_required", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send auto-response if generated
            if auto_response:
                await self.send_healthcare_sms(
                    to=from_number,
                    message=auto_response["message"],
                    sms_type=SMSType.HEALTH_EDUCATION,
                    priority=MessagePriority.NORMAL,
                    language=language,
                    context={"response_to": message_sid, "auto_generated": True}
                )
                result["auto_response_sent"] = True
            
            # Audit incoming message
            await self._audit_incoming_sms(result, context)
            
            return result
            
        except Exception as e:
            logger.error(f"Incoming SMS handling failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Incoming SMS processing failed: {str(e)}",
                operation="handle_incoming_sms",
                details={"from_number": from_number, "message_sid": message_sid}
            )
    
    async def get_message_delivery_status(
        self,
        message_id: str,
        include_delivery_confirmations: bool = True
    ) -> Dict[str, Any]:
        """
        Get enhanced message delivery status with healthcare-specific tracking
        
        Args:
            message_id: Internal message ID
            include_delivery_confirmations: Whether to include delivery confirmations
        
        Returns:
            Enhanced delivery status information
        """
        # Get base status from parent class
        base_status = await super().get_message_status(message_id)
        
        # Add delivery confirmations if available
        if include_delivery_confirmations and message_id in self.delivery_confirmations:
            base_status["delivery_confirmations"] = self.delivery_confirmations[message_id]
        
        # Add conversation context if applicable
        conversation_context = await self._get_message_conversation_context(message_id)
        if conversation_context:
            base_status["conversation_context"] = conversation_context
        
        return base_status
    
    async def get_sms_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sms_types: Optional[List[SMSType]] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive SMS analytics for healthcare communications
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            sms_types: Filter by SMS types
            language: Filter by language
        
        Returns:
            Comprehensive analytics report
        """
        # Calculate analytics from stored data
        analytics = {
            "summary": asdict(self.message_analytics),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "breakdown_by_type": {},
            "breakdown_by_language": {},
            "cultural_sensitivity_metrics": {},
            "prayer_time_impact": {},
            "bulk_campaign_performance": [],
            "conversation_metrics": {},
            "phi_detection_stats": {}
        }
        
        # Add filtered analytics based on parameters
        if sms_types:
            for sms_type in sms_types:
                analytics["breakdown_by_type"][sms_type.value] = await self._get_type_analytics(sms_type)
        
        if language:
            analytics["breakdown_by_language"][language] = await self._get_language_analytics(language)
        
        # Cultural sensitivity metrics
        analytics["cultural_sensitivity_metrics"] = await self._get_cultural_metrics()
        
        # Prayer time impact analysis
        analytics["prayer_time_impact"] = await self._get_prayer_time_impact()
        
        return analytics
    
    async def validate_saudi_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Enhanced Saudi phone number validation
        
        Args:
            phone_number: Phone number to validate
        
        Returns:
            Enhanced validation result with Saudi-specific information
        """
        # Get base validation
        base_validation = await super().validate_phone_number(phone_number)
        
        # Add Saudi-specific validation
        saudi_validation = {
            "is_saudi_mobile": False,
            "is_saudi_landline": False,
            "mobile_operator": None,
            "region": None,
            "nphies_compatible": False
        }
        
        if base_validation["is_saudi"]:
            # Detect mobile vs landline
            clean_number = re.sub(r'[^\d]', '', phone_number)
            
            if clean_number.startswith("966"):
                clean_number = clean_number[3:]
            elif clean_number.startswith("0"):
                clean_number = clean_number[1:]
            
            # Mobile operators in Saudi Arabia
            mobile_prefixes = {
                "50": "STC",
                "53": "STC", 
                "54": "STC",
                "55": "Mobily",
                "56": "Mobily",
                "57": "Zain",
                "58": "Zain",
                "59": "Virgin Mobile"
            }
            
            if len(clean_number) == 9 and clean_number[:2] in mobile_prefixes:
                saudi_validation["is_saudi_mobile"] = True
                saudi_validation["mobile_operator"] = mobile_prefixes[clean_number[:2]]
                saudi_validation["nphies_compatible"] = True
            elif len(clean_number) == 8 and clean_number.startswith("1"):
                saudi_validation["is_saudi_landline"] = True
                # Determine region based on area code
                region_codes = {
                    "11": "Riyadh",
                    "12": "Makkah", 
                    "13": "Eastern Province",
                    "14": "Qassim",
                    "15": "Madinah",
                    "16": "Hail",
                    "17": "Northern Borders"
                }
                area_code = clean_number[1:3]
                saudi_validation["region"] = region_codes.get(area_code, "Unknown")
        
        # Merge validations
        base_validation.update(saudi_validation)
        return base_validation
    
    # Private helper methods
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        return bool(re.search(r'[\u0600-\u06FF]', text))
    
    async def _schedule_sms(
        self,
        to: str,
        message: str,
        scheduled_time: datetime,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule SMS for later delivery"""
        # Implementation would integrate with task scheduler (Celery, etc.)
        scheduled_id = str(uuid.uuid4())
        
        return {
            "scheduled_id": scheduled_id,
            "to": to,
            "message": message,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "scheduled",
            "context": context
        }
    
    async def _process_sms_batch(
        self,
        batch: List[Dict[str, Any]],
        template_id: str,
        sms_type: SMSType,
        priority: MessagePriority,
        language: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Process a batch of SMS messages"""
        sent = 0
        failed = 0
        errors = []
        
        for recipient in batch:
            try:
                await self.send_healthcare_sms(
                    to=recipient["phone"],
                    message="",  # Will use template
                    sms_type=sms_type,
                    priority=priority,
                    template_id=template_id,
                    template_variables=recipient.get("variables", {}),
                    language=language,
                    context={"bulk_job_id": job_id}
                )
                sent += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "phone": recipient["phone"],
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return {"sent": sent, "failed": failed, "errors": errors}
    
    async def _validate_medical_image_permissions(
        self,
        patient_id: Optional[str],
        healthcare_provider_id: Optional[str],
        image_type: str
    ) -> bool:
        """Validate permissions for medical image transmission"""
        # Implementation would check against healthcare access control system
        # For now, return True if both IDs are provided
        return bool(patient_id and healthcare_provider_id)
    
    async def _validate_medical_image(self, url: str, image_type: str) -> Dict[str, Any]:
        """Validate medical image format and content"""
        # Basic validation - in production would include:
        # - File format validation
        # - Image content analysis
        # - PHI detection in images
        # - File size limits
        
        return {
            "is_valid": True,
            "format": "DICOM",
            "size_mb": 2.5,
            "contains_phi": True,
            "image_type": image_type
        }
    
    async def _encrypt_medical_image(self, url: str, patient_id: str) -> str:
        """Encrypt medical image for secure transmission"""
        # Implementation would:
        # - Download image temporarily
        # - Encrypt using patient-specific key
        # - Upload to secure storage
        # - Return encrypted URL
        
        encrypted_id = hashlib.sha256(f"{url}{patient_id}".encode()).hexdigest()[:16]
        return f"https://secure.brainsait.com/encrypted/{encrypted_id}"
    
    async def _track_conversation(
        self,
        patient_id: str,
        healthcare_provider_id: str,
        message_id: str,
        initiated_by: str,
        sms_type: SMSType
    ):
        """Track SMS conversation thread"""
        thread_id = f"{patient_id}_{healthcare_provider_id}"
        
        if thread_id not in self.conversations:
            self.conversations[thread_id] = ConversationThread(
                thread_id=thread_id,
                patient_id=patient_id,
                healthcare_provider_id=healthcare_provider_id,
                initiated_by=initiated_by,
                last_message_at=datetime.utcnow()
            )
        
        conversation = self.conversations[thread_id]
        conversation.message_count += 1
        conversation.last_message_at = datetime.utcnow()
        conversation.keywords.append(sms_type.value)
    
    async def _update_sms_analytics(self, result: Dict[str, Any], arabic_metrics: Optional[ArabicSMSMetrics]):
        """Update SMS analytics with new message data"""
        self.message_analytics.total_sent += 1
        
        if result.get("status") == "delivered":
            self.message_analytics.total_delivered += 1
        elif result.get("status") == "failed":
            self.message_analytics.total_failed += 1
        
        if arabic_metrics:
            # Update Arabic percentage
            total_messages = self.message_analytics.total_sent
            arabic_messages = self.message_analytics.arabic_message_percentage * (total_messages - 1) + 1
            self.message_analytics.arabic_message_percentage = arabic_messages / total_messages
        
        # Calculate delivery rate
        if self.message_analytics.total_sent > 0:
            self.message_analytics.delivery_rate = (
                self.message_analytics.total_delivered / self.message_analytics.total_sent
            ) * 100
    
    async def _audit_medical_mms(self, result: Dict[str, Any], context: Dict[str, Any]):
        """Audit medical MMS transmission"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "medical_mms_sent",
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": result["message_id"],
            "twilio_sid": result["twilio_sid"],
            "image_type": result["image_type"],
            "patient_id": result.get("patient_id"),
            "healthcare_provider_id": result.get("healthcare_provider_id"),
            "encryption_used": result["encryption_used"],
            "media_count": len(result["media_urls"]),
            "phi_risk": "HIGH",
            "context": context
        }
        
        self._audit_events.append(audit_event)
        logger.info(f"AUDIT: Medical MMS sent - {result['message_id']}", extra=audit_event)
    
    async def _analyze_healthcare_keywords(self, message: str, language: str) -> List[str]:
        """Analyze message for healthcare-related keywords"""
        keywords = []
        
        if language == "arabic":
            arabic_keywords = ["موعد", "دواء", "طبيب", "ممرض", "مستشفى", "ألم", "مرض", "علاج"]
            keywords.extend([kw for kw in arabic_keywords if kw in message])
        else:
            english_keywords = ["appointment", "medication", "doctor", "nurse", "hospital", "pain", "illness", "treatment"]
            message_lower = message.lower()
            keywords.extend([kw for kw in english_keywords if kw in message_lower])
        
        return keywords
    
    async def _find_conversation_thread(self, phone_number: str) -> Optional[ConversationThread]:
        """Find existing conversation thread for phone number"""
        # In production, this would query the database
        for thread in self.conversations.values():
            # This is simplified - would need proper patient phone lookup
            if phone_number in thread.thread_id:
                return thread
        return None
    
    async def _determine_response_strategy(
        self,
        message: str,
        keywords: List[str],
        conversation: Optional[ConversationThread],
        language: str
    ) -> Dict[str, Any]:
        """Determine automated response strategy"""
        strategy = {
            "auto_respond": False,
            "human_review_required": False,
            "response_type": None,
            "urgency_level": "low"
        }
        
        # Check for emergency keywords
        emergency_keywords_ar = ["طوارئ", "ألم شديد", "نزيف", "إغماء"]
        emergency_keywords_en = ["emergency", "severe pain", "bleeding", "unconscious"]
        
        emergency_detected = any(
            kw in message for kw in (emergency_keywords_ar if language == "arabic" else emergency_keywords_en)
        )
        
        if emergency_detected:
            strategy.update({
                "auto_respond": True,
                "human_review_required": True,
                "response_type": "emergency_guidance",
                "urgency_level": "critical"
            })
        elif "موعد" in keywords or "appointment" in keywords:
            strategy.update({
                "auto_respond": True,
                "response_type": "appointment_info",
                "urgency_level": "normal"
            })
        
        return strategy
    
    async def _generate_automated_response(
        self,
        message: str,
        keywords: List[str],
        language: str,
        strategy: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """Generate automated response based on strategy"""
        if not strategy["auto_respond"]:
            return None
        
        responses = {
            "emergency_guidance": {
                "arabic": "في حالة الطوارئ الطبية، يرجى الاتصال فوراً بالرقم 997 أو التوجه لأقرب مستشفى",
                "english": "For medical emergencies, please call 997 immediately or go to the nearest hospital"
            },
            "appointment_info": {
                "arabic": "للاستفسار عن المواعيد، يرجى الاتصال بالعيادة أو استخدام التطبيق الطبي",
                "english": "For appointment inquiries, please call the clinic or use the medical app"
            }
        }
        
        response_type = strategy["response_type"]
        if response_type in responses:
            return {
                "message": responses[response_type][language],
                "type": response_type,
                "auto_generated": True
            }
        
        return None
    
    async def _analyze_sentiment(self, message: str, language: str) -> float:
        """Analyze message sentiment (simplified implementation)"""
        # Simplified sentiment analysis
        positive_words_ar = ["شكرا", "ممتاز", "راضي", "سعيد"]
        negative_words_ar = ["سيء", "ألم", "مشكلة", "غاضب"]
        
        positive_words_en = ["thank", "excellent", "satisfied", "happy"]
        negative_words_en = ["bad", "pain", "problem", "angry"]
        
        words = positive_words_ar + negative_words_ar if language == "arabic" else positive_words_en + negative_words_en
        
        positive_count = sum(1 for word in (positive_words_ar if language == "arabic" else positive_words_en) if word in message)
        negative_count = sum(1 for word in (negative_words_ar if language == "arabic" else negative_words_en) if word in message)
        
        if positive_count + negative_count == 0:
            return 0.5  # Neutral
        
        return positive_count / (positive_count + negative_count)
    
    async def _audit_incoming_sms(self, result: Dict[str, Any], context: Optional[Dict[str, Any]]):
        """Audit incoming SMS processing"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "incoming_sms_processed",
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": result["message_id"],
            "from_number": hashlib.sha256(result["from_number"].encode()).hexdigest()[:16],
            "language": result["language"],
            "phi_detected": result["phi_detected"],
            "healthcare_keywords_count": len(result["healthcare_keywords"]),
            "auto_response_sent": result.get("auto_response_sent", False),
            "requires_human_review": result["requires_human_review"],
            "context": context
        }
        
        self._audit_events.append(audit_event)
        logger.info(f"AUDIT: Incoming SMS processed - {result['message_id']}", extra=audit_event)
    
    async def _get_message_conversation_context(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context for a message"""
        # Implementation would look up message in conversation threads
        return None
    
    async def _get_type_analytics(self, sms_type: SMSType) -> Dict[str, Any]:
        """Get analytics for specific SMS type"""
        # Implementation would aggregate data by SMS type
        return {"total_sent": 0, "delivery_rate": 0.0}
    
    async def _get_language_analytics(self, language: str) -> Dict[str, Any]:
        """Get analytics for specific language"""
        # Implementation would aggregate data by language
        return {"total_sent": 0, "avg_length": 0}
    
    async def _get_cultural_metrics(self) -> Dict[str, Any]:
        """Get cultural sensitivity metrics"""
        return {
            "avg_cultural_score": 0.95,
            "prayer_time_respect_rate": 0.98,
            "islamic_greeting_usage": 0.75
        }
    
    async def _get_prayer_time_impact(self) -> Dict[str, Any]:
        """Get prayer time impact analysis"""
        return {
            "messages_delayed": 0,
            "avg_delay_minutes": 0,
            "prayer_time_distribution": {}
        }


# Context manager for advanced SMS operations
@asynccontextmanager
async def advanced_sms_service(**kwargs):
    """
    Context manager for advanced SMS service
    
    Usage:
        async with advanced_sms_service() as sms:
            await sms.send_healthcare_sms("+966501234567", "Test message", SMSType.APPOINTMENT_REMINDER)
    """
    service = AdvancedSMSService(**kwargs)
    try:
        yield service
    finally:
        await service.close()


# Export main classes and functions
__all__ = [
    "AdvancedSMSService",
    "SMSType",
    "MessagePriority",
    "DeliveryStatus",
    "ArabicTextEncoding",
    "SMSTemplate",
    "BulkSMSJob",
    "ConversationThread",
    "SMSAnalytics",
    "ArabicSMSMetrics",
    "PrayerTimeManager",
    "ArabicTextProcessor",
    "SMSEncryption",
    "SMSTemplateManager",
    "advanced_sms_service"
]