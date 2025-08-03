# BrainSAIT Video Services - HIPAA-Compliant Telehealth Platform

## Overview

The BrainSAIT Video Services module provides comprehensive HIPAA-compliant video consultation capabilities specifically designed for the Saudi Arabia healthcare ecosystem. Built on Twilio Video with enhanced security, encryption, and cultural considerations.

## Key Features

### 🏥 Healthcare-Specific Features
- **HIPAA-Compliant Video Consultations**: End-to-end encrypted video sessions with comprehensive audit trails
- **Saudi Healthcare Integration**: Native NPHIES integration and MOH compliance
- **Arabic Language Support**: Complete RTL interface with Arabic medical terminology
- **Cultural Considerations**: Gender preferences, Islamic calendar integration, and family consultation support

### 🔒 Security & Compliance
- **End-to-End Encryption**: AES-256-GCM encryption for all video streams and recordings
- **HIPAA Audit Trails**: Comprehensive logging of all video session activities
- **PHI Protection**: Automatic PHI detection in chat and document sharing
- **Access Control**: Role-based permissions with healthcare provider verification

### 🎥 Advanced Video Features
- **Multi-Participant Sessions**: Support for up to 15 participants per session
- **Waiting Room Management**: Secure admission control for participants
- **Recording with Encryption**: Automatic encrypted recording with 7-year retention
- **Screen Sharing**: Medical record and DICOM image sharing during consultations
- **Quality Adaptation**: Automatic video quality adjustment based on network conditions

### 🚑 Specialized Consultation Types
- **Doctor-Patient Consultations**: Standard telehealth appointments
- **Emergency Consultations**: Rapid multi-specialist emergency calls
- **Family Consultations**: Cultural-aware family involvement sessions
- **Second Opinion Conferences**: Multi-provider consultation sessions
- **Remote Monitoring**: Patient monitoring with medical device integration

## Quick Start

### Basic Video Consultation

```python
from backend.services.communication.twilio_hipaa.video import (
    VideoHIPAAService, VideoParticipant, VideoCallType, 
    ParticipantRole, HealthcareContext
)

# Create participants
doctor = VideoParticipant(
    participant_id="doctor_001",
    user_id="dr_ahmed_hassan",
    name="د. أحمد حسن",  # Arabic name
    role=ParticipantRole.DOCTOR,
    phone_number="+966501234567",
    license_number="DOC-2024-001",
    department="Cardiology",
    is_saudi_resident=True,
    preferred_language="ar"
)

patient = VideoParticipant(
    participant_id="patient_001",
    user_id="patient_sara",
    name="سارة علي",  # Arabic name
    role=ParticipantRole.PATIENT,
    is_saudi_resident=True,
    preferred_language="ar",
    gender_preference="female"  # Cultural consideration
)

# Healthcare context
healthcare_context = HealthcareContext(
    patient_id="PAT-2024-001",
    medical_record_number="MRN-12345678",
    appointment_id="APT-2024-001",
    diagnosis_codes=["I25.10"],
    specialty="Cardiology",
    saudi_health_id="1234567890",
    family_consent=True,
    cultural_considerations=["arabic_language_primary"]
)

# Create video service
video_service = VideoHIPAAService()

# Create session
session = await video_service.create_video_session(
    session_type=VideoCallType.DOCTOR_PATIENT,
    organizer=doctor,
    healthcare_context=healthcare_context,
    user_id="admin_001"
)

# Add patient
patient_result = await video_service.add_participant(
    session.session_id,
    patient,
    user_id="admin_001"
)

# Start recording
recording = await video_service.start_recording(
    session.session_id,
    user_id=doctor.user_id,
    encryption_required=True
)

print(f"Session: {session.session_id}")
print(f"Doctor token: {doctor.access_token}")
print(f"Patient token: {patient_result['access_token']}")
print(f"Recording: {recording['recording_sid']}")
```

### Context Manager Usage

