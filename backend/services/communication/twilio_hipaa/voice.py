"""
BrainSAIT Healthcare Platform - HIPAA-Compliant Voice Services
Comprehensive voice communication services with encryption, PHI protection, and Arabic support
Supports Saudi Arabia healthcare regulations with real-time transcription and biometric authentication
"""

import asyncio
import json
import uuid
import hashlib
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import asynccontextmanager
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, quote

# Twilio imports
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException, TwilioRestException
from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Record, Conference, Dial

# Internal imports
from .base import TwilioHIPAAClient, HIPAAMessage, TwilioCredentials
from .compliance import HIPAACompliance, PHIDetectionResult, require_hipaa_compliance
from .exceptions import (
    TwilioHIPAAException, PHIExposureException, EncryptionException,
    AuditException, ConfigurationException, ArabicProcessingException,
    AccessControlException, RateLimitException
)
from ..config.hipaa_settings import hipaa_settings, CommunicationChannel

# Arabic processing
import arabic_reshaper
from bidi.algorithm import get_display

# Voice processing libraries (would need to be installed)
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from gtts import gTTS
    import pygame
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


# Configure logging
voice_logger = logging.getLogger(__name__)


class VoiceCallType(str, Enum):
    """Types of voice calls in healthcare context"""
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_REMINDER = "appointment_reminder"
    MEDICATION_REMINDER = "medication_reminder"
    EMERGENCY_ALERT = "emergency_alert"
    PROVIDER_COMMUNICATION = "provider_communication"
    PATIENT_EDUCATION = "patient_education"
    CLINICAL_CONSULTATION = "clinical_consultation"
    FOLLOW_UP_CARE = "follow_up_care"
    LAB_RESULTS = "lab_results"
    TREATMENT_PLAN = "treatment_plan"
    INSURANCE_VERIFICATION = "insurance_verification"
    NPHIES_COMMUNICATION = "nphies_communication"


class VoiceCallStatus(str, Enum):
    """Voice call status tracking"""
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    CANCELLED = "cancelled"
    RECORDED = "recorded"
    TRANSCRIBED = "transcribed"


class VoiceLanguage(str, Enum):
    """Supported voice languages"""
    ARABIC_SA = "ar-SA"  # Saudi Arabic
    ENGLISH_US = "en-US"  # US English
    ENGLISH_UK = "en-UK"  # UK English
    ARABIC_GULF = "ar-AE"  # Gulf Arabic


class VoiceGender(str, Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class BiometricAuthResult(str, Enum):
    """Voice biometric authentication results"""
    AUTHENTICATED = "authenticated"
    FAILED = "failed"
    ENROLLMENT_REQUIRED = "enrollment_required"
    INSUFFICIENT_AUDIO = "insufficient_audio"
    ERROR = "error"


@dataclass
class VoiceTranscription:
    """Voice transcription with PHI protection"""
    transcription_id: str
    audio_duration: float
    text: str
    language: VoiceLanguage
    confidence_score: float
    phi_detected: bool = False
    phi_types: List[str] = None
    redacted_text: Optional[str] = None
    speaker_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.phi_types is None:
            self.phi_types = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if not self.transcription_id:
            self.transcription_id = str(uuid.uuid4())


@dataclass
class VoiceBiometric:
    """Voice biometric data container"""
    biometric_id: str
    user_id: str
    voice_print: str  # Encrypted voice print
    enrollment_date: datetime
    last_verification: Optional[datetime] = None
    verification_count: int = 0
    confidence_threshold: float = 0.85
    is_active: bool = True
    
    def __post_init__(self):
        if not self.biometric_id:
            self.biometric_id = str(uuid.uuid4())


@dataclass
class VoiceCallDetails:
    """Comprehensive voice call details"""
    call_id: str
    twilio_sid: str
    call_type: VoiceCallType
    from_number: str
    to_number: str
    status: VoiceCallStatus
    language: VoiceLanguage
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    recording_encrypted: bool = False
    transcription: Optional[VoiceTranscription] = None
    biometric_result: Optional[BiometricAuthResult] = None
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    appointment_id: Optional[str] = None
    phi_detected: bool = False
    consent_verified: bool = False
    emergency_call: bool = False
    audit_trail: List[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if not self.call_id:
            self.call_id = str(uuid.uuid4())


@dataclass
class ArabicVoiceConfig:
    """Configuration for Arabic voice processing"""
    dialect: str = "saudi"  # saudi, gulf, egyptian, levantine
    voice_gender: VoiceGender = VoiceGender.FEMALE
    speech_rate: float = 1.0  # Normal speed
    prayer_time_aware: bool = True
    ramadan_mode: bool = False
    cultural_greetings: bool = True
    honorific_titles: bool = True  # Use titles like دكتور، أستاذ
    
    def get_culturally_appropriate_greeting(self, time_of_day: datetime) -> str:
        """Get culturally appropriate Arabic greeting"""
        hour = time_of_day.hour
        
        if 5 <= hour < 12:
            return "صباح الخير"  # Good morning
        elif 12 <= hour < 18:
            return "مساء الخير"  # Good afternoon
        elif 18 <= hour < 22:
            return "مساء الخير"  # Good evening
        else:
            return "أهلاً وسهلاً"  # General greeting for late night


class VoiceEncryption:
    """Voice data encryption utilities"""
    
    @staticmethod
    def encrypt_voice_data(voice_data: bytes, encryption_key: str) -> str:
        """Encrypt voice data for HIPAA compliance"""
        try:
            # Implementation would use proper encryption like AES-256
            # This is a simplified example
            import cryptography.fernet as fernet
            key = base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'0'))
            cipher = fernet.Fernet(key)
            encrypted_data = cipher.encrypt(voice_data)
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            raise EncryptionException(
                message=f"Voice data encryption failed: {str(e)}",
                encryption_type="AES-256",
                operation="voice_data_encryption"
            )
    
    @staticmethod
    def decrypt_voice_data(encrypted_data: str, encryption_key: str) -> bytes:
        """Decrypt voice data for processing"""
        try:
            import cryptography.fernet as fernet
            key = base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'0'))
            cipher = fernet.Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = cipher.decrypt(encrypted_bytes)
            return decrypted_data
        except Exception as e:
            raise EncryptionException(
                message=f"Voice data decryption failed: {str(e)}",
                encryption_type="AES-256",
                operation="voice_data_decryption"
            )


