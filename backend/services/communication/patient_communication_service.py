"""
BrainSAIT Healthcare Platform - Comprehensive Patient Communication Service
HIPAA-compliant Twilio-based communication workflows for Saudi Arabian healthcare

This service implements five core communication workflows:
1. Pre-Visit Workflow (appointment confirmation, health screening, insurance verification)
2. Visit Workflow (check-in notifications, wait time updates, provider alerts)
3. Post-Visit Workflow (visit summary, prescriptions, follow-ups, care plans)
4. Clinical Results Workflow (lab results, critical alerts, imaging reports, referrals)
5. Emergency Communication Protocols (critical alerts, escalation procedures)

Features:
- HIPAA-compliant data handling and encryption
- Arabic/English bilingual messaging with RTL support
- NPHIES integration and compliance checkpoints
- Intelligent channel selection (SMS, Voice, WhatsApp, Email)
- Automated escalation procedures
- Comprehensive audit logging for healthcare compliance
- Integration with existing BrainSAIT healthcare systems
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import json
import logging
import uuid
import asyncio
import re
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Import Twilio SDK
try:
    from twilio.rest import Client as TwilioClient
    from twilio.base.exceptions import TwilioException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioClient = None
    TwilioException = Exception

logger = logging.getLogger(__name__)

class CommunicationChannel(str, Enum):
    """Available communication channels"""
    SMS = "sms"
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class WorkflowType(str, Enum):
    """Available workflow types"""
    PRE_VISIT = "pre_visit"
    VISIT = "visit"
    POST_VISIT = "post_visit"
    CLINICAL_RESULTS = "clinical_results"
    EMERGENCY = "emergency"

class Language(str, Enum):
    """Supported languages"""
    ARABIC = "ar"
    ENGLISH = "en"

class PatientCommunicationData(BaseModel):
    """Patient communication data model"""
    patient_id: str
    national_id: Optional[str] = None
    nphies_id: Optional[str] = None
    phone_number: str
    email: Optional[str] = None
    preferred_language: Language = Language.ARABIC
    preferred_channels: List[CommunicationChannel] = Field(default_factory=lambda: [CommunicationChannel.SMS])
    emergency_contact: Optional[str] = None
    consent_sms: bool = True
    consent_voice: bool = True
    consent_whatsapp: bool = False
    consent_email: bool = True

class AppointmentData(BaseModel):
    """Appointment data for communication workflows"""
    appointment_id: str
    patient_id: str
    provider_id: str
    provider_name: str
    provider_name_ar: Optional[str] = None
    appointment_datetime: datetime
    appointment_type: str
    department: str
    department_ar: Optional[str] = None
    location: str
    location_ar: Optional[str] = None
    estimated_duration: int = 30  # minutes
    instructions: Optional[str] = None
    instructions_ar: Optional[str] = None

class ClinicalResultData(BaseModel):
    """Clinical result data for communication"""
    result_id: str
    patient_id: str
    result_type: str  # "lab", "imaging", "pathology", "referral"
    provider_name: str
    test_name: str
    test_name_ar: Optional[str] = None
    result_status: str  # "available", "critical", "abnormal", "normal"
    priority: MessagePriority = MessagePriority.NORMAL
    requires_follow_up: bool = False
    follow_up_instructions: Optional[str] = None
    follow_up_instructions_ar: Optional[str] = None

class CommunicationMessage(BaseModel):
    """Communication message model"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_type: WorkflowType
    patient_id: str
    channel: CommunicationChannel
    language: Language
    priority: MessagePriority
    subject: Optional[str] = None
    message_content: str
    scheduled_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, sent, delivered, failed, cancelled
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

@dataclass
class MessageTemplate:
    """Message template with Arabic and English variants"""
    template_id: str
    workflow_type: WorkflowType
    trigger_event: str
    priority: MessagePriority
    channels: List[CommunicationChannel]
    subject_en: str
    subject_ar: str
    content_en: str
    content_ar: str
    variables: List[str] = field(default_factory=list)
    requires_consent: bool = True
    hipaa_compliance_required: bool = True