```python
from backend.services.communication.twilio_hipaa.video import video_consultation_session

async with video_consultation_session(
    VideoCallType.DOCTOR_PATIENT,
    doctor,
    healthcare_context=healthcare_context
) as video_service:
    # Add participants
    await video_service.add_participant(session_id, patient)
    
    # Start recording
    await video_service.start_recording(session_id)
    
    # Share medical documents
    with open('medical_report.pdf', 'rb') as f:
        await video_service.share_medical_document(
            session_id,
            f.read(),
            "PDF",
            doctor.participant_id
        )
    
    # Session automatically ends and cleans up
```

## Configuration

### Environment Variables

```bash
# Twilio Video Configuration
HIPAA_TWILIO_API_KEY=your_api_key
HIPAA_TWILIO_API_SECRET=your_api_secret
HIPAA_VIDEO_ENABLED=true
HIPAA_VIDEO_RECORDING_ENABLED=true
HIPAA_VIDEO_AUTO_RECORD=true
HIPAA_VIDEO_MAX_PARTICIPANTS=10
HIPAA_VIDEO_ENCRYPTION_REQUIRED=true
HIPAA_VIDEO_WAITING_ROOM_ENABLED=true
HIPAA_VIDEO_SCREEN_SHARING_ENABLED=true
HIPAA_VIDEO_CHAT_ENABLED=true
HIPAA_VIDEO_RECORDING_RETENTION_DAYS=2555  # 7 years
```

### HIPAA Settings Configuration

```python
from backend.services.communication.config.hipaa_settings import hipaa_settings

# Video-specific settings
video_config = hipaa_settings.get_channel_config(CommunicationChannel.VIDEO)
print(f"Video enabled: {video_config['enabled']}")
print(f"Recording enabled: {video_config['recording_enabled']}")
print(f"Max participants: {video_config['max_participants']}")
print(f"Encryption required: {video_config['encryption_required']}")
```

## API Reference

### VideoHIPAAService

Main service class for HIPAA-compliant video consultations.

#### Methods

##### `create_video_session(session_type, organizer, healthcare_context=None, **kwargs)`
Creates a new video consultation session.

**Parameters:**
- `session_type` (VideoCallType): Type of consultation
- `organizer` (VideoParticipant): Session organizer
- `healthcare_context` (HealthcareContext, optional): Healthcare-specific context
- `scheduled_start` (datetime, optional): Scheduled start time
- `max_participants` (int): Maximum participants (default: 10)
- `quality` (VideoQuality): Video quality setting
- `user_id` (str, optional): User ID for audit trail

**Returns:** `VideoSession` object with room details and encryption info.

##### `add_participant(session_id, participant, bypass_waiting_room=False, user_id=None)`
Adds a participant to the video session.

**Parameters:**
- `session_id` (str): Video session ID
- `participant` (VideoParticipant): Participant to add
- `bypass_waiting_room` (bool): Skip waiting room (default: False)
- `user_id` (str, optional): User ID for audit trail

**Returns:** Dictionary with participant details and access token.

##### `admit_from_waiting_room(session_id, participant_id, admitted_by, user_id=None)`
Admits a participant from the waiting room.

##### `start_recording(session_id, user_id=None, encryption_required=True)`
Starts recording the video session with encryption.

##### `share_medical_document(session_id, document_data, document_type, shared_by, user_id=None)`
Shares a medical document during the consultation.

##### `end_session(session_id, ended_by, reason="normal", user_id=None)`
Ends the video consultation session.

### Data Classes

#### VideoParticipant
Represents a participant in the video consultation.

```python
@dataclass
class VideoParticipant:
    participant_id: str
    user_id: str
    name: str
    role: ParticipantRole
    phone_number: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    organization: Optional[str] = None
    is_saudi_resident: bool = False
    preferred_language: str = "ar"
    gender_preference: Optional[str] = None
    # ... additional fields
```

#### HealthcareContext
Healthcare-specific context for consultations.

