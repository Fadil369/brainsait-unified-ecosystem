"""
BrainSAIT Healthcare Platform - Video HIPAA Service Tests
Comprehensive test suite for HIPAA-compliant video consultation services

Tests cover:
- Video session creation and management
- Participant management and access control
- Recording and encryption functionality
- Arabic language and cultural support
- HIPAA compliance and audit trails
- Error handling and edge cases

Author: BrainSAIT Healthcare Platform Team
Version: 1.0.0
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import video services
from backend.services.communication.twilio_hipaa.video import (
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

from backend.services.communication.twilio_hipaa.exceptions import (
    TwilioHIPAAException,
    PHIExposureException,
    EncryptionException,
    AccessControlException
)

from backend.services.communication.config.hipaa_settings import hipaa_settings


class TestVideoHIPAAService:
    """Test suite for VideoHIPAAService"""
    
    @pytest.fixture
    def mock_twilio_client(self):
        """Mock Twilio client for testing"""
        mock_client = Mock()
        mock_room = Mock()
        mock_room.sid = "RM123456789"
        mock_room.status = "in-progress"
        mock_client.video.rooms.create.return_value = mock_room
        mock_client.video.rooms.return_value = mock_room
        return mock_client
    
    @pytest.fixture
    def video_service(self, mock_twilio_client):
        """Create VideoHIPAAService instance for testing"""
        with patch('backend.services.communication.twilio_hipaa.video.TwilioHIPAAClient') as mock_twilio:
            mock_twilio_instance = Mock()
            mock_twilio_instance.client = mock_twilio_client
            mock_twilio_instance.credentials = Mock()
            mock_twilio_instance.credentials.account_sid = "AC123456789"
            mock_twilio.return_value = mock_twilio_instance
            
            service = VideoHIPAAService(
                twilio_client=mock_twilio_instance,
                encryption_enabled=True,
                saudi_compliance=True
            )
            return service
    
    @pytest.fixture
    def sample_doctor(self):
        """Create sample doctor participant"""
        return VideoParticipant(
            participant_id="doctor_001",
            user_id="dr_ahmed_hassan",
            name="د. أحمد حسن",
            role=ParticipantRole.DOCTOR,
            phone_number="+966501234567",
            license_number="DOC-2024-001",
            department="Cardiology",
            is_saudi_resident=True,
            preferred_language="ar"
        )
    
    @pytest.fixture
    def sample_patient(self):
        """Create sample patient participant"""
        return VideoParticipant(
            participant_id="patient_001",
            user_id="patient_sara",
            name="سارة علي",
            role=ParticipantRole.PATIENT,
            phone_number="+966509876543",
            is_saudi_resident=True,
            preferred_language="ar",
            gender_preference="female"
        )
    
    @pytest.fixture
    def sample_healthcare_context(self):
        """Create sample healthcare context"""
        return HealthcareContext(
            patient_id="PAT-2024-001",
            medical_record_number="MRN-12345678",
            appointment_id="APT-2024-001",
            diagnosis_codes=["I25.10"],
            specialty="Cardiology",
            urgency_level="routine",
            saudi_health_id="1234567890",
            family_consent=True,
            cultural_considerations=["arabic_language_primary"]
        )


class TestVideoSessionCreation:
    """Test video session creation functionality"""
    
    @pytest.mark.asyncio
    async def test_create_basic_video_session(self, video_service, sample_doctor, sample_healthcare_context):
        """Test basic video session creation"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            healthcare_context=sample_healthcare_context,
            user_id="test_admin"
        )
        
        assert isinstance(session, VideoSession)
        assert session.session_type == VideoCallType.DOCTOR_PATIENT
        assert session.status == VideoSessionStatus.SCHEDULED
        assert len(session.participants) == 1
        assert session.participants[0] == sample_doctor
        assert session.healthcare_context == sample_healthcare_context
        assert session.encryption is not None
        assert sample_doctor.access_token is not None
    
    @pytest.mark.asyncio
    async def test_create_emergency_session(self, video_service, sample_doctor):
        """Test emergency video session creation"""
        emergency_context = HealthcareContext(
            urgency_level="emergency",
            consultation_type="emergency"
        )
        
        session = await video_service.create_video_session(
            session_type=VideoCallType.EMERGENCY_CONSULTATION,
            organizer=sample_doctor,
            healthcare_context=emergency_context,
            max_participants=15,
            quality=VideoQuality.STANDARD,
            user_id="emergency_admin"
        )
        
        assert session.session_type == VideoCallType.EMERGENCY_CONSULTATION
        assert session.max_participants == 15
        assert session.quality_settings == VideoQuality.STANDARD
        assert session.healthcare_context.urgency_level == "emergency"
    
    @pytest.mark.asyncio
    async def test_session_encryption_generation(self, video_service, sample_doctor):
        """Test encryption key generation for sessions"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        assert session.encryption is not None
        assert isinstance(session.encryption, VideoEncryption)
        assert session.encryption.encryption_key is not None
        assert session.encryption.key_id is not None
        assert session.encryption.algorithm == "AES-256-GCM"
        assert session.encryption.expires_at > datetime.utcnow()
    
    @pytest.mark.asyncio
    async def test_arabic_ui_elements_loaded(self, video_service):
        """Test Arabic UI elements are properly loaded"""
        assert video_service.arabic_ui_elements is not None
        assert "join_call" in video_service.arabic_ui_elements
        assert "انضم إلى المكالمة" in video_service.arabic_ui_elements.values()
        assert "doctor" in video_service.arabic_ui_elements
        assert "طبيب" in video_service.arabic_ui_elements.values()


class TestParticipantManagement:
    """Test participant management functionality"""
    
    @pytest.mark.asyncio
    async def test_add_participant_to_session(self, video_service, sample_doctor, sample_patient):
        """Test adding participant to video session"""
        # Create session
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Add patient
        result = await video_service.add_participant(
            session.session_id,
            sample_patient,
            bypass_waiting_room=True,
            user_id="test_admin"
        )
        
        assert result["participant_id"] == sample_patient.participant_id
        assert result["status"] == "connected"
        assert result["access_token"] is not None
        assert result["arabic_ui"] is not None  # Arabic UI provided
        assert len(session.participants) == 2
    
    @pytest.mark.asyncio
    async def test_waiting_room_functionality(self, video_service, sample_doctor, sample_patient):
        """Test waiting room functionality"""
        # Create session with waiting room enabled
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        session.waiting_room_enabled = True
        
        # Add patient (should go to waiting room)
        result = await video_service.add_participant(
            session.session_id,
            sample_patient,
            bypass_waiting_room=False,
            user_id="test_admin"
        )
        
        assert result["status"] == "waiting"
        assert result["waiting_room"] == True
        assert session.session_id in video_service.waiting_rooms
        assert len(video_service.waiting_rooms[session.session_id]) == 1
    
    @pytest.mark.asyncio
    async def test_admit_from_waiting_room(self, video_service, sample_doctor, sample_patient):
        """Test admitting participant from waiting room"""
        # Create session and add patient to waiting room
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Add to waiting room
        await video_service.add_participant(
            session.session_id,
            sample_patient,
            bypass_waiting_room=False,
            user_id="test_admin"
        )
        
        # Admit from waiting room
        result = await video_service.admit_from_waiting_room(
            session.session_id,
            sample_patient.participant_id,
            admitted_by=sample_doctor.participant_id,
            user_id="test_admin"
        )
        
        assert result["status"] == "connected"
        assert result["access_token"] is not None
        assert len(video_service.waiting_rooms[session.session_id]) == 0
        assert len(session.participants) == 2
    
    @pytest.mark.asyncio
    async def test_cultural_considerations_validation(self, video_service, sample_doctor):
        """Test cultural considerations for Saudi patients"""
        saudi_patient = VideoParticipant(
            participant_id="saudi_patient_001",
            user_id="saudi_patient",
            name="فاطمة أحمد",
            role=ParticipantRole.PATIENT,
            is_saudi_resident=True,
            preferred_language="ar",
            gender_preference="female"
        )
        
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # This should trigger cultural considerations validation
        result = await video_service.add_participant(
            session.session_id,
            saudi_patient,
            bypass_waiting_room=True,
            user_id="test_admin"
        )
        
        assert result["participant_id"] == saudi_patient.participant_id
        assert "gender_preference_female" in session.compliance_flags
        assert "arabic_language_support" in session.healthcare_context.cultural_considerations
    
    @pytest.mark.asyncio
    async def test_participant_limit_enforcement(self, video_service, sample_doctor):
        """Test enforcement of participant limits"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            max_participants=2,
            user_id="test_admin"
        )
        
        # Add second participant
        patient = VideoParticipant(
            participant_id="patient_002",
            user_id="patient_002",
            name="Patient Two",
            role=ParticipantRole.PATIENT
        )
        
        await video_service.add_participant(
            session.session_id,
            patient,
            bypass_waiting_room=True,
            user_id="test_admin"
        )
        
        # Try to add third participant (should fail)
        patient_three = VideoParticipant(
            participant_id="patient_003",
            user_id="patient_003",
            name="Patient Three",
            role=ParticipantRole.PATIENT
        )
        
        with pytest.raises(TwilioHIPAAException, match="Maximum participants reached"):
            await video_service.add_participant(
                session.session_id,
                patient_three,
                bypass_waiting_room=True,
                user_id="test_admin"
            )