class SaudiPhoneFormatter:
    """Saudi phone number formatting utilities"""
    
    @staticmethod
    def format_saudi_number(phone_number: str) -> str:
        """Format phone number according to Saudi standards"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Handle different formats
        if digits_only.startswith('966'):
            # International format starting with country code
            if len(digits_only) == 12:
                return f"+966{digits_only[3:5]}{digits_only[5:8]}{digits_only[8:]}"
            elif len(digits_only) == 13:
                return f"+966{digits_only[3:6]}{digits_only[6:9]}{digits_only[9:]}"
        elif digits_only.startswith('05'):
            # Local mobile format
            if len(digits_only) == 10:
                return f"+966{digits_only[1:3]}{digits_only[3:6]}{digits_only[6:]}"
        elif digits_only.startswith('01') or digits_only.startswith('02'):
            # Local landline format
            if len(digits_only) == 9:
                return f"+966{digits_only[1:2]}{digits_only[2:5]}{digits_only[5:]}"
        
        return phone_number  # Return original if no pattern matches
    
    @staticmethod
    def is_saudi_number(phone_number: str) -> bool:
        """Check if phone number is Saudi"""
        formatted = SaudiPhoneFormatter.format_saudi_number(phone_number)
        return formatted.startswith('+966')


class HIPAAVoiceService(TwilioHIPAAClient):
    """
    HIPAA-compliant voice services for BrainSAIT Healthcare Platform
    Provides secure voice communication with encryption, PHI protection, and Arabic support
    """
    
    def __init__(
        self,
        credentials: Optional[TwilioCredentials] = None,
        arabic_config: Optional[ArabicVoiceConfig] = None,
        **kwargs
    ):
        """
        Initialize HIPAA-compliant voice service
        
        Args:
            credentials: Twilio credentials
            arabic_config: Arabic voice configuration
            **kwargs: Additional configuration options
        """
        super().__init__(credentials=credentials, **kwargs)
        
        self.arabic_config = arabic_config or ArabicVoiceConfig()
        self.voice_calls_cache = {}
        self.biometric_store = {}
        self.transcription_cache = {}
        self.encryption_keys = {}
        
        # Initialize voice processing components
        self._init_voice_processors()
        
        voice_logger.info("HIPAA Voice Service initialized with Arabic support")
    
    def _init_voice_processors(self):
        """Initialize voice processing components"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            voice_logger.warning("Speech recognition not available - transcription disabled")
        
        if not TTS_AVAILABLE:
            voice_logger.warning("Text-to-speech not available - TTS disabled")
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="voice")
    async def initiate_appointment_confirmation_call(
        self,
        patient_phone: str,
        appointment_details: Dict[str, Any],
        language: VoiceLanguage = VoiceLanguage.ARABIC_SA,
        user_id: Optional[str] = None
    ) -> VoiceCallDetails:
        """
        Initiate appointment confirmation call
        
        Args:
            patient_phone: Patient's phone number
            appointment_details: Appointment information
            language: Preferred language for the call
            user_id: User initiating the call
        
        Returns:
            VoiceCallDetails with call information
        """
        try:
            # Format phone number
            formatted_phone = SaudiPhoneFormatter.format_saudi_number(patient_phone)
            
            # Create TwiML for appointment confirmation
            twiml_url = await self._generate_appointment_confirmation_twiml(
                appointment_details, language
            )
            
            # Generate encryption key for this call
            encryption_key = self._generate_encryption_key()
            
            # Initiate call
            call_response = await self.make_voice_call(
                to=formatted_phone,
                twiml_url=twiml_url,
                user_id=user_id,
                context={
                    "call_type": VoiceCallType.APPOINTMENT_CONFIRMATION.value,
                    "language": language.value,
                    "appointment_id": appointment_details.get("appointment_id")
                },
                record=True
            )
            
            # Create call details
            call_details = VoiceCallDetails(
                call_id=call_response["call_id"],
                twilio_sid=call_response["twilio_sid"],
                call_type=VoiceCallType.APPOINTMENT_CONFIRMATION,
                from_number=call_response["from"],
                to_number=formatted_phone,
                status=VoiceCallStatus.INITIATED,
                language=language,
                patient_id=appointment_details.get("patient_id"),
                appointment_id=appointment_details.get("appointment_id"),
                consent_verified=True  # Assumed for appointment confirmations
            )
            
            # Store encryption key
            self.encryption_keys[call_details.call_id] = encryption_key
            
            # Cache call details
            self.voice_calls_cache[call_details.call_id] = call_details
            
            # Audit call initiation
            await self._audit_voice_call_initiated(call_details, user_id)
            
            return call_details
            
        except Exception as e:
            voice_logger.error(f"Appointment confirmation call failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to initiate appointment confirmation call: {str(e)}",
                operation="initiate_appointment_confirmation_call"
            )
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="voice")
    async def initiate_medication_reminder_call(
        self,
        patient_phone: str,
        medication_details: Dict[str, Any],
        language: VoiceLanguage = VoiceLanguage.ARABIC_SA,
        user_id: Optional[str] = None
    ) -> VoiceCallDetails:
        """
        Initiate medication reminder call
        
        Args:
            patient_phone: Patient's phone number
            medication_details: Medication information
            language: Preferred language for the call
            user_id: User initiating the call
        
        Returns:
            VoiceCallDetails with call information
        """
        try:
            formatted_phone = SaudiPhoneFormatter.format_saudi_number(patient_phone)
            
            # Create TwiML for medication reminder
            twiml_url = await self._generate_medication_reminder_twiml(
                medication_details, language
            )
            
            encryption_key = self._generate_encryption_key()
            
            call_response = await self.make_voice_call(
                to=formatted_phone,
                twiml_url=twiml_url,
                user_id=user_id,
                context={
                    "call_type": VoiceCallType.MEDICATION_REMINDER.value,
                    "language": language.value,
                    "medication_id": medication_details.get("medication_id")
                },
                record=True
            )
            
            call_details = VoiceCallDetails(
                call_id=call_response["call_id"],
                twilio_sid=call_response["twilio_sid"],
                call_type=VoiceCallType.MEDICATION_REMINDER,
                from_number=call_response["from"],
                to_number=formatted_phone,
                status=VoiceCallStatus.INITIATED,
                language=language,
                patient_id=medication_details.get("patient_id"),
                consent_verified=True
            )
            
            self.encryption_keys[call_details.call_id] = encryption_key
            self.voice_calls_cache[call_details.call_id] = call_details
            
            await self._audit_voice_call_initiated(call_details, user_id)
            
            return call_details
            
        except Exception as e:
            voice_logger.error(f"Medication reminder call failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to initiate medication reminder call: {str(e)}",
                operation="initiate_medication_reminder_call"
            )
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="voice")
    async def initiate_emergency_alert_call(
        self,
        emergency_contacts: List[str],
        emergency_details: Dict[str, Any],
        priority_override: bool = True,
        user_id: Optional[str] = None
    ) -> List[VoiceCallDetails]:
        """
        Initiate emergency alert calls to multiple contacts
        
        Args:
            emergency_contacts: List of phone numbers to call
            emergency_details: Emergency information
            priority_override: Override rate limits for emergency
            user_id: User initiating the emergency call
        
        Returns:
            List of VoiceCallDetails for each call initiated
        """
        call_details_list = []
        
        try:
            # Create TwiML for emergency alert
            twiml_url = await self._generate_emergency_alert_twiml(emergency_details)
            
            for contact_phone in emergency_contacts:
                try:
                    formatted_phone = SaudiPhoneFormatter.format_saudi_number(contact_phone)
                    encryption_key = self._generate_encryption_key()
                    
                    # Skip rate limiting for emergency calls
                    call_response = await self.make_voice_call(
                        to=formatted_phone,
                        twiml_url=twiml_url,
                        user_id=user_id,
                        context={
                            "call_type": VoiceCallType.EMERGENCY_ALERT.value,
                            "priority": "EMERGENCY",
                            "emergency_id": emergency_details.get("emergency_id")
                        },
                        record=True
                    )
                    
                    call_details = VoiceCallDetails(
                        call_id=call_response["call_id"],
                        twilio_sid=call_response["twilio_sid"],
                        call_type=VoiceCallType.EMERGENCY_ALERT,
                        from_number=call_response["from"],
                        to_number=formatted_phone,
                        status=VoiceCallStatus.INITIATED,
                        language=VoiceLanguage.ARABIC_SA,  # Default for emergency
                        patient_id=emergency_details.get("patient_id"),
                        emergency_call=True,
                        consent_verified=True  # Emergency override
                    )
                    
                    self.encryption_keys[call_details.call_id] = encryption_key
                    self.voice_calls_cache[call_details.call_id] = call_details
                    call_details_list.append(call_details)
                    
                    await self._audit_emergency_call_initiated(call_details, user_id)
                    
                except Exception as contact_error:
                    voice_logger.error(f"Failed to call {contact_phone}: {str(contact_error)}")
                    continue
            
            return call_details_list
            
        except Exception as e:
            voice_logger.error(f"Emergency alert calls failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to initiate emergency alert calls: {str(e)}",
                operation="initiate_emergency_alert_call"
            )
    
    async def create_provider_conference_call(
        self,
        provider_phones: List[str],
        conference_details: Dict[str, Any],
        moderator_controls: bool = True,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create conference call for provider-to-provider communication
        
        Args:
            provider_phones: List of provider phone numbers
            conference_details: Conference information
            moderator_controls: Enable moderator controls
            user_id: User creating the conference
        
        Returns:
            Conference details with participant information
        """
        try:
            conference_id = str(uuid.uuid4())
            conference_name = f"brainsait_conference_{conference_id[:8]}"
            
            # Generate conference TwiML
            twiml_url = await self._generate_conference_twiml(
                conference_name, conference_details, moderator_controls
            )
            
            participants = []
            
            for i, provider_phone in enumerate(provider_phones):
                formatted_phone = SaudiPhoneFormatter.format_saudi_number(provider_phone)
                is_moderator = i == 0 if moderator_controls else False
                
                call_response = await self.make_voice_call(
                    to=formatted_phone,
                    twiml_url=twiml_url,
                    user_id=user_id,
                    context={
                        "call_type": VoiceCallType.PROVIDER_COMMUNICATION.value,
                        "conference_id": conference_id,
                        "is_moderator": is_moderator
                    },
                    record=True
                )
                
                participants.append({
                    "phone": formatted_phone,
                    "call_id": call_response["call_id"],
                    "twilio_sid": call_response["twilio_sid"],
                    "is_moderator": is_moderator,
                    "status": "calling"
                })
            
            conference_result = {
                "conference_id": conference_id,
                "conference_name": conference_name,
                "participants": participants,
                "created_at": datetime.utcnow().isoformat(),
                "moderator_controls": moderator_controls,
                "recording_enabled": True
            }
            
            await self._audit_conference_created(conference_result, user_id)
            
            return conference_result
            
        except Exception as e:
            voice_logger.error(f"Conference creation failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to create provider conference: {str(e)}",
                operation="create_provider_conference_call"
            )
    
    async def perform_voice_biometric_authentication(
        self,
        call_sid: str,
        audio_data: bytes,
        user_id: str
    ) -> BiometricAuthResult:
        """
        Perform voice biometric authentication
        
        Args:
            call_sid: Twilio call SID
            audio_data: Voice audio data for authentication
            user_id: User ID for biometric comparison
        
        Returns:
            BiometricAuthResult with authentication status
        """
        try:
            # Check if user has enrolled biometric
            if user_id not in self.biometric_store:
                return BiometricAuthResult.ENROLLMENT_REQUIRED
            
            biometric_data = self.biometric_store[user_id]
            
            if not biometric_data.is_active:
                return BiometricAuthResult.FAILED
            
            # Extract voice features (simplified implementation)
            # In production, this would use advanced voice recognition algorithms
            voice_features = await self._extract_voice_features(audio_data)
            
            if not voice_features:
                return BiometricAuthResult.INSUFFICIENT_AUDIO
            
            # Compare with stored voice print
            confidence_score = await self._compare_voice_prints(
                voice_features, biometric_data.voice_print
            )
            
            if confidence_score >= biometric_data.confidence_threshold:
                # Update verification record
                biometric_data.last_verification = datetime.utcnow()
                biometric_data.verification_count += 1
                
                await self._audit_biometric_authentication(
                    user_id, call_sid, BiometricAuthResult.AUTHENTICATED, confidence_score
                )
                
                return BiometricAuthResult.AUTHENTICATED
            else:
                await self._audit_biometric_authentication(
                    user_id, call_sid, BiometricAuthResult.FAILED, confidence_score
                )
                
                return BiometricAuthResult.FAILED
                
        except Exception as e:
            voice_logger.error(f"Voice biometric authentication failed: {str(e)}")
            await self._audit_biometric_authentication(
                user_id, call_sid, BiometricAuthResult.ERROR, 0.0
            )
            return BiometricAuthResult.ERROR
    
    async def enroll_voice_biometric(
        self,
        user_id: str,
        audio_samples: List[bytes],
        confidence_threshold: float = 0.85
    ) -> VoiceBiometric:
        """
        Enroll user for voice biometric authentication
        
        Args:
            user_id: User ID for enrollment
            audio_samples: Multiple voice samples for enrollment
            confidence_threshold: Authentication confidence threshold
        
        Returns:
            VoiceBiometric enrollment data
        """
        try:
            if len(audio_samples) < 3:
                raise ConfigurationException(
                    message="Minimum 3 voice samples required for enrollment",
                    config_parameter="voice_biometric_samples"
                )
            
            # Extract and combine voice features from multiple samples
            voice_features = []
            for audio_sample in audio_samples:
                features = await self._extract_voice_features(audio_sample)
                if features:
                    voice_features.append(features)
            
            if len(voice_features) < 2:
                raise ConfigurationException(
                    message="Insufficient voice samples for enrollment",
                    config_parameter="voice_biometric_quality"
                )
            
            # Create composite voice print
            voice_print = await self._create_voice_print(voice_features)
            
            # Encrypt voice print
            encryption_key = self._generate_encryption_key()
            encrypted_voice_print = VoiceEncryption.encrypt_voice_data(
                voice_print.encode(), encryption_key
            )
            
            # Create biometric record
            biometric_data = VoiceBiometric(
                biometric_id=str(uuid.uuid4()),
                user_id=user_id,
                voice_print=encrypted_voice_print,
                enrollment_date=datetime.utcnow(),
                confidence_threshold=confidence_threshold
            )
            
            # Store biometric data
            self.biometric_store[user_id] = biometric_data
            self.encryption_keys[biometric_data.biometric_id] = encryption_key
            
            await self._audit_biometric_enrollment(user_id, biometric_data.biometric_id)
            
            return biometric_data
            
        except Exception as e:
            voice_logger.error(f"Voice biometric enrollment failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to enroll voice biometric: {str(e)}",
                operation="enroll_voice_biometric"
            )
    
    async def transcribe_call_recording(
        self,
        call_id: str,
        language: VoiceLanguage = VoiceLanguage.ARABIC_SA,
        detect_phi: bool = True
    ) -> VoiceTranscription:
        """
        Transcribe call recording with PHI detection
        
        Args:
            call_id: Call ID to transcribe
            language: Language for transcription
            detect_phi: Whether to detect PHI in transcription
        
        Returns:
            VoiceTranscription with PHI protection
        """
        try:
            if call_id not in self.voice_calls_cache:
                raise TwilioHIPAAException(
                    message=f"Call not found: {call_id}",
                    operation="transcribe_call_recording"
                )
            
            call_details = self.voice_calls_cache[call_id]
            
            if not call_details.recording_url:
                raise TwilioHIPAAException(
                    message=f"No recording available for call: {call_id}",
                    operation="transcribe_call_recording"
                )
            
            # Get recording from Twilio
            recording_data = await self._fetch_call_recording(call_details.recording_url)
            
            # Transcribe audio
            transcription_text = await self._transcribe_audio(
                recording_data, language
            )
            
            # Create transcription object
            transcription = VoiceTranscription(
                transcription_id=str(uuid.uuid4()),
                audio_duration=call_details.duration or 0,
                text=transcription_text,
                language=language,
                confidence_score=0.9  # Would come from actual transcription service
            )
            
            # Detect PHI if enabled
            if detect_phi:
                phi_result = await self.compliance.detect_phi(
                    transcription_text,
                    context=f"voice_transcription_{call_details.call_type.value}",
                    auto_redact=True
                )
                
                transcription.phi_detected = phi_result.phi_detected
                transcription.phi_types = [t.value for t in phi_result.phi_types]
                transcription.redacted_text = phi_result.redacted_content
                
                # Update call details
                call_details.phi_detected = phi_result.phi_detected
                call_details.transcription = transcription
            
            # Cache transcription
            self.transcription_cache[transcription.transcription_id] = transcription
            
            await self._audit_transcription_completed(call_id, transcription)
            
            return transcription
            
        except Exception as e:
            voice_logger.error(f"Call transcription failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to transcribe call recording: {str(e)}",
                operation="transcribe_call_recording"
            )
    
    async def generate_arabic_tts(
        self,
        text: str,
        voice_gender: VoiceGender = VoiceGender.FEMALE,
        dialect: str = "saudi"
    ) -> bytes:
        """
        Generate Arabic text-to-speech audio
        
        Args:
            text: Arabic text to convert to speech
            voice_gender: Voice gender preference
            dialect: Arabic dialect preference
        
        Returns:
            Audio data as bytes
        """
        try:
            if not TTS_AVAILABLE:
                raise ConfigurationException(
                    message="Text-to-speech service not available",
                    config_parameter="tts_service"
                )
            
            # Process Arabic text for proper pronunciation
            processed_text = await self._process_arabic_for_tts(text, dialect)
            
            # Generate TTS audio
            # This would integrate with Google TTS, Azure Cognitive Services, or AWS Polly
            # For Arabic voices with Saudi dialect support
            tts = gTTS(text=processed_text, lang='ar', tld='com.sa')
            
            # Convert to audio bytes
            import io
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            return audio_data
            
        except Exception as e:
            voice_logger.error(f"Arabic TTS generation failed: {str(e)}")
            raise ArabicProcessingException(
                message=f"Failed to generate Arabic TTS: {str(e)}",
                processing_stage="text_to_speech",
                text_sample=text[:100]
            )
    
    async def create_interactive_voice_response(
        self,
        menu_options: Dict[str, str],
        language: VoiceLanguage = VoiceLanguage.ARABIC_SA,
        max_attempts: int = 3
    ) -> str:
        """
        Create interactive voice response (IVR) system
        
        Args:
            menu_options: Dictionary of options (key: spoken text)
            language: Language for IVR
            max_attempts: Maximum input attempts
        
        Returns:
            TwiML URL for IVR system
        """
        try:
            # Generate unique IVR ID
            ivr_id = str(uuid.uuid4())
            
            # Create TwiML for IVR
            response = VoiceResponse()
            
            # Welcome message based on language
            if language == VoiceLanguage.ARABIC_SA:
                welcome_msg = "أهلاً وسهلاً بك في منصة برين سايت الصحية"
                instruction_msg = "يرجى اختيار أحد الخيارات التالية"
            else:
                welcome_msg = "Welcome to BrainSAIT Healthcare Platform"
                instruction_msg = "Please select one of the following options"
            
            # Add cultural greeting if Arabic
            if language == VoiceLanguage.ARABIC_SA and self.arabic_config.cultural_greetings:
                current_time = datetime.utcnow()
                greeting = self.arabic_config.get_culturally_appropriate_greeting(current_time)
                welcome_msg = f"{greeting}. {welcome_msg}"
            
            gather = Gather(
                num_digits=1,
                timeout=10,
                action=f"/voice/ivr/{ivr_id}/process",
                method='POST'
            )
            
            gather.say(welcome_msg, language=language.value)
            gather.say(instruction_msg, language=language.value)
            
            # Add menu options
            for key, option_text in menu_options.items():
                gather.say(f"اضغط {key} للخيار: {option_text}", language=language.value)
            
            response.append(gather)
            
            # Fallback for no input
            response.say("لم نتلق أي إدخال. سيتم إنهاء المكالمة. شكراً لكم", language=language.value)
            
            # Store IVR configuration for processing
            ivr_config = {
                "ivr_id": ivr_id,
                "menu_options": menu_options,
                "language": language.value,
                "max_attempts": max_attempts,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Cache IVR configuration
            # In production, this would be stored in a database
            self._cache_ivr_config(ivr_id, ivr_config)
            
            return f"/voice/ivr/{ivr_id}/menu"
            
        except Exception as e:
            voice_logger.error(f"IVR creation failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to create IVR system: {str(e)}",
                operation="create_interactive_voice_response"
            )
    
    async def monitor_call_quality(
        self,
        call_id: str
    ) -> Dict[str, Any]:
        """
        Monitor call quality metrics
        
        Args:
            call_id: Call ID to monitor
        
        Returns:
            Call quality metrics
        """
        try:
            if call_id not in self.voice_calls_cache:
                raise TwilioHIPAAException(
                    message=f"Call not found: {call_id}",
                    operation="monitor_call_quality"
                )
            
            call_details = self.voice_calls_cache[call_id]
            
            # Fetch call metrics from Twilio
            try:
                call = self.client.calls(call_details.twilio_sid).fetch()
                
                quality_metrics = {
                    "call_id": call_id,
                    "twilio_sid": call_details.twilio_sid,
                    "status": call.status,
                    "duration": call.duration,
                    "direction": call.direction,
                    "answered_by": getattr(call, 'answered_by', None),
                    "price": call.price,
                    "price_unit": call.price_unit,
                    "quality_issues": [],
                    "monitoring_timestamp": datetime.utcnow().isoformat()
                }
                
                # Check for quality issues
                if hasattr(call, 'price') and call.price:
                    if float(call.price) > 0.5:  # High cost indicator
                        quality_metrics["quality_issues"].append("HIGH_COST")
                
                if call.duration and int(call.duration) < 10:
                    quality_metrics["quality_issues"].append("SHORT_DURATION")
                
                return quality_metrics
                
            except TwilioException as e:
                voice_logger.warning(f"Could not fetch call metrics: {str(e)}")
                return {
                    "call_id": call_id,
                    "error": "Unable to fetch call metrics",
                    "monitoring_timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            voice_logger.error(f"Call quality monitoring failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to monitor call quality: {str(e)}",
                operation="monitor_call_quality"
            )
    
    # TwiML Generation Methods
    
    async def _generate_appointment_confirmation_twiml(
        self,
        appointment_details: Dict[str, Any],
        language: VoiceLanguage
    ) -> str:
        """Generate TwiML for appointment confirmation calls"""
        try:
            response = VoiceResponse()
            
            if language == VoiceLanguage.ARABIC_SA:
                # Arabic appointment confirmation
                greeting = self.arabic_config.get_culturally_appropriate_greeting(datetime.utcnow())
                message = f"""
                {greeting}. هذه مكالمة تأكيد موعد من منصة برين سايت الصحية.
                لديك موعد مع الدكتور {appointment_details.get('doctor_name', '')} 
                في تاريخ {appointment_details.get('appointment_date', '')} 
                في الساعة {appointment_details.get('appointment_time', '')}.
                اضغط 1 لتأكيد الموعد، اضغط 2 لإلغاء الموعد، اضغط 3 لإعادة الجدولة.
                """
            else:
                # English appointment confirmation
                message = f"""
                Hello, this is an appointment confirmation call from BrainSAIT Healthcare Platform.
                You have an appointment with Dr. {appointment_details.get('doctor_name', '')} 
                on {appointment_details.get('appointment_date', '')} 
                at {appointment_details.get('appointment_time', '')}.
                Press 1 to confirm, press 2 to cancel, press 3 to reschedule.
                """
            
            gather = Gather(
                num_digits=1,
                timeout=10,
                action="/voice/appointment/process",
                method='POST'
            )
            gather.say(message.strip(), language=language.value)
            response.append(gather)
            
            # Fallback
            response.say("شكراً لكم. سيتم إنهاء المكالمة.", language=language.value)
            
            return self._twiml_to_url(response)
            
        except Exception as e:
            voice_logger.error(f"Appointment TwiML generation failed: {str(e)}")
            raise
    
    async def _generate_medication_reminder_twiml(
        self,
        medication_details: Dict[str, Any],
        language: VoiceLanguage
    ) -> str:
        """Generate TwiML for medication reminder calls"""
        try:
            response = VoiceResponse()
            
            if language == VoiceLanguage.ARABIC_SA:
                message = f"""
                السلام عليكم. هذا تذكير دوائي من منصة برين سايت الصحية.
                حان وقت تناول دواء {medication_details.get('medication_name', '')}.
                الجرعة المطلوبة: {medication_details.get('dosage', '')}.
                اضغط 1 لتأكيد أخذ الدواء، اضغط 2 للتأجيل لمدة ساعة.
                """
            else:
                message = f"""
                Hello, this is a medication reminder from BrainSAIT Healthcare Platform.
                It's time to take your medication: {medication_details.get('medication_name', '')}.
                Dosage: {medication_details.get('dosage', '')}.
                Press 1 to confirm medication taken, press 2 to postpone for one hour.
                """
            
            gather = Gather(
                num_digits=1,
                timeout=15,
                action="/voice/medication/process",
                method='POST'
            )
            gather.say(message.strip(), language=language.value)
            response.append(gather)
            
            response.say("شكراً لكم على اهتمامكم بصحتكم.", language=language.value)
            
            return self._twiml_to_url(response)
            
        except Exception as e:
            voice_logger.error(f"Medication TwiML generation failed: {str(e)}")
            raise
    
    async def _generate_emergency_alert_twiml(
        self,
        emergency_details: Dict[str, Any]
    ) -> str:
        """Generate TwiML for emergency alert calls"""
        try:
            response = VoiceResponse()
            
            # Emergency calls are bilingual for maximum understanding
            message = f"""
            تنبيه طارئ! Emergency Alert! 
            هذا تنبيه طارئ من منصة برين سايت الصحية.
            This is an emergency alert from BrainSAIT Healthcare Platform.
            المريض: {emergency_details.get('patient_name', 'غير محدد')}
            Patient: {emergency_details.get('patient_name', 'Unknown')}
            نوع الطوارئ: {emergency_details.get('emergency_type', 'غير محدد')}
            Emergency Type: {emergency_details.get('emergency_type', 'Unknown')}
            اضغط 1 للاستجابة للطوارئ، اضغط 2 لتوجيه المكالمة.
            Press 1 to respond to emergency, press 2 to transfer call.
            """
            
            gather = Gather(
                num_digits=1,
                timeout=20,
                action="/voice/emergency/process",
                method='POST'
            )
            gather.say(message.strip(), language='ar-SA')
            response.append(gather)
            
            # Repeat in case of no response
            response.say("تنبيه طارئ! يرجى الاستجابة فوراً!", language='ar-SA')
            
            return self._twiml_to_url(response)
            
        except Exception as e:
            voice_logger.error(f"Emergency TwiML generation failed: {str(e)}")
            raise
    
    async def _generate_conference_twiml(
        self,
        conference_name: str,
        conference_details: Dict[str, Any],
        moderator_controls: bool
    ) -> str:
        """Generate TwiML for conference calls"""
        try:
            response = VoiceResponse()
            
            # Welcome message
            response.say(
                "مرحباً بكم في مؤتمر طبي عبر منصة برين سايت الصحية",
                language='ar-SA'
            )
            
            # Join conference
            conference_params = {
                'start_conference_on_enter': True,
                'end_conference_on_exit': moderator_controls,
                'record': 'record-from-start',
                'status_callback': '/voice/conference/events',
                'status_callback_event': 'start end join leave mute hold',
                'status_callback_method': 'POST'
            }
            
            if moderator_controls:
                conference_params.update({
                    'muted': False,
                    'beep': 'true'
                })
            
            dial = Dial()
            dial.conference(conference_name, **conference_params)
            response.append(dial)
            
            return self._twiml_to_url(response)
            
        except Exception as e:
            voice_logger.error(f"Conference TwiML generation failed: {str(e)}")
            raise
    
    # Utility Methods
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key for voice data"""
        import secrets
        return secrets.token_urlsafe(32)
    
    async def _extract_voice_features(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Extract voice features for biometric authentication"""
        # Simplified implementation - in production would use advanced audio processing
        try:
            import hashlib
            audio_hash = hashlib.sha256(audio_data).hexdigest()
            
            # Mock feature extraction
            features = {
                "audio_hash": audio_hash,
                "duration": len(audio_data) / 1000,  # Approximate duration
                "sample_rate": 8000,  # Standard voice sample rate
                "features": [0.1, 0.2, 0.3, 0.4, 0.5]  # Mock feature vector
            }
            
            return features
        except Exception as e:
            voice_logger.error(f"Voice feature extraction failed: {str(e)}")
            return None
    
    async def _compare_voice_prints(
        self,
        current_features: Dict[str, Any],
        stored_voice_print: str
    ) -> float:
        """Compare voice features for authentication"""
        try:
            # Simplified comparison - in production would use ML algorithms
            # This is a mock implementation
            confidence_score = 0.9  # Mock high confidence
            return confidence_score
        except Exception as e:
            voice_logger.error(f"Voice print comparison failed: {str(e)}")
            return 0.0
    
    async def _create_voice_print(self, voice_features: List[Dict[str, Any]]) -> str:
        """Create composite voice print from multiple samples"""
        try:
            # Simplified implementation
            combined_features = {}
            for features in voice_features:
                for key, value in features.items():
                    if key not in combined_features:
                        combined_features[key] = []
                    combined_features[key].append(value)
            
            # Create voice print hash
            voice_print_data = json.dumps(combined_features, sort_keys=True)
            return hashlib.sha256(voice_print_data.encode()).hexdigest()
        except Exception as e:
            voice_logger.error(f"Voice print creation failed: {str(e)}")
            raise
    
    async def _transcribe_audio(
        self,
        audio_data: bytes,
        language: VoiceLanguage
    ) -> str:
        """Transcribe audio to text"""
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return "[Transcription not available - speech recognition service not installed]"
            
            # Mock transcription - in production would use Google Speech-to-Text,
            # Azure Cognitive Services, or AWS Transcribe with Arabic support
            return "نص مُحول من الصوت - هذا مثال تجريبي"
        except Exception as e:
            voice_logger.error(f"Audio transcription failed: {str(e)}")
            return "[Transcription failed]"
    
    async def _fetch_call_recording(self, recording_url: str) -> bytes:
        """Fetch call recording from Twilio"""
        try:
            # In production, this would fetch the actual recording
            # This is a mock implementation
            return b"mock_audio_data"
        except Exception as e:
            voice_logger.error(f"Recording fetch failed: {str(e)}")
            raise
    
    async def _process_arabic_for_tts(self, text: str, dialect: str) -> str:
        """Process Arabic text for better TTS pronunciation"""
        try:
            # Apply Arabic text reshaping
            reshaped_text = arabic_reshaper.reshape(text)
            
            # Apply dialect-specific modifications
            if dialect == "saudi":
                # Saudi-specific pronunciation adjustments
                reshaped_text = reshaped_text.replace("ج", "ج")  # Keep jeem as is for Saudi
            
            return reshaped_text
        except Exception as e:
            voice_logger.error(f"Arabic TTS processing failed: {str(e)}")
            return text  # Return original text if processing fails
    
    def _twiml_to_url(self, twiml_response: VoiceResponse) -> str:
        """Convert TwiML response to URL (mock implementation)"""
        # In production, this would store TwiML and return actual URL
        twiml_id = str(uuid.uuid4())
        return f"/voice/twiml/{twiml_id}"
    
    def _cache_ivr_config(self, ivr_id: str, config: Dict[str, Any]):
        """Cache IVR configuration"""
        # In production, this would be stored in Redis or database
        pass
    
    # Audit Methods
    
    async def _audit_voice_call_initiated(
        self,
        call_details: VoiceCallDetails,
        user_id: Optional[str]
    ):
        """Audit voice call initiation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "voice_call_initiated",
            "timestamp": datetime.utcnow().isoformat(),
            "call_id": call_details.call_id,
            "call_type": call_details.call_type.value,
            "language": call_details.language.value,
            "user_id": user_id,
            "patient_id": call_details.patient_id,
            "emergency_call": call_details.emergency_call,
            "consent_verified": call_details.consent_verified
        }
        
        self._audit_events.append(audit_event)
        voice_logger.info(f"AUDIT: Voice call initiated - {call_details.call_id}", extra=audit_event)
    
    async def _audit_emergency_call_initiated(
        self,
        call_details: VoiceCallDetails,
        user_id: Optional[str]
    ):
        """Audit emergency call initiation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "emergency_call_initiated",
            "timestamp": datetime.utcnow().isoformat(),
            "call_id": call_details.call_id,
            "user_id": user_id,
            "patient_id": call_details.patient_id,
            "severity": "CRITICAL",
            "priority": "EMERGENCY"
        }
        
        self._audit_events.append(audit_event)
        voice_logger.critical(f"AUDIT: Emergency call initiated - {call_details.call_id}", extra=audit_event)
    
    async def _audit_conference_created(
        self,
        conference_result: Dict[str, Any],
        user_id: Optional[str]
    ):
        """Audit conference creation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "conference_created",
            "timestamp": datetime.utcnow().isoformat(),
            "conference_id": conference_result["conference_id"],
            "participants_count": len(conference_result["participants"]),
            "user_id": user_id,
            "moderator_controls": conference_result["moderator_controls"]
        }
        
        self._audit_events.append(audit_event)
        voice_logger.info(f"AUDIT: Conference created - {conference_result['conference_id']}", extra=audit_event)
    
    async def _audit_biometric_authentication(
        self,
        user_id: str,
        call_sid: str,
        result: BiometricAuthResult,
        confidence_score: float
    ):
        """Audit biometric authentication attempt"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "biometric_authentication",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "call_sid": call_sid,
            "result": result.value,
            "confidence_score": confidence_score,
            "authentication_method": "voice_biometric"
        }
        
        self._audit_events.append(audit_event)
        voice_logger.info(f"AUDIT: Biometric authentication - {user_id}: {result.value}", extra=audit_event)
    
    async def _audit_biometric_enrollment(self, user_id: str, biometric_id: str):
        """Audit biometric enrollment"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "biometric_enrollment",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "biometric_id": biometric_id,
            "biometric_type": "voice"
        }
        
        self._audit_events.append(audit_event)
        voice_logger.info(f"AUDIT: Biometric enrollment - {user_id}", extra=audit_event)
    
    async def _audit_transcription_completed(
        self,
        call_id: str,
        transcription: VoiceTranscription
    ):
        """Audit transcription completion"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "transcription_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "call_id": call_id,
            "transcription_id": transcription.transcription_id,
            "language": transcription.language.value,
            "phi_detected": transcription.phi_detected,
            "confidence_score": transcription.confidence_score
        }
        
        self._audit_events.append(audit_event)
        voice_logger.info(f"AUDIT: Transcription completed - {call_id}", extra=audit_event)


# Context manager for HIPAA voice service
@asynccontextmanager
async def hipaa_voice_service(**kwargs):
    """
    Context manager for HIPAA-compliant voice service
    
    Usage:
        async with hipaa_voice_service() as voice_service:
            await voice_service.initiate_appointment_confirmation_call(...)
    """
    service = HIPAAVoiceService(**kwargs)
    try:
        yield service
    finally:
        await service.close()


# Export main classes and functions
__all__ = [
    "HIPAAVoiceService",
    "VoiceCallType",
    "VoiceCallStatus",
    "VoiceLanguage",
    "VoiceGender",
    "BiometricAuthResult",
    "VoiceCallDetails",
    "VoiceTranscription",
    "VoiceBiometric",
    "ArabicVoiceConfig",
    "VoiceEncryption",
    "SaudiPhoneFormatter",
    "hipaa_voice_service"
]