```python
@dataclass
class HealthcareContext:
    patient_id: Optional[str] = None
    medical_record_number: Optional[str] = None
    appointment_id: Optional[str] = None
    diagnosis_codes: List[str] = field(default_factory=list)
    specialty: Optional[str] = None
    urgency_level: str = "routine"
    consultation_type: str = "general"
    saudi_health_id: Optional[str] = None
    family_consent: bool = False
    cultural_considerations: List[str] = field(default_factory=list)
```

### Enums

#### VideoCallType
- `DOCTOR_PATIENT`: Standard doctor-patient consultation
- `MEDICAL_TEAM`: Medical team conference
- `FAMILY_CONSULTATION`: Family involvement consultation
- `SECOND_OPINION`: Second opinion conference
- `EMERGENCY_CONSULTATION`: Emergency consultation
- `REMOTE_MONITORING`: Remote patient monitoring
- `TRAINING_SESSION`: Medical training session

#### ParticipantRole
- `DOCTOR`: Medical doctor
- `PATIENT`: Patient
- `NURSE`: Nursing staff
- `SPECIALIST`: Medical specialist
- `FAMILY_MEMBER`: Patient family member
- `OBSERVER`: Session observer
- `ADMIN`: Administrative user

#### VideoQuality
- `LOW`: 320x240 resolution
- `STANDARD`: 640x480 resolution
- `HIGH`: 1280x720 resolution
- `HD`: 1920x1080 resolution

## Arabic Language Support

### UI Elements
The module includes comprehensive Arabic UI elements:

```python
arabic_ui = {
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
    "doctor": "طبيب",
    "patient": "مريض",
    "family": "أفراد العائلة"
}
```

### RTL Support
All video interface elements support right-to-left text direction for Arabic content.

### Medical Terminology
Integrated Arabic medical terminology for healthcare professionals.

## Security Features

### Encryption
- **Video Streams**: WebRTC with DTLS encryption
- **Recordings**: AES-256-GCM encryption at rest
- **Documents**: Fernet encryption for shared medical documents
- **Metadata**: Separate encryption for PHI-containing metadata

### Access Control
- Role-based access permissions
- Healthcare provider license verification
- Waiting room admission control
- Session-based access tokens

### Audit Trails
Comprehensive logging of all video session activities:
- Session creation and termination
- Participant joins and departures
- Recording start/stop events
- Document sharing activities
- Quality adjustments
- PHI detection events

## Compliance

### HIPAA Compliance
- Business Associate Agreement validation
- PHI detection and protection
- Encrypted data transmission and storage
- Comprehensive audit logging
- Access control and authentication
- Data retention policies

### Saudi Arabia Compliance
- PDPL (Personal Data Protection Law) compliance
- MOH (Ministry of Health) integration
- SCFHS (Saudi Commission for Health Specialties) reporting
- NPHIES (National Platform for Health Information Exchange) integration
- Data residency requirements
- Cultural and religious considerations

## Error Handling

### Common Errors

#### `TwilioHIPAAException`
General Twilio video service errors.

#### `PHIExposureException`
PHI detected in video chat or documents.

#### `EncryptionException`
Encryption setup or processing failures.

#### `AccessControlException`
Access denied or authentication failures.

### Error Handling Example

```python
try:
    session = await video_service.create_video_session(
        VideoCallType.DOCTOR_PATIENT,
        doctor
    )
except TwilioHIPAAException as e:
    logger.error(f"Video session creation failed: {e.message}")
    # Handle specific error
except PHIExposureException as e:
    logger.warning(f"PHI detected: {e.phi_type}")
    # Handle PHI exposure
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    # Handle general error
```

## Testing

### Running Tests

```bash
# Run video service tests
pytest backend/tests/test_video_hipaa.py -v

# Run with coverage
pytest backend/tests/test_video_hipaa.py --cov=backend.services.communication.twilio_hipaa.video

# Run specific test class
pytest backend/tests/test_video_hipaa.py::TestVideoSessionCreation -v
```