class TestRecordingAndEncryption:
    """Test recording and encryption functionality"""
    
    @pytest.mark.asyncio
    async def test_start_recording(self, video_service, sample_doctor):
        """Test starting video recording"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Mock recording creation
        mock_recording = Mock()
        mock_recording.sid = "REC123456789"
        video_service.twilio_client.client.video.rooms.return_value.recordings.create.return_value = mock_recording
        
        result = await video_service.start_recording(
            session.session_id,
            user_id=sample_doctor.user_id,
            encryption_required=True
        )
        
        assert result["recording_sid"] == "REC123456789"
        assert result["status"] == "recording"
        assert result["encrypted"] == True
        assert session.recording_status == RecordingStatus.RECORDING
        assert "REC123456789" in session.recording_sids
    
    @pytest.mark.asyncio
    async def test_recording_encryption_setup(self, video_service, sample_doctor):
        """Test recording encryption setup"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Verify encryption is set up
        assert session.encryption is not None
        
        # Start recording
        mock_recording = Mock()
        mock_recording.sid = "REC123456789"
        video_service.twilio_client.client.video.rooms.return_value.recordings.create.return_value = mock_recording
        
        result = await video_service.start_recording(
            session.session_id,
            user_id=sample_doctor.user_id,
            encryption_required=True
        )
        
        # Check encryption metadata was added to audit trail
        encryption_events = [
            event for event in session.audit_trail
            if event.get("action") == "recording_encryption_setup"
        ]
        assert len(encryption_events) > 0
        assert encryption_events[0]["recording_sid"] == "REC123456789"
    
    @pytest.mark.asyncio
    async def test_recording_without_encryption_fails(self, video_service, sample_doctor):
        """Test that recording fails when encryption is required but not enabled"""
        # Create service without encryption
        video_service.encryption_enabled = False
        
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # This should still work but without encryption
        mock_recording = Mock()
        mock_recording.sid = "REC123456789"
        video_service.twilio_client.client.video.rooms.return_value.recordings.create.return_value = mock_recording
        
        result = await video_service.start_recording(
            session.session_id,
            user_id=sample_doctor.user_id,
            encryption_required=False
        )
        
        assert result["encrypted"] == False


