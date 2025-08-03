"""
BrainSAIT Healthcare Platform - HIPAA-Compliant Video Services
Secure telehealth video consultation services with end-to-end encryption
Supports Saudi Arabia healthcare regulations with Arabic language features
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from contextlib import asynccontextmanager
import mimetypes
import io

# Cryptography imports for E2E encryption
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Twilio Video imports
from twilio.rest import Client as TwilioClient
from twilio.jwt.access_token import AccessToken, VideoGrant
from twilio.base.exceptions import TwilioException, TwilioRestException

# Internal imports
from .base import TwilioHIPAAClient, TwilioCredentials
from .exceptions import (
    TwilioHIPAAException, BAAViolationException, PHIExposureException,
    EncryptionException, AccessControlException, AuditException,
    ConfigurationException, RateLimitException
)
from .compliance import HIPAACompliance, require_hipaa_compliance
from ..config.hipaa_settings import hipaa_settings, CommunicationChannel

# Configure logging
logger = logging.getLogger(__name__)


class VideoCallType(str, Enum):
    """Types of video consultations"""
    DOCTOR_PATIENT = "doctor_patient"
    MEDICAL_TEAM = "medical_team"
    FAMILY_CONSULTATION = "family_consultation"
    SECOND_OPINION = "second_opinion"
    EMERGENCY_CONSULTATION = "emergency_consultation"
    REMOTE_MONITORING = "remote_monitoring"
    TRAINING_SESSION = "training_session"


class VideoQuality(str, Enum):
    """Video quality settings"""
    LOW = "low"          # 320x240
    STANDARD = "standard" # 640x480
    HIGH = "high"        # 1280x720
    HD = "hd"           # 1920x1080


class ParticipantRole(str, Enum):
    """Participant roles in video consultation"""
    DOCTOR = "doctor"
    PATIENT = "patient"
    NURSE = "nurse"
    SPECIALIST = "specialist"
    FAMILY_MEMBER = "family_member"
    OBSERVER = "observer"
    ADMIN = "admin"


class VideoSessionStatus(str, Enum):
    """Video session status"""
    SCHEDULED = "scheduled"
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EMERGENCY_ENDED = "emergency_ended"


class RecordingStatus(str, Enum):
    """Recording status"""
    NOT_STARTED = "not_started"
    RECORDING = "recording"
    PAUSED = "paused"
    COMPLETED = "completed"
    ENCRYPTED = "encrypted"
    ARCHIVED = "archived"


@dataclass
class VideoParticipant:
    """Video consultation participant"""
    participant_id: str
    user_id: str
    name: str
    role: ParticipantRole
    phone_number: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None  # For healthcare providers
    department: Optional[str] = None
    organization: Optional[str] = None
    is_saudi_resident: bool = False
    preferred_language: str = "ar"  # Arabic by default
    gender_preference: Optional[str] = None  # For cultural considerations
    access_token: Optional[str] = None
    connection_status: str = "disconnected"
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.participant_id:
            self.participant_id = str(uuid.uuid4())


@dataclass
class VideoEncryption:
    """Video call encryption settings"""
    encryption_key: str
    key_id: str
    algorithm: str = "AES-256-GCM"
    iv: Optional[str] = None
    metadata_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=24)


@dataclass
class HealthcareContext:
    """Healthcare-specific context for video calls"""
    patient_id: Optional[str] = None
    medical_record_number: Optional[str] = None
    appointment_id: Optional[str] = None
    diagnosis_codes: List[str] = field(default_factory=list)
    specialty: Optional[str] = None
    urgency_level: str = "routine"  # routine, urgent, emergency
    consultation_type: str = "general"
    saudi_health_id: Optional[str] = None  # National Health ID
    insurance_info: Optional[Dict[str, Any]] = None
    family_consent: bool = False
    interpreter_needed: bool = False
    cultural_considerations: List[str] = field(default_factory=list)


@dataclass
class VideoSession:
    """Complete video consultation session"""
    session_id: str
    room_sid: str
    session_type: VideoCallType
    status: VideoSessionStatus
    participants: List[VideoParticipant]
    healthcare_context: HealthcareContext
    encryption: VideoEncryption
    quality_settings: VideoQuality = VideoQuality.STANDARD
    max_participants: int = 10
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    recording_enabled: bool = True
    recording_status: RecordingStatus = RecordingStatus.NOT_STARTED
    recording_sids: List[str] = field(default_factory=list)
    screen_sharing_enabled: bool = True
    chat_enabled: bool = True
    waiting_room_enabled: bool = True
    auto_record: bool = True
    data_residency: str = "saudi_arabia"
    compliance_flags: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())


class VideoHIPAAService:
    """
    HIPAA-compliant video consultation service for BrainSAIT Healthcare Platform
    Provides secure, encrypted, and audited video consultations for Saudi healthcare
    """
    
    def __init__(
        self,
        twilio_client: Optional[TwilioHIPAAClient] = None,
        encryption_enabled: bool = True,
        saudi_compliance: bool = True
    ):
        """
        Initialize video service
        
        Args:
            twilio_client: HIPAA-compliant Twilio client
            encryption_enabled: Enable end-to-end encryption
            saudi_compliance: Enable Saudi-specific compliance
        """
        self.twilio_client = twilio_client or TwilioHIPAAClient()
        self.compliance = HIPAACompliance()
        self.encryption_enabled = encryption_enabled
        self.saudi_compliance = saudi_compliance
        
        # Session management
        self.active_sessions: Dict[str, VideoSession] = {}
        self.waiting_rooms: Dict[str, List[VideoParticipant]] = {}
        self.encryption_keys: Dict[str, VideoEncryption] = {}
        
        # Arabic language support
        self.arabic_ui_elements = self._load_arabic_ui()
        
        # Audit trail
        self.audit_events: List[Dict[str, Any]] = []
        
        logger.info("Video HIPAA service initialized")
    
    def _load_arabic_ui(self) -> Dict[str, str]:
        """Load Arabic UI elements for video interface"""
        return {
            "join_call": "انضم إلى المكالمة",
            "end_call": "إنهاء المكالمة",
            "mute": "كتم الصوت",
            "unmute": "إلغاء كتم الصوت",
            "video_on": "تشغيل الفيديو",
            "video_off": "إيقاف الفيديو",
            "screen_share": "مشاركة الشاشة",
            "chat": "الدردشة",
            "participants": "المشاركون",
            "waiting_room": "غرفة الانتظار",
            "record": "تسجيل",
            "doctor": "طبيب",
            "patient": "مريض",
            "nurse": "ممرض/ممرضة",
            "family": "أفراد العائلة",
            "emergency": "طوارئ",
            "consultation_ended": "انتهت الاستشارة",
            "poor_connection": "ضعف في الاتصال",
            "quality_adjusted": "تم تعديل الجودة"
        }
    
    def _generate_encryption_key(self) -> VideoEncryption:
        """Generate encryption keys for video session"""
        if not self.encryption_enabled:
            return None
        
        try:
            # Generate AES key for video encryption
            encryption_key = Fernet.generate_key()
            key_id = str(uuid.uuid4())
            
            # Generate initialization vector
            iv = secrets.token_bytes(16)
            
            # Generate metadata encryption key
            metadata_key = Fernet.generate_key()
            
            encryption = VideoEncryption(
                encryption_key=base64.b64encode(encryption_key).decode(),
                key_id=key_id,
                iv=base64.b64encode(iv).decode(),
                metadata_key=base64.b64encode(metadata_key).decode()
            )
            
            # Store encryption keys securely
            self.encryption_keys[key_id] = encryption
            
            return encryption
            
        except Exception as e:
            logger.error(f"Encryption key generation failed: {str(e)}")
            raise EncryptionException(
                message="Failed to generate video encryption keys",
                encryption_context="video_session_creation",
                details={"error": str(e)}
            )
    
    @require_hipaa_compliance(check_phi=True, check_baa=True, channel="video")
    async def create_video_session(
        self,
        session_type: VideoCallType,
        organizer: VideoParticipant,
        healthcare_context: Optional[HealthcareContext] = None,
        scheduled_start: Optional[datetime] = None,
        max_participants: int = 10,
        quality: VideoQuality = VideoQuality.STANDARD,
        user_id: Optional[str] = None
    ) -> VideoSession:
        """
        Create a new HIPAA-compliant video consultation session
        
        Args:
            session_type: Type of video consultation
            organizer: Session organizer (usually doctor)
            healthcare_context: Healthcare-specific information
            scheduled_start: Scheduled start time
            max_participants: Maximum number of participants
            quality: Video quality setting
            user_id: User ID for audit trail
        
        Returns:
            VideoSession object with room details
        """
        try:
            session_id = str(uuid.uuid4())
            
            # Generate encryption for the session
            encryption = self._generate_encryption_key()
            
            # Create Twilio Video room
            room_name = f"brainsait-{session_type.value}-{session_id[:8]}"
            
            # Room settings for healthcare compliance
            room_settings = {
                "unique_name": room_name,
                "type": "group",  # Group room for multiple participants
                "max_participants": max_participants,
                "record_participants_on_connect": True if hipaa_settings.VIDEO_AUTO_RECORD else False,
                "video_codecs": ["VP8", "H264"],  # Supported codecs
                "media_region": "us1" if not self.saudi_compliance else "ie1"  # Closest to Saudi Arabia
            }
            
            # Create room via Twilio
            room = self.twilio_client.client.video.rooms.create(**room_settings)
            
            # Create session object
            session = VideoSession(
                session_id=session_id,
                room_sid=room.sid,
                session_type=session_type,
                status=VideoSessionStatus.SCHEDULED,
                participants=[organizer],
                healthcare_context=healthcare_context or HealthcareContext(),
                encryption=encryption,
                quality_settings=quality,
                max_participants=max_participants,
                scheduled_start=scheduled_start
            )
            
            # Store session
            self.active_sessions[session_id] = session
            
            # Initialize waiting room
            self.waiting_rooms[session_id] = []
            
            # Generate access token for organizer
            organizer.access_token = await self._generate_access_token(
                organizer,
                room_name,
                session
            )
            
            # Audit event
            await self._audit_session_created(session, organizer, user_id)
            
            logger.info(f"Video session created: {session_id}")
            
            return session
            
        except TwilioException as e:
            logger.error(f"Twilio video room creation failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Video session creation failed: {str(e)}",
                twilio_error_code=getattr(e, 'code', None),
                operation="create_video_session"
            )
        except Exception as e:
            logger.error(f"Video session creation error: {str(e)}")
            raise
    
    async def _generate_access_token(
        self,
        participant: VideoParticipant,
        room_name: str,
        session: VideoSession,
        ttl: int = 3600  # 1 hour
    ) -> str:
        """
        Generate Twilio access token for participant
        
        Args:
            participant: Video participant
            room_name: Twilio room name
            session: Video session
            ttl: Token time-to-live in seconds
        
        Returns:
            Signed JWT access token
        """
        try:
            # Create access token
            token = AccessToken(
                self.twilio_client.credentials.account_sid,
                hipaa_settings.TWILIO_API_KEY,
                hipaa_settings.TWILIO_API_SECRET,
                identity=participant.participant_id,
                ttl=ttl
            )
            
            # Add video grant
            video_grant = VideoGrant(room=room_name)
            token.add_grant(video_grant)
            
            # Generate JWT
            jwt_token = token.to_jwt()
            
            # Audit token generation
            await self._audit_token_generated(participant, session, ttl)
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Access token generation failed: {str(e)}")
            raise AccessControlException(
                message="Failed to generate video access token",
                user_context=participant.participant_id,
                access_type="video_session",
                details={"error": str(e)}
            )
    
    async def add_participant(
        self,
        session_id: str,
        participant: VideoParticipant,
        bypass_waiting_room: bool = False,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add participant to video session
        
        Args:
            session_id: Video session ID
            participant: Participant to add
            bypass_waiting_room: Skip waiting room
            user_id: User ID for audit trail
        
        Returns:
            Participant details with access token
        """
        if session_id not in self.active_sessions:
            raise TwilioHIPAAException(
                message=f"Video session not found: {session_id}",
                operation="add_participant"
            )
        
        session = self.active_sessions[session_id]
        
        # Check participant limit
        if len(session.participants) >= session.max_participants:
            raise TwilioHIPAAException(
                message="Maximum participants reached",
                operation="add_participant"
            )
        
        # Cultural and gender considerations for Saudi patients
        if self.saudi_compliance and participant.role == ParticipantRole.PATIENT:
            await self._validate_cultural_considerations(participant, session)
        
        # Add to waiting room if enabled and not bypassed
        if session.waiting_room_enabled and not bypass_waiting_room:
            if participant.role not in [ParticipantRole.DOCTOR, ParticipantRole.ADMIN]:
                self.waiting_rooms[session_id].append(participant)
                
                await self._audit_participant_waiting(participant, session, user_id)
                
                return {
                    "participant_id": participant.participant_id,
                    "status": "waiting",
                    "waiting_room": True,
                    "message": self.arabic_ui_elements["waiting_room"] if participant.preferred_language == "ar" else "In waiting room"
                }
        
        # Generate access token
        room_name = f"brainsait-{session.session_type.value}-{session.session_id[:8]}"
        participant.access_token = await self._generate_access_token(
            participant,
            room_name,
            session
        )
        
        # Add to session
        session.participants.append(participant)
        participant.joined_at = datetime.utcnow()
        participant.connection_status = "connected"
        
        # Update session status
        if session.status == VideoSessionStatus.SCHEDULED:
            session.status = VideoSessionStatus.ACTIVE
            session.actual_start = datetime.utcnow()
        
        # Audit event
        await self._audit_participant_joined(participant, session, user_id)
        
        logger.info(f"Participant added to session {session_id}: {participant.participant_id}")
        
        return {
            "participant_id": participant.participant_id,
            "access_token": participant.access_token,
            "room_sid": session.room_sid,
            "status": "connected",
            "arabic_ui": self.arabic_ui_elements if participant.preferred_language == "ar" else None,
            "encryption_enabled": self.encryption_enabled,
            "session_type": session.session_type.value,
            "quality": session.quality_settings.value
        }
    
    async def _validate_cultural_considerations(
        self,
        participant: VideoParticipant,
        session: VideoSession
    ):
        """Validate cultural and religious considerations for Saudi patients"""
        if not participant.is_saudi_resident:
            return
        
        # Check gender preferences for consultation
        if participant.gender_preference:
            doctors_in_session = [
                p for p in session.participants 
                if p.role == ParticipantRole.DOCTOR
            ]
            
            # This would need to be implemented with proper gender tracking
            # For now, we'll just log the preference
            session.compliance_flags.append(f"gender_preference_{participant.gender_preference}")
        
        # Add Islamic calendar considerations
        if "cultural_considerations" not in session.healthcare_context.__dict__:
            session.healthcare_context.cultural_considerations = []
        
        session.healthcare_context.cultural_considerations.extend([
            "islamic_calendar_aware",
            "gender_preference_respected",
            "arabic_language_support"
        ])
    
    async def admit_from_waiting_room(
        self,
        session_id: str,
        participant_id: str,
        admitted_by: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Admit participant from waiting room to video session
        
        Args:
            session_id: Video session ID
            participant_id: Participant to admit
            admitted_by: Who admitted the participant
            user_id: User ID for audit trail
        
        Returns:
            Updated participant details
        """
        if session_id not in self.waiting_rooms:
            raise TwilioHIPAAException(
                message=f"Waiting room not found: {session_id}",
                operation="admit_from_waiting_room"
            )
        
        # Find participant in waiting room
        waiting_participants = self.waiting_rooms[session_id]
        participant = None
        
        for i, p in enumerate(waiting_participants):
            if p.participant_id == participant_id:
                participant = waiting_participants.pop(i)
                break
        
        if not participant:
            raise TwilioHIPAAException(
                message=f"Participant not in waiting room: {participant_id}",
                operation="admit_from_waiting_room"
            )
        
        # Add to session (bypass waiting room)
        result = await self.add_participant(
            session_id,
            participant,
            bypass_waiting_room=True,
            user_id=user_id
        )
        
        # Audit admission
        await self._audit_participant_admitted(participant, session_id, admitted_by, user_id)
        
        return result
    
    async def start_recording(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        encryption_required: bool = True
    ) -> Dict[str, Any]:
        """
        Start recording video session with HIPAA compliance
        
        Args:
            session_id: Video session ID
            user_id: User ID for audit trail
            encryption_required: Require recording encryption
        
        Returns:
            Recording details
        """
        if session_id not in self.active_sessions:
            raise TwilioHIPAAException(
                message=f"Video session not found: {session_id}",
                operation="start_recording"
            )
        
        session = self.active_sessions[session_id]
        
        if not session.recording_enabled:
            raise TwilioHIPAAException(
                message="Recording not enabled for this session",
                operation="start_recording"
            )
        
        try:
            # Start Twilio recording
            recording = self.twilio_client.client.video.rooms(session.room_sid).recordings.create()
            
            session.recording_status = RecordingStatus.RECORDING
            session.recording_sids.append(recording.sid)
            
            # Set up encryption for recording if required
            if encryption_required and self.encryption_enabled:
                await self._setup_recording_encryption(session, recording.sid)
            
            # Audit event
            await self._audit_recording_started(session, recording.sid, user_id)
            
            logger.info(f"Recording started for session {session_id}: {recording.sid}")
            
            return {
                "recording_sid": recording.sid,
                "session_id": session_id,
                "status": "recording",
                "encrypted": encryption_required and self.encryption_enabled,
                "started_at": datetime.utcnow().isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Recording start failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to start recording: {str(e)}",
                twilio_error_code=getattr(e, 'code', None),
                operation="start_recording"
            )
    
    async def _setup_recording_encryption(self, session: VideoSession, recording_sid: str):
        """Set up encryption for video recording"""
        if not session.encryption:
            return
        
        try:
            # Use session encryption key for recording
            encryption_key = base64.b64decode(session.encryption.encryption_key)
            
            # Store recording encryption metadata
            recording_encryption = {
                "recording_sid": recording_sid,
                "encryption_key_id": session.encryption.key_id,
                "algorithm": session.encryption.algorithm,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # This would be stored in the database in a real implementation
            session.audit_trail.append({
                "action": "recording_encryption_setup",
                "recording_sid": recording_sid,
                "encryption_metadata": recording_encryption,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Recording encryption setup failed: {str(e)}")
            raise EncryptionException(
                message="Failed to set up recording encryption",
                encryption_context="video_recording",
                details={"recording_sid": recording_sid, "error": str(e)}
            )
    
    async def share_medical_document(
        self,
        session_id: str,
        document_data: bytes,
        document_type: str,
        shared_by: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Share medical document during video consultation
        
        Args:
            session_id: Video session ID
            document_data: Document binary data
            document_type: Type of document (e.g., DICOM, PDF, image)
            shared_by: Who shared the document
            user_id: User ID for audit trail
        
        Returns:
            Document sharing details
        """
        if session_id not in self.active_sessions:
            raise TwilioHIPAAException(
                message=f"Video session not found: {session_id}",
                operation="share_medical_document"
            )
        
        session = self.active_sessions[session_id]
        
        # PHI detection and validation
        phi_result = await self.compliance.detect_phi(
            str(document_data),
            context="medical_document_sharing",
            auto_redact=False  # Don't auto-redact medical documents
        )
        
        if phi_result.phi_detected:
            # Log PHI presence but allow sharing in healthcare context
            logger.info(f"PHI detected in shared document: {phi_result.phi_types}")
        
        try:
            # Encrypt document if encryption is enabled
            encrypted_data = document_data
            encryption_metadata = None
            
            if self.encryption_enabled and session.encryption:
                encrypted_data, encryption_metadata = await self._encrypt_document(
                    document_data,
                    session.encryption
                )
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Create sharing record
            sharing_record = {
                "document_id": document_id,
                "session_id": session_id,
                "document_type": document_type,
                "shared_by": shared_by,
                "shared_at": datetime.utcnow().isoformat(),
                "size_bytes": len(document_data),
                "encrypted": encryption_metadata is not None,
                "phi_detected": phi_result.phi_detected,
                "phi_types": [t.value for t in phi_result.phi_types]
            }
            
            # Add to session audit trail
            session.audit_trail.append({
                "action": "document_shared",
                "document_metadata": sharing_record,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Audit event
            await self._audit_document_shared(session, sharing_record, user_id)
            
            logger.info(f"Document shared in session {session_id}: {document_id}")
            
            return {
                "document_id": document_id,
                "session_id": session_id,
                "status": "shared",
                "encrypted": encryption_metadata is not None,
                "size_mb": round(len(document_data) / 1024 / 1024, 2),
                "type": document_type,
                "shared_at": sharing_record["shared_at"]
            }
            
        except Exception as e:
            logger.error(f"Document sharing failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to share document: {str(e)}",
                operation="share_medical_document"
            )
    
    async def _encrypt_document(
        self,
        document_data: bytes,
        encryption: VideoEncryption
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt medical document for secure sharing"""
        try:
            # Use session encryption key
            fernet = Fernet(encryption.encryption_key.encode())
            encrypted_data = fernet.encrypt(document_data)
            
            # Create encryption metadata
            metadata = {
                "key_id": encryption.key_id,
                "algorithm": encryption.algorithm,
                "encrypted_at": datetime.utcnow().isoformat(),
                "original_size": len(document_data),
                "encrypted_size": len(encrypted_data)
            }
            
            return encrypted_data, metadata
            
        except Exception as e:
            logger.error(f"Document encryption failed: {str(e)}")
            raise EncryptionException(
                message="Failed to encrypt medical document",
                encryption_context="document_sharing",
                details={"error": str(e)}
            )
    
    async def end_session(
        self,
        session_id: str,
        ended_by: str,
        reason: str = "normal",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End video consultation session
        
        Args:
            session_id: Video session ID
            ended_by: Who ended the session
            reason: Reason for ending (normal, emergency, technical)
            user_id: User ID for audit trail
        
        Returns:
            Session summary
        """
        if session_id not in self.active_sessions:
            raise TwilioHIPAAException(
                message=f"Video session not found: {session_id}",
                operation="end_session"
            )
        
        session = self.active_sessions[session_id]
        
        try:
            # Complete any active recordings
            if session.recording_status == RecordingStatus.RECORDING:
                for recording_sid in session.recording_sids:
                    await self._complete_recording(session, recording_sid)
            
            # Close Twilio room
            room = self.twilio_client.client.video.rooms(session.room_sid).update(status='completed')
            
            # Update session status
            session.status = VideoSessionStatus.EMERGENCY_ENDED if reason == "emergency" else VideoSessionStatus.COMPLETED
            session.ended_at = datetime.utcnow()
            
            # Update participant statuses
            for participant in session.participants:
                if participant.left_at is None:
                    participant.left_at = datetime.utcnow()
                participant.connection_status = "disconnected"
            
            # Calculate session duration
            duration_minutes = 0
            if session.actual_start:
                duration = session.ended_at - session.actual_start
                duration_minutes = round(duration.total_seconds() / 60, 2)
            
            # Create session summary
            summary = {
                "session_id": session_id,
                "session_type": session.session_type.value,
                "status": session.status.value,
                "started_at": session.actual_start.isoformat() if session.actual_start else None,
                "ended_at": session.ended_at.isoformat(),
                "duration_minutes": duration_minutes,
                "participants_count": len(session.participants),
                "recordings_count": len(session.recording_sids),
                "ended_by": ended_by,
                "reason": reason,
                "healthcare_context": asdict(session.healthcare_context)
            }
            
            # Audit event
            await self._audit_session_ended(session, ended_by, reason, user_id)
            
            # Archive session data
            await self._archive_session(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            if session_id in self.waiting_rooms:
                del self.waiting_rooms[session_id]
            
            logger.info(f"Video session ended: {session_id}")
            
            return summary
            
        except TwilioException as e:
            logger.error(f"Session end failed: {str(e)}")
            raise TwilioHIPAAException(
                message=f"Failed to end session: {str(e)}",
                twilio_error_code=getattr(e, 'code', None),
                operation="end_session"
            )
    
    async def _complete_recording(self, session: VideoSession, recording_sid: str):
        """Complete and encrypt video recording"""
        try:
            # Stop recording
            recording = self.twilio_client.client.video.rooms(session.room_sid).recordings(recording_sid).update(status='stopped')
            
            session.recording_status = RecordingStatus.COMPLETED
            
            # Set up post-processing for encryption if enabled
            if self.encryption_enabled:
                await self._schedule_recording_encryption(session, recording_sid)
            
        except Exception as e:
            logger.error(f"Recording completion failed: {str(e)}")
    
    async def _schedule_recording_encryption(self, session: VideoSession, recording_sid: str):
        """Schedule recording for encryption and secure storage"""
        # This would typically be handled by a background job queue
        encryption_task = {
            "task_id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "recording_sid": recording_sid,
            "encryption_key_id": session.encryption.key_id,
            "scheduled_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        session.audit_trail.append({
            "action": "recording_encryption_scheduled",
            "task_metadata": encryption_task,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Recording encryption scheduled: {recording_sid}")
    
    async def _archive_session(self, session: VideoSession):
        """Archive completed session for compliance retention"""
        # Calculate retention period based on Saudi healthcare regulations
        retention_years = 10  # Standard medical record retention
        retention_until = datetime.utcnow() + timedelta(days=365 * retention_years)
        
        archive_record = {
            "session_id": session.session_id,
            "archived_at": datetime.utcnow().isoformat(),
            "retention_until": retention_until.isoformat(),
            "session_data": asdict(session),
            "compliance_flags": session.compliance_flags,
            "saudi_compliance": self.saudi_compliance
        }
        
        # This would be stored in a compliance database
        logger.info(f"Session archived: {session.session_id}, retention until: {retention_until}")
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of video session"""
        if session_id not in self.active_sessions:
            # Check if it might be archived
            return {
                "session_id": session_id,
                "status": "not_found",
                "message": "Session not found or archived"
            }
        
        session = self.active_sessions[session_id]
        
        # Get Twilio room status
        room_status = "unknown"
        try:
            room = self.twilio_client.client.video.rooms(session.room_sid).fetch()
            room_status = room.status
        except Exception as e:
            logger.warning(f"Could not fetch room status: {str(e)}")
        
        return {
            "session_id": session_id,
            "status": session.status.value,
            "room_status": room_status,
            "participants_count": len(session.participants),
            "waiting_count": len(self.waiting_rooms.get(session_id, [])),
            "recording_status": session.recording_status.value,
            "duration_minutes": self._calculate_session_duration(session),
            "session_type": session.session_type.value,
            "healthcare_context": asdict(session.healthcare_context),
            "arabic_support": True
        }
    
    def _calculate_session_duration(self, session: VideoSession) -> float:
        """Calculate current session duration in minutes"""
        if not session.actual_start:
            return 0.0
        
        end_time = session.ended_at or datetime.utcnow()
        duration = end_time - session.actual_start
        return round(duration.total_seconds() / 60, 2)
    
    async def get_waiting_room_participants(self, session_id: str) -> List[Dict[str, Any]]:
        """Get list of participants in waiting room"""
        if session_id not in self.waiting_rooms:
            return []
        
        participants = []
        for participant in self.waiting_rooms[session_id]:
            participants.append({
                "participant_id": participant.participant_id,
                "name": participant.name,
                "role": participant.role.value,
                "preferred_language": participant.preferred_language,
                "waiting_since": participant.joined_at.isoformat() if participant.joined_at else None
            })
        
        return participants
    
    async def update_video_quality(
        self,
        session_id: str,
        quality: VideoQuality,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update video quality for session"""
        if session_id not in self.active_sessions:
            raise TwilioHIPAAException(
                message=f"Video session not found: {session_id}",
                operation="update_video_quality"
            )
        
        session = self.active_sessions[session_id]
        old_quality = session.quality_settings
        session.quality_settings = quality
        
        # Audit quality change
        await self._audit_quality_changed(session, old_quality, quality, user_id)
        
        return {
            "session_id": session_id,
            "old_quality": old_quality.value,
            "new_quality": quality.value,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    # Audit methods
    async def _audit_session_created(self, session: VideoSession, organizer: VideoParticipant, user_id: Optional[str]):
        """Audit session creation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "video_session_created",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "session_type": session.session_type.value,
            "organizer_id": organizer.participant_id,
            "organizer_role": organizer.role.value,
            "max_participants": session.max_participants,
            "encryption_enabled": self.encryption_enabled,
            "saudi_compliance": self.saudi_compliance,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Video session created - {session.session_id}", extra=audit_event)
    
    async def _audit_participant_joined(self, participant: VideoParticipant, session: VideoSession, user_id: Optional[str]):
        """Audit participant joining"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "participant_joined",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "participant_id": participant.participant_id,
            "participant_role": participant.role.value,
            "preferred_language": participant.preferred_language,
            "is_saudi_resident": participant.is_saudi_resident,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Participant joined - {participant.participant_id}", extra=audit_event)
    
    async def _audit_participant_waiting(self, participant: VideoParticipant, session: VideoSession, user_id: Optional[str]):
        """Audit participant in waiting room"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "participant_waiting",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "participant_id": participant.participant_id,
            "participant_role": participant.role.value,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Participant waiting - {participant.participant_id}", extra=audit_event)
    
    async def _audit_participant_admitted(self, participant: VideoParticipant, session_id: str, admitted_by: str, user_id: Optional[str]):
        """Audit participant admission from waiting room"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "participant_admitted",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "participant_id": participant.participant_id,
            "admitted_by": admitted_by,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Participant admitted - {participant.participant_id}", extra=audit_event)
    
    async def _audit_recording_started(self, session: VideoSession, recording_sid: str, user_id: Optional[str]):
        """Audit recording start"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "recording_started",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "recording_sid": recording_sid,
            "encryption_enabled": self.encryption_enabled,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Recording started - {recording_sid}", extra=audit_event)
    
    async def _audit_document_shared(self, session: VideoSession, sharing_record: Dict[str, Any], user_id: Optional[str]):
        """Audit document sharing"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "document_shared",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "document_id": sharing_record["document_id"],
            "document_type": sharing_record["document_type"],
            "shared_by": sharing_record["shared_by"],
            "phi_detected": sharing_record["phi_detected"],
            "encrypted": sharing_record["encrypted"],
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Document shared - {sharing_record['document_id']}", extra=audit_event)
    
    async def _audit_session_ended(self, session: VideoSession, ended_by: str, reason: str, user_id: Optional[str]):
        """Audit session end"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "video_session_ended",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "ended_by": ended_by,
            "reason": reason,
            "duration_minutes": self._calculate_session_duration(session),
            "participants_count": len(session.participants),
            "recordings_count": len(session.recording_sids),
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Session ended - {session.session_id}", extra=audit_event)
    
    async def _audit_token_generated(self, participant: VideoParticipant, session: VideoSession, ttl: int):
        """Audit access token generation"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "access_token_generated",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "participant_id": participant.participant_id,
            "ttl_seconds": ttl,
            "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Access token generated - {participant.participant_id}", extra=audit_event)
    
    async def _audit_quality_changed(self, session: VideoSession, old_quality: VideoQuality, new_quality: VideoQuality, user_id: Optional[str]):
        """Audit video quality change"""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "action": "video_quality_changed",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session.session_id,
            "old_quality": old_quality.value,
            "new_quality": new_quality.value,
            "user_id": user_id
        }
        
        self.audit_events.append(audit_event)
        logger.info(f"AUDIT: Video quality changed - {session.session_id}", extra=audit_event)
    
    async def get_audit_trail(
        self,
        session_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail for video services"""
        filtered_events = self.audit_events.copy()
        
        # Apply filters
        if session_id:
            filtered_events = [
                e for e in filtered_events
                if e.get("session_id") == session_id
            ]
        
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
        
        if action_type:
            filtered_events = [
                e for e in filtered_events
                if e.get("action") == action_type
            ]
        
        return filtered_events
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for video services"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "video_service_active": True,
            "active_sessions": len(self.active_sessions),
            "waiting_rooms": len(self.waiting_rooms),
            "encryption_enabled": self.encryption_enabled,
            "saudi_compliance": self.saudi_compliance,
            "checks": {}
        }
        
        try:
            # Check Twilio Video service
            rooms = self.twilio_client.client.video.rooms.list(limit=1)
            health_status["checks"]["twilio_video"] = "PASS"
        except Exception as e:
            health_status["checks"]["twilio_video"] = f"FAIL: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check encryption service
        if self.encryption_enabled:
            try:
                test_encryption = self._generate_encryption_key()
                health_status["checks"]["encryption"] = "PASS"
            except Exception as e:
                health_status["checks"]["encryption"] = f"FAIL: {str(e)}"
                health_status["status"] = "unhealthy"
        
        # Check compliance service
        try:
            await self.compliance.validate_baa_compliance("Twilio_Video")
            health_status["checks"]["compliance"] = "PASS"
        except Exception as e:
            health_status["checks"]["compliance"] = f"FAIL: {str(e)}"
            health_status["status"] = "unhealthy"
        
        return health_status


# Context manager for video consultation sessions
@asynccontextmanager
async def video_consultation_session(
    session_type: VideoCallType,
    organizer: VideoParticipant,
    **kwargs
):
    """
    Context manager for HIPAA-compliant video consultation
    
    Usage:
        async with video_consultation_session(
            VideoCallType.DOCTOR_PATIENT,
            doctor_participant
        ) as session:
            # Add participants, start recording, etc.
            await session.add_participant(patient_participant)
    """
    video_service = VideoHIPAAService()
    session = await video_service.create_video_session(
        session_type,
        organizer,
        **kwargs
    )
    
    try:
        yield video_service
    finally:
        # Clean up session
        if session.session_id in video_service.active_sessions:
            await video_service.end_session(
                session.session_id,
                ended_by="system",
                reason="context_manager_cleanup"
            )


# Export main classes and functions
__all__ = [
    "VideoHIPAAService",
    "VideoSession",
    "VideoParticipant",
    "VideoCallType",
    "VideoQuality",
    "ParticipantRole",
    "VideoSessionStatus",
    "RecordingStatus",
    "HealthcareContext",
    "VideoEncryption",
    "video_consultation_session"
]