### Test Coverage
- Video session creation and management
- Participant management and access control
- Recording and encryption functionality
- Arabic language and cultural support
- HIPAA compliance and audit trails
- Error handling and edge cases

### Example Test

```python
@pytest.mark.asyncio
async def test_arabic_consultation():
    """Test Arabic language video consultation"""
    doctor = VideoParticipant(
        name="د. أحمد حسن",
        role=ParticipantRole.DOCTOR,
        preferred_language="ar"
    )
    
    video_service = VideoHIPAAService()
    session = await video_service.create_video_session(
        VideoCallType.DOCTOR_PATIENT,
        doctor
    )
    
    assert session.session_id is not None
    assert doctor.preferred_language == "ar"
    assert video_service.arabic_ui_elements is not None
```

## Performance Considerations

### Optimization Tips
- Use appropriate video quality settings for network conditions
- Enable waiting rooms to control bandwidth usage
- Implement network quality monitoring
- Use screen sharing selectively for large documents
- Cache access tokens appropriately

### Monitoring
- Track video session duration and quality
- Monitor recording storage usage
- Track participant connection quality
- Monitor encryption performance
- Audit PHI detection accuracy

## Integration Examples

### With Electronic Health Records (EHR)

```python
# EHR integration example
async def create_ehr_consultation(patient_id, doctor_id, appointment_id):
    # Fetch patient and doctor from EHR
    patient_data = await ehr_service.get_patient(patient_id)
    doctor_data = await ehr_service.get_doctor(doctor_id)
    
    # Create participants
    doctor = VideoParticipant(
        participant_id=doctor_id,
        name=doctor_data['name'],
        role=ParticipantRole.DOCTOR,
        license_number=doctor_data['license']
    )
    
    patient = VideoParticipant(
        participant_id=patient_id,
        name=patient_data['name'],
        role=ParticipantRole.PATIENT
    )
    
    # Healthcare context from EHR
    context = HealthcareContext(
        patient_id=patient_id,
        medical_record_number=patient_data['mrn'],
        appointment_id=appointment_id,
        diagnosis_codes=patient_data['diagnoses']
    )
    
    # Create video session
    session = await video_service.create_video_session(
        VideoCallType.DOCTOR_PATIENT,
        doctor,
        healthcare_context=context
    )
    
    # Update EHR with session details
    await ehr_service.update_appointment(appointment_id, {
        'video_session_id': session.session_id,
        'video_room_sid': session.room_sid
    })
    
    return session
```

### With NPHIES Integration

```python
# NPHIES billing integration
async def end_consultation_with_billing(session_id, doctor_id):
    # End video session
    summary = await video_service.end_session(
        session_id,
        ended_by=doctor_id,
        reason="consultation_completed"
    )
    
    # Submit to NPHIES for billing
    nphies_claim = {
        'session_id': session_id,
        'duration_minutes': summary['duration_minutes'],
        'consultation_type': summary['session_type'],
        'provider_id': doctor_id,
        'patient_id': summary['healthcare_context']['patient_id']
    }
    
    await nphies_service.submit_telehealth_claim(nphies_claim)
    
    return summary
```

## Support and Documentation

### Additional Resources
- [HIPAA Compliance Guide](./HIPAA_COMPLIANCE.md)
- [Saudi Healthcare Integration](./SAUDI_COMPLIANCE.md)
- [API Documentation](./API_REFERENCE.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

### Support
For technical support or questions:
- Email: support@brainsait.com
- Documentation: https://docs.brainsait.com/video-services
- GitHub Issues: [BrainSAIT Repository](https://github.com/brainsait/healthcare-platform)

### Contributing
Please read our contribution guidelines before submitting pull requests or issues.

---

**BrainSAIT Healthcare Platform**  
*Transforming Healthcare Through Technology*  
Version 1.0.0 | © 2024 BrainSAIT Healthcare Solutions