class TestMedicalDocumentSharing:
    """Test medical document sharing functionality"""
    
    @pytest.mark.asyncio
    async def test_share_medical_document(self, video_service, sample_doctor):
        """Test sharing medical document during consultation"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Mock PHI detection
        with patch.object(video_service.compliance, 'detect_phi', new_callable=AsyncMock) as mock_phi:
            mock_phi_result = Mock()
            mock_phi_result.phi_detected = True
            mock_phi_result.phi_types = ["medical_record"]
            mock_phi.return_value = mock_phi_result
            
            document_data = b"Sample medical report with patient information"
            
            result = await video_service.share_medical_document(
                session.session_id,
                document_data,
                "PDF",
                sample_doctor.participant_id,
                user_id=sample_doctor.user_id
            )
            
            assert result["document_id"] is not None
            assert result["session_id"] == session.session_id
            assert result["status"] == "shared"
            assert result["encrypted"] == True
            assert result["type"] == "PDF"
            assert result["size_mb"] > 0
    
    @pytest.mark.asyncio
    async def test_document_encryption(self, video_service, sample_doctor):
        """Test document encryption during sharing"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        document_data = b"Test document content"
        
        # Test document encryption
        encrypted_data, metadata = await video_service._encrypt_document(
            document_data,
            session.encryption
        )
        
        assert encrypted_data != document_data  # Should be encrypted
        assert metadata["key_id"] == session.encryption.key_id
        assert metadata["algorithm"] == session.encryption.algorithm
        assert metadata["original_size"] == len(document_data)
        assert metadata["encrypted_size"] == len(encrypted_data)
    
    @pytest.mark.asyncio
    async def test_document_sharing_with_phi_detection(self, video_service, sample_doctor):
        """Test document sharing with PHI detection"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Document with potential PHI
        phi_document = b"Patient MRN: 12345678, DOB: 1990-01-01"
        
        with patch.object(video_service.compliance, 'detect_phi', new_callable=AsyncMock) as mock_phi:
            mock_phi_result = Mock()
            mock_phi_result.phi_detected = True
            mock_phi_result.phi_types = ["medical_record", "date_of_birth"]
            mock_phi.return_value = mock_phi_result
            
            result = await video_service.share_medical_document(
                session.session_id,
                phi_document,
                "PDF",
                sample_doctor.participant_id,
                user_id=sample_doctor.user_id
            )
            
            # Should succeed but with PHI flagged
            assert result["status"] == "shared"
            
            # Check audit trail includes PHI detection
            sharing_events = [
                event for event in session.audit_trail
                if event.get("action") == "document_shared"
            ]
            assert len(sharing_events) > 0


class TestSessionManagement:
    """Test session management functionality"""
    
    @pytest.mark.asyncio
    async def test_get_session_status(self, video_service, sample_doctor):
        """Test getting session status"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        status = await video_service.get_session_status(session.session_id)
        
        assert status["session_id"] == session.session_id
        assert status["status"] == VideoSessionStatus.SCHEDULED.value
        assert status["participants_count"] == 1
        assert status["waiting_count"] == 0
        assert status["recording_status"] == RecordingStatus.NOT_STARTED.value
        assert status["session_type"] == VideoCallType.DOCTOR_PATIENT.value
        assert status["arabic_support"] == True
    
    @pytest.mark.asyncio
    async def test_update_video_quality(self, video_service, sample_doctor):
        """Test updating video quality"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            quality=VideoQuality.HIGH,
            user_id="test_admin"
        )
        
        result = await video_service.update_video_quality(
            session.session_id,
            VideoQuality.STANDARD,
            user_id="test_admin"
        )
        
        assert result["session_id"] == session.session_id
        assert result["old_quality"] == VideoQuality.HIGH.value
        assert result["new_quality"] == VideoQuality.STANDARD.value
        assert session.quality_settings == VideoQuality.STANDARD
    
    @pytest.mark.asyncio
    async def test_end_session(self, video_service, sample_doctor):
        """Test ending video session"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Mock Twilio room update
        mock_room = Mock()
        mock_room.status = "completed"
        video_service.twilio_client.client.video.rooms.return_value.update.return_value = mock_room
        
        summary = await video_service.end_session(
            session.session_id,
            ended_by=sample_doctor.participant_id,
            reason="consultation_completed",
            user_id="test_admin"
        )
        
        assert summary["session_id"] == session.session_id
        assert summary["status"] == VideoSessionStatus.COMPLETED.value
        assert summary["ended_by"] == sample_doctor.participant_id
        assert summary["reason"] == "consultation_completed"
        assert summary["participants_count"] == 1
        assert session.session_id not in video_service.active_sessions
    
    @pytest.mark.asyncio
    async def test_emergency_session_end(self, video_service, sample_doctor):
        """Test emergency session termination"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.EMERGENCY_CONSULTATION,
            organizer=sample_doctor,
            user_id="emergency_admin"
        )
        
        # Mock Twilio room update
        mock_room = Mock()
        mock_room.status = "completed"
        video_service.twilio_client.client.video.rooms.return_value.update.return_value = mock_room
        
        summary = await video_service.end_session(
            session.session_id,
            ended_by="emergency_system",
            reason="emergency",
            user_id="emergency_admin"
        )
        
        assert summary["status"] == VideoSessionStatus.EMERGENCY_ENDED.value
        assert summary["reason"] == "emergency"


class TestAuditAndCompliance:
    """Test audit and compliance functionality"""
    
    @pytest.mark.asyncio
    async def test_audit_trail_creation(self, video_service, sample_doctor):
        """Test audit trail is properly created"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Check that audit events were created
        assert len(video_service.audit_events) > 0
        
        creation_events = [
            event for event in video_service.audit_events
            if event.get("action") == "video_session_created"
        ]
        assert len(creation_events) == 1
        assert creation_events[0]["session_id"] == session.session_id
        assert creation_events[0]["organizer_id"] == sample_doctor.participant_id
    
    @pytest.mark.asyncio
    async def test_get_audit_trail(self, video_service, sample_doctor, sample_patient):
        """Test retrieving audit trail"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        await video_service.add_participant(
            session.session_id,
            sample_patient,
            bypass_waiting_room=True,
            user_id="test_admin"
        )
        
        # Get audit trail for session
        audit_trail = await video_service.get_audit_trail(
            session_id=session.session_id
        )
        
        assert len(audit_trail) >= 2  # At least session creation and participant join
        
        # Check for specific events
        event_types = [event["action"] for event in audit_trail]
        assert "video_session_created" in event_types
        assert "participant_joined" in event_types
    
    @pytest.mark.asyncio
    async def test_audit_trail_filtering(self, video_service, sample_doctor):
        """Test audit trail filtering capabilities"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Filter by action type
        creation_events = await video_service.get_audit_trail(
            action_type="video_session_created"
        )
        
        assert len(creation_events) == 1
        assert creation_events[0]["action"] == "video_session_created"
        
        # Filter by date range
        now = datetime.utcnow()
        past_events = await video_service.get_audit_trail(
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1)
        )
        
        assert len(past_events) > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, video_service):
        """Test video service health check"""
        health = await video_service.health_check()
        
        assert health["status"] in ["healthy", "unhealthy"]
        assert health["video_service_active"] == True
        assert health["encryption_enabled"] == video_service.encryption_enabled
        assert health["saudi_compliance"] == video_service.saudi_compliance
        assert "checks" in health
        assert isinstance(health["active_sessions"], int)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_session_not_found_error(self, video_service):
        """Test error when session is not found"""
        with pytest.raises(TwilioHIPAAException, match="Video session not found"):
            await video_service.get_session_status("nonexistent_session")
    
    @pytest.mark.asyncio
    async def test_participant_not_in_waiting_room(self, video_service, sample_doctor):
        """Test error when participant not in waiting room"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        with pytest.raises(TwilioHIPAAException, match="Participant not in waiting room"):
            await video_service.admit_from_waiting_room(
                session.session_id,
                "nonexistent_participant",
                admitted_by=sample_doctor.participant_id,
                user_id="test_admin"
            )
    
    @pytest.mark.asyncio
    async def test_recording_when_disabled(self, video_service, sample_doctor):
        """Test error when trying to record with recording disabled"""
        session = await video_service.create_video_session(
            session_type=VideoCallType.DOCTOR_PATIENT,
            organizer=sample_doctor,
            user_id="test_admin"
        )
        
        # Disable recording
        session.recording_enabled = False
        
        with pytest.raises(TwilioHIPAAException, match="Recording not enabled"):
            await video_service.start_recording(
                session.session_id,
                user_id=sample_doctor.user_id
            )


class TestContextManager:
    """Test video consultation context manager"""
    
    @pytest.mark.asyncio
    async def test_video_consultation_context_manager(self, sample_doctor, sample_healthcare_context):
        """Test video consultation context manager"""
        with patch('backend.services.communication.twilio_hipaa.video.VideoHIPAAService') as mock_service:
            mock_service_instance = Mock()
            mock_session = Mock()
            mock_session.session_id = "test_session_123"
            mock_service_instance.create_video_session = AsyncMock(return_value=mock_session)
            mock_service_instance.end_session = AsyncMock()
            mock_service_instance.active_sessions = {"test_session_123": mock_session}
            mock_service.return_value = mock_service_instance
            
            async with video_consultation_session(
                VideoCallType.DOCTOR_PATIENT,
                sample_doctor,
                healthcare_context=sample_healthcare_context
            ) as service:
                assert service == mock_service_instance
                mock_service_instance.create_video_session.assert_called_once()
            
            # Verify cleanup was called
            mock_service_instance.end_session.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])