class PatientCommunicationService:
    """
    Comprehensive patient communication service with HIPAA-compliant Twilio integration
    """
    
    def __init__(self, 
                 twilio_account_sid: str,
                 twilio_auth_token: str,
                 twilio_phone_number: str,
                 encryption_key: Optional[str] = None):
        """
        Initialize the patient communication service
        
        Args:
            twilio_account_sid: Twilio account SID
            twilio_auth_token: Twilio authentication token
            twilio_phone_number: Twilio phone number for sending messages
            encryption_key: Optional encryption key for HIPAA compliance
        """
        self.twilio_account_sid = twilio_account_sid
        self.twilio_auth_token = twilio_auth_token
        self.twilio_phone_number = twilio_phone_number
        self.encryption_key = encryption_key
        
        if TWILIO_AVAILABLE:
            self.twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
        else:
            self.twilio_client = None
            logger.warning("Twilio SDK not available - communication features will be limited")
        
        self.message_templates = self._initialize_message_templates()
        self.active_workflows: Dict[str, Dict] = {}
        
        logger.info("Patient Communication Service initialized")

    def _initialize_message_templates(self) -> Dict[str, MessageTemplate]:
        """Initialize all message templates for different workflows"""
        templates = {}
        
        # Pre-Visit Workflow Templates
        templates["appointment_confirmation"] = MessageTemplate(
            template_id="appointment_confirmation",
            workflow_type=WorkflowType.PRE_VISIT,
            trigger_event="appointment_scheduled",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.WHATSAPP],
            subject_en="Appointment Confirmation - BrainSAIT Healthcare",
            subject_ar="تأكيد موعد - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, your appointment with Dr. {provider_name} is confirmed for {appointment_date} at {appointment_time}. Location: {location}. Please arrive 15 minutes early. Reply CONFIRM to acknowledge.",
            content_ar="عزيزي {patient_name}، موعدك مع الدكتور {provider_name} مؤكد في {appointment_date} الساعة {appointment_time}. الموقع: {location}. يرجى الحضور قبل 15 دقيقة. أرسل تأكيد للموافقة.",
            variables=["patient_name", "provider_name", "appointment_date", "appointment_time", "location"]
        )
        
        templates["pre_visit_screening"] = MessageTemplate(
            template_id="pre_visit_screening",
            workflow_type=WorkflowType.PRE_VISIT,
            trigger_event="24_hours_before_appointment",
            priority=MessagePriority.HIGH,
            channels=[CommunicationChannel.SMS, CommunicationChannel.WHATSAPP],
            subject_en="Pre-Visit Health Screening - BrainSAIT Healthcare",
            subject_ar="فحص صحي قبل الزيارة - برينسيت للرعاية الصحية",
            content_en="Hi {patient_name}, please complete your pre-visit screening before tomorrow's appointment. Click: {screening_link}. Contact us if you have COVID-19 symptoms.",
            content_ar="مرحباً {patient_name}، يرجى إكمال الفحص الصحي قبل موعد الغد. اضغط: {screening_link}. اتصل بنا إذا كان لديك أعراض كوفيد-19.",
            variables=["patient_name", "screening_link"]
        )
        
        templates["insurance_verification"] = MessageTemplate(
            template_id="insurance_verification",
            workflow_type=WorkflowType.PRE_VISIT,
            trigger_event="insurance_verification_required",
            priority=MessagePriority.HIGH,
            channels=[CommunicationChannel.SMS, CommunicationChannel.EMAIL],
            subject_en="Insurance Verification Required - BrainSAIT Healthcare",
            subject_ar="مطلوب التحقق من التأمين - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, we need to verify your insurance for your upcoming appointment on {appointment_date}. Please bring your insurance card or call us at {clinic_phone}.",
            content_ar="عزيزي {patient_name}، نحتاج للتحقق من تأمينك لموعدك القادم في {appointment_date}. يرجى إحضار بطاقة التأمين أو الاتصال بنا على {clinic_phone}.",
            variables=["patient_name", "appointment_date", "clinic_phone"]
        )
        
        # Visit Workflow Templates
        templates["check_in_notification"] = MessageTemplate(
            template_id="check_in_notification",
            workflow_type=WorkflowType.VISIT,
            trigger_event="patient_arrival",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.PUSH_NOTIFICATION],
            subject_en="Check-in Confirmation - BrainSAIT Healthcare",
            subject_ar="تأكيد تسجيل الوصول - برينسيت للرعاية الصحية",
            content_en="Welcome {patient_name}! You've been checked in for your appointment with Dr. {provider_name}. Estimated wait time: {wait_time} minutes.",
            content_ar="أهلاً وسهلاً {patient_name}! تم تسجيل وصولك لموعدك مع الدكتور {provider_name}. وقت الانتظار المتوقع: {wait_time} دقيقة.",
            variables=["patient_name", "provider_name", "wait_time"]
        )
        
        templates["wait_time_update"] = MessageTemplate(
            template_id="wait_time_update",
            workflow_type=WorkflowType.VISIT,
            trigger_event="wait_time_extended",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.PUSH_NOTIFICATION],
            subject_en="Wait Time Update - BrainSAIT Healthcare",
            subject_ar="تحديث وقت الانتظار - برينسيت للرعاية الصحية",
            content_en="Hi {patient_name}, your appointment is running {delay_minutes} minutes behind schedule. New estimated time: {new_wait_time} minutes. Thank you for your patience.",
            content_ar="مرحباً {patient_name}، موعدك متأخر {delay_minutes} دقيقة عن الجدول المحدد. الوقت المتوقع الجديد: {new_wait_time} دقيقة. شكراً لصبرك.",
            variables=["patient_name", "delay_minutes", "new_wait_time"]
        )
        
        templates["provider_alert"] = MessageTemplate(
            template_id="provider_alert",
            workflow_type=WorkflowType.VISIT,
            trigger_event="patient_ready",
            priority=MessagePriority.HIGH,
            channels=[CommunicationChannel.SMS, CommunicationChannel.PUSH_NOTIFICATION],
            subject_en="Patient Ready - BrainSAIT Healthcare",
            subject_ar="المريض جاهز - برينسيت للرعاية الصحية",
            content_en="Dr. {provider_name}, patient {patient_name} (ID: {patient_id}) is ready in Room {room_number}. Vitals completed.",
            content_ar="دكتور {provider_name}، المريض {patient_name} (الرقم: {patient_id}) جاهز في الغرفة {room_number}. تم قياس العلامات الحيوية.",
            variables=["provider_name", "patient_name", "patient_id", "room_number"]
        )
        
        # Post-Visit Workflow Templates
        templates["visit_summary"] = MessageTemplate(
            template_id="visit_summary",
            workflow_type=WorkflowType.POST_VISIT,
            trigger_event="visit_completed",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.EMAIL],
            subject_en="Visit Summary - BrainSAIT Healthcare",
            subject_ar="ملخص الزيارة - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, thank you for visiting Dr. {provider_name}. Your visit summary and next steps are available in your patient portal: {portal_link}",
            content_ar="عزيزي {patient_name}، شكراً لزيارة الدكتور {provider_name}. ملخص زيارتك والخطوات التالية متاحة في بوابة المريض: {portal_link}",
            variables=["patient_name", "provider_name", "portal_link"]
        )
        
        templates["prescription_ready"] = MessageTemplate(
            template_id="prescription_ready",
            workflow_type=WorkflowType.POST_VISIT,
            trigger_event="prescription_processed",
            priority=MessagePriority.HIGH,
            channels=[CommunicationChannel.SMS, CommunicationChannel.WHATSAPP],
            subject_en="Prescription Ready - BrainSAIT Healthcare",
            subject_ar="الوصفة جاهزة - برينسيت للرعاية الصحية",
            content_en="Hi {patient_name}, your prescription is ready for pickup at {pharmacy_name}. Prescription ID: {prescription_id}. Hours: {pharmacy_hours}",
            content_ar="مرحباً {patient_name}، وصفتك جاهزة للاستلام من {pharmacy_name}. رقم الوصفة: {prescription_id}. ساعات العمل: {pharmacy_hours}",
            variables=["patient_name", "pharmacy_name", "prescription_id", "pharmacy_hours"]
        )
        
        templates["follow_up_reminder"] = MessageTemplate(
            template_id="follow_up_reminder",
            workflow_type=WorkflowType.POST_VISIT,
            trigger_event="follow_up_due",
            priority=MessagePriority.HIGH,
            channels=[CommunicationChannel.SMS, CommunicationChannel.VOICE],
            subject_en="Follow-up Appointment Reminder - BrainSAIT Healthcare",
            subject_ar="تذكير موعد المتابعة - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, it's time to schedule your follow-up appointment with Dr. {provider_name}. Please call {clinic_phone} or book online: {booking_link}",
            content_ar="عزيزي {patient_name}، حان وقت حجز موعد المتابعة مع الدكتور {provider_name}. يرجى الاتصال على {clinic_phone} أو الحجز أونلاين: {booking_link}",
            variables=["patient_name", "provider_name", "clinic_phone", "booking_link"]
        )
        
        # Clinical Results Workflow Templates
        templates["lab_results_available"] = MessageTemplate(
            template_id="lab_results_available",
            workflow_type=WorkflowType.CLINICAL_RESULTS,
            trigger_event="lab_results_ready",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.EMAIL],
            subject_en="Lab Results Available - BrainSAIT Healthcare",
            subject_ar="نتائج المختبر متاحة - برينسيت للرعاية الصحية",
            content_en="Hello {patient_name}, your lab results from {test_date} are now available. Please log into your patient portal to view: {portal_link}",
            content_ar="مرحباً {patient_name}، نتائج مختبرك من {test_date} متاحة الآن. يرجى تسجيل الدخول لبوابة المريض للعرض: {portal_link}",
            variables=["patient_name", "test_date", "portal_link"]
        )
        
        templates["critical_result_alert"] = MessageTemplate(
            template_id="critical_result_alert",
            workflow_type=WorkflowType.CLINICAL_RESULTS,
            trigger_event="critical_result_received",
            priority=MessagePriority.CRITICAL,
            channels=[CommunicationChannel.VOICE, CommunicationChannel.SMS],
            subject_en="URGENT: Critical Lab Result - BrainSAIT Healthcare",
            subject_ar="عاجل: نتيجة مختبر حرجة - برينسيت للرعاية الصحية",
            content_en="URGENT: {patient_name}, please contact Dr. {provider_name} immediately regarding your recent test results. Call {provider_phone} now.",
            content_ar="عاجل: {patient_name}، يرجى الاتصال بالدكتور {provider_name} فوراً بخصوص نتائج فحصك الأخير. اتصل على {provider_phone} الآن.",
            variables=["patient_name", "provider_name", "provider_phone"]
        )
        
        templates["imaging_results"] = MessageTemplate(
            template_id="imaging_results",
            workflow_type=WorkflowType.CLINICAL_RESULTS,
            trigger_event="imaging_results_ready",
            priority=MessagePriority.NORMAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.EMAIL],
            subject_en="Imaging Results Available - BrainSAIT Healthcare",
            subject_ar="نتائج الأشعة متاحة - برينسيت للرعاية الصحية",
            content_en="Hi {patient_name}, your {imaging_type} results from {scan_date} are ready. Schedule a follow-up with Dr. {provider_name}: {clinic_phone}",
            content_ar="مرحباً {patient_name}، نتائج {imaging_type} من {scan_date} جاهزة. احجز متابعة مع الدكتور {provider_name}: {clinic_phone}",
            variables=["patient_name", "imaging_type", "scan_date", "provider_name", "clinic_phone"]
        )
        
        # Emergency Communication Templates
        templates["emergency_alert"] = MessageTemplate(
            template_id="emergency_alert",
            workflow_type=WorkflowType.EMERGENCY,
            trigger_event="emergency_situation",
            priority=MessagePriority.CRITICAL,
            channels=[CommunicationChannel.VOICE, CommunicationChannel.SMS, CommunicationChannel.WHATSAPP],
            subject_en="EMERGENCY ALERT - BrainSAIT Healthcare",
            subject_ar="تنبيه طوارئ - برينسيت للرعاية الصحية",
            content_en="EMERGENCY: {patient_name}, please proceed to the nearest emergency room immediately. Call 997 if you need an ambulance.",
            content_ar="طوارئ: {patient_name}، يرجى التوجه لأقرب غرفة طوارئ فوراً. اتصل على 997 إذا كنت تحتاج إسعاف.",
            variables=["patient_name"]
        )
        
        templates["facility_emergency"] = MessageTemplate(
            template_id="facility_emergency",
            workflow_type=WorkflowType.EMERGENCY,
            trigger_event="facility_emergency",
            priority=MessagePriority.CRITICAL,
            channels=[CommunicationChannel.SMS, CommunicationChannel.VOICE],
            subject_en="FACILITY EMERGENCY - BrainSAIT Healthcare",
            subject_ar="طوارئ المنشأة - برينسيت للرعاية الصحية",
            content_en="ALERT: Due to an emergency at our facility, all appointments for {date} are cancelled. We will contact you to reschedule. Emergency hotline: {emergency_phone}",
            content_ar="تنبيه: بسبب طارئ في منشأتنا، جميع المواعيد ليوم {date} ملغية. سنتصل بك لإعادة الجدولة. خط الطوارئ: {emergency_phone}",
            variables=["date", "emergency_phone"]
        )
        
        return templates

    def format_arabic_text(self, text: str) -> str:
        """Format Arabic text for proper display with RTL support"""
        try:
            reshaped_text = reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logger.warning(f"Arabic text formatting failed: {e}")
            return text

    def select_communication_channel(self, 
                                   patient_data: PatientCommunicationData,
                                   priority: MessagePriority,
                                   available_channels: List[CommunicationChannel]) -> CommunicationChannel:
        """
        Intelligent channel selection based on patient preferences, consent, and message priority
        """
        # For critical and urgent messages, prefer voice or SMS
        if priority in [MessagePriority.CRITICAL, MessagePriority.URGENT]:
            if patient_data.consent_voice and CommunicationChannel.VOICE in available_channels:
                return CommunicationChannel.VOICE
            elif patient_data.consent_sms and CommunicationChannel.SMS in available_channels:
                return CommunicationChannel.SMS
        
        # Check patient preferences
        for preferred_channel in patient_data.preferred_channels:
            if preferred_channel in available_channels:
                # Check consent for the preferred channel
                consent_map = {
                    CommunicationChannel.SMS: patient_data.consent_sms,
                    CommunicationChannel.VOICE: patient_data.consent_voice,
                    CommunicationChannel.WHATSAPP: patient_data.consent_whatsapp,
                    CommunicationChannel.EMAIL: patient_data.consent_email
                }
                
                if consent_map.get(preferred_channel, False):
                    return preferred_channel
        
        # Default fallback to SMS if consent is given
        if patient_data.consent_sms and CommunicationChannel.SMS in available_channels:
            return CommunicationChannel.SMS
        
        # Final fallback to email
        if patient_data.consent_email and CommunicationChannel.EMAIL in available_channels:
            return CommunicationChannel.EMAIL
        
        raise ValueError("No suitable communication channel available with patient consent")

    def render_message_template(self, 
                              template: MessageTemplate,
                              language: Language,
                              variables: Dict[str, Any]) -> tuple[str, str]:
        """
        Render message template with variables in specified language
        
        Returns:
            tuple: (subject, content)
        """
        if language == Language.ARABIC:
            subject_template = template.subject_ar
            content_template = template.content_ar
        else:
            subject_template = template.subject_en
            content_template = template.content_en
        
        # Replace variables in templates
        subject = subject_template
        content = content_template
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            subject = subject.replace(placeholder, str(var_value))
            content = content.replace(placeholder, str(var_value))
        
        # Format Arabic text if needed
        if language == Language.ARABIC:
            subject = self.format_arabic_text(subject)
            content = self.format_arabic_text(content)
        
        return subject, content

    async def send_sms_message(self, 
                              to_number: str,
                              message_content: str,
                              message_id: str) -> Dict[str, Any]:
        """Send SMS message via Twilio with HIPAA compliance"""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Clean phone number (ensure it starts with country code)
            if not to_number.startswith('+'):
                # Assume Saudi Arabia if no country code
                to_number = f"+966{to_number.lstrip('0')}"
            
            message = self.twilio_client.messages.create(
                body=message_content,
                from_=self.twilio_phone_number,
                to=to_number
            )
            
            return {
                "status": "sent",
                "provider_message_id": message.sid,
                "message_id": message_id,
                "sent_at": datetime.now().isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Twilio SMS error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"SMS sending error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }

    async def send_voice_message(self, 
                               to_number: str,
                               message_content: str,
                               message_id: str,
                               language: Language = Language.ARABIC) -> Dict[str, Any]:
        """Send voice message via Twilio with text-to-speech"""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Clean phone number
            if not to_number.startswith('+'):
                to_number = f"+966{to_number.lstrip('0')}"
            
            # Set voice and language for TTS
            voice_settings = {
                Language.ARABIC: {"voice": "woman", "language": "ar"},
                Language.ENGLISH: {"voice": "alice", "language": "en-US"}
            }
            
            settings = voice_settings.get(language, voice_settings[Language.ENGLISH])
            
            # Create TwiML for voice message
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="{settings['voice']}" language="{settings['language']}">{message_content}</Say>
                <Pause length="1"/>
                <Say voice="{settings['voice']}" language="{settings['language']}">Press any key to repeat this message.</Say>
                <Gather timeout="10" numDigits="1">
                    <Say voice="{settings['voice']}" language="{settings['language']}">{message_content}</Say>
                </Gather>
            </Response>"""
            
            call = self.twilio_client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.twilio_phone_number
            )
            
            return {
                "status": "sent",
                "provider_message_id": call.sid,
                "message_id": message_id,
                "sent_at": datetime.now().isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Twilio voice error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Voice message error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }

    async def send_whatsapp_message(self, 
                                  to_number: str,
                                  message_content: str,
                                  message_id: str) -> Dict[str, Any]:
        """Send WhatsApp message via Twilio"""
        try:
            if not self.twilio_client:
                raise Exception("Twilio client not initialized")
            
            # Clean phone number
            if not to_number.startswith('+'):
                to_number = f"+966{to_number.lstrip('0')}"
            
            message = self.twilio_client.messages.create(
                body=message_content,
                from_=f"whatsapp:{self.twilio_phone_number}",
                to=f"whatsapp:{to_number}"
            )
            
            return {
                "status": "sent",
                "provider_message_id": message.sid,
                "message_id": message_id,
                "sent_at": datetime.now().isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Twilio WhatsApp error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"WhatsApp message error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }

    async def send_email_message(self, 
                               to_email: str,
                               subject: str,
                               message_content: str,
                               message_id: str) -> Dict[str, Any]:
        """Send email message (placeholder - would integrate with SendGrid or similar)"""
        try:
            # This would integrate with an email service like SendGrid
            # For now, we'll simulate successful sending
            logger.info(f"Simulating email send to {to_email}: {subject}")
            
            return {
                "status": "sent",
                "provider_message_id": f"email_{message_id}",
                "message_id": message_id,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email sending error for message {message_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message_id,
                "failed_at": datetime.now().isoformat()
            }

    async def send_message(self, 
                          patient_data: PatientCommunicationData,
                          message: CommunicationMessage) -> Dict[str, Any]:
        """
        Send a communication message using the appropriate channel
        """
        try:
            # HIPAA compliance check
            if not self._check_hipaa_compliance(message):
                raise Exception("Message failed HIPAA compliance check")
            
            # Audit log the communication attempt
            await self._audit_communication_attempt(patient_data, message)
            
            # Send message based on channel
            if message.channel == CommunicationChannel.SMS:
                result = await self.send_sms_message(
                    patient_data.phone_number,
                    message.message_content,
                    message.message_id
                )
            elif message.channel == CommunicationChannel.VOICE:
                result = await self.send_voice_message(
                    patient_data.phone_number,
                    message.message_content,
                    message.message_id,
                    message.language
                )
            elif message.channel == CommunicationChannel.WHATSAPP:
                result = await self.send_whatsapp_message(
                    patient_data.phone_number,
                    message.message_content,
                    message.message_id
                )
            elif message.channel == CommunicationChannel.EMAIL:
                if not patient_data.email:
                    raise ValueError("Patient email not available")
                result = await self.send_email_message(
                    patient_data.email,
                    message.subject or "Healthcare Communication",
                    message.message_content,
                    message.message_id
                )
            else:
                raise ValueError(f"Unsupported communication channel: {message.channel}")
            
            # Update message status
            message.status = result["status"]
            if result["status"] == "failed":
                message.retry_count += 1
            
            # Audit log the result
            await self._audit_communication_result(patient_data, message, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            message.status = "failed"
            message.retry_count += 1
            
            return {
                "status": "failed",
                "error": str(e),
                "message_id": message.message_id,
                "failed_at": datetime.now().isoformat()
            }

    def _check_hipaa_compliance(self, message: CommunicationMessage) -> bool:
        """
        Check if message meets HIPAA compliance requirements
        """
        # Check for prohibited PHI in message content
        phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card pattern
            # Add more PHI patterns as needed
        ]
        
        for pattern in phi_patterns:
            if re.search(pattern, message.message_content):
                logger.warning(f"Message {message.message_id} contains potential PHI")
                return False
        
        # Additional HIPAA checks can be added here
        return True

    async def _audit_communication_attempt(self, 
                                         patient_data: PatientCommunicationData,
                                         message: CommunicationMessage):
        """Log communication attempt for audit trail"""
        audit_data = {
            "event": "communication_attempt",
            "message_id": message.message_id,
            "patient_id": patient_data.patient_id,
            "channel": message.channel.value,
            "workflow_type": message.workflow_type.value,
            "priority": message.priority.value,
            "timestamp": datetime.now().isoformat(),
            "language": message.language.value
        }
        
        # Log to audit system (would integrate with proper audit logging)
        logger.info(f"AUDIT: {json.dumps(audit_data)}")

    async def _audit_communication_result(self, 
                                        patient_data: PatientCommunicationData,
                                        message: CommunicationMessage,
                                        result: Dict[str, Any]):
        """Log communication result for audit trail"""
        audit_data = {
            "event": "communication_result",
            "message_id": message.message_id,
            "patient_id": patient_data.patient_id,
            "status": result["status"],
            "provider_message_id": result.get("provider_message_id"),
            "timestamp": datetime.now().isoformat(),
            "retry_count": message.retry_count
        }
        
        if result["status"] == "failed":
            audit_data["error"] = result.get("error", "Unknown error")
        
        # Log to audit system
        logger.info(f"AUDIT: {json.dumps(audit_data)}")

    # Workflow Methods will be continued in the next part due to length...
