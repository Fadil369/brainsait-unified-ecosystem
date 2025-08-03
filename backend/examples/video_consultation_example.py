"""
BrainSAIT Healthcare Platform - Video Consultation Example
Demonstrates HIPAA-compliant video consultation setup for Saudi healthcare

This example shows how to:
1. Create a video consultation session
2. Add participants with proper roles
3. Manage waiting room functionality
4. Handle Arabic language support
5. Record sessions with encryption
6. Share medical documents securely
7. End sessions with proper audit trails

Author: BrainSAIT Healthcare Platform Team
Version: 1.0.0
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Import video services
from backend.services.communication.twilio_hipaa.video import (
    VideoHIPAAService,
    VideoParticipant,
    VideoCallType,
    VideoQuality,
    ParticipantRole,
    HealthcareContext,
    video_consultation_session
)


async def example_doctor_patient_consultation():
    """
    Example: Doctor-Patient video consultation with full HIPAA compliance
    """
    print("=== Doctor-Patient Video Consultation Example ===")
    
    # Create doctor participant
    doctor = VideoParticipant(
        participant_id="doctor_001",
        user_id="dr_ahmed_hassan",
        name="د. أحمد حسن",  # Dr. Ahmed Hassan in Arabic
        role=ParticipantRole.DOCTOR,
        phone_number="+966501234567",
        email="ahmed.hassan@brainsait.com",
        license_number="DOC-2024-001",
        department="Cardiology",
        organization="King Fahd Medical City",
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Create patient participant
    patient = VideoParticipant(
        participant_id="patient_001",
        user_id="patient_sara_ali",
        name="سارة علي",  # Sara Ali in Arabic
        role=ParticipantRole.PATIENT,
        phone_number="+966509876543",
        is_saudi_resident=True,
        preferred_language="ar",
        gender_preference="female"  # Cultural consideration for Saudi patients
    )
    
    # Healthcare context
    healthcare_context = HealthcareContext(
        patient_id="PAT-2024-001",
        medical_record_number="MRN-12345678",
        appointment_id="APT-2024-001",
        diagnosis_codes=["I25.10", "Z51.11"],  # ICD-10 codes
        specialty="Cardiology",
        urgency_level="routine",
        consultation_type="follow_up",
        saudi_health_id="1234567890",
        family_consent=True,
        cultural_considerations=[
            "gender_preference_respected",
            "arabic_language_primary",
            "islamic_prayer_considerations"
        ]
    )
    
    # Create video consultation session
    async with video_consultation_session(
        VideoCallType.DOCTOR_PATIENT,
        doctor,
        healthcare_context=healthcare_context,
        quality=VideoQuality.HIGH,
        max_participants=5  # Allow family members to join
    ) as video_service:
        
        # Get session details
        session_id = list(video_service.active_sessions.keys())[0]
        session = video_service.active_sessions[session_id]
        
        print(f"✅ Video session created: {session_id}")
        print(f"   Room SID: {session.room_sid}")
        print(f"   Doctor access token: {doctor.access_token[:20]}...")
        print(f"   Arabic UI available: Yes")
        print(f"   Encryption enabled: {video_service.encryption_enabled}")
        
        # Add patient to session (will go to waiting room first)
        patient_result = await video_service.add_participant(
            session_id,
            patient,
            user_id="admin_001"
        )
        
        print(f"✅ Patient added to waiting room")
        print(f"   Status: {patient_result['status']}")
        
        # Doctor admits patient from waiting room
        admitted_result = await video_service.admit_from_waiting_room(
            session_id,
            patient.participant_id,
            admitted_by=doctor.participant_id,
            user_id="admin_001"
        )
        
        print(f"✅ Patient admitted to consultation")
        print(f"   Patient access token: {admitted_result['access_token'][:20]}...")
        
        # Start recording for compliance
        recording_result = await video_service.start_recording(
            session_id,
            user_id=doctor.user_id,
            encryption_required=True
        )
        
        print(f"✅ Recording started")
        print(f"   Recording SID: {recording_result['recording_sid']}")
        print(f"   Encrypted: {recording_result['encrypted']}")
        
        # Simulate medical document sharing
        sample_document = b"Sample medical report content..."
        document_result = await video_service.share_medical_document(
            session_id,
            sample_document,
            "PDF",
            doctor.participant_id,
            user_id=doctor.user_id
        )
        
        print(f"✅ Medical document shared")
        print(f"   Document ID: {document_result['document_id']}")
        print(f"   Size: {document_result['size_mb']} MB")
        print(f"   Encrypted: {document_result['encrypted']}")
        
        # Get session status
        status = await video_service.get_session_status(session_id)
        print(f"✅ Session status: {status['status']}")
        print(f"   Duration: {status['duration_minutes']} minutes")
        print(f"   Participants: {status['participants_count']}")
        
        # End session
        session_summary = await video_service.end_session(
            session_id,
            ended_by=doctor.participant_id,
            reason="consultation_completed",
            user_id=doctor.user_id
        )
        
        print(f"✅ Session ended successfully")
        print(f"   Total duration: {session_summary['duration_minutes']} minutes")
        print(f"   Recordings: {session_summary['recordings_count']}")
        
        return session_summary


async def example_emergency_consultation():
    """
    Example: Emergency multi-participant video consultation
    """
    print("\n=== Emergency Video Consultation Example ===")
    
    # Emergency doctor
    emergency_doctor = VideoParticipant(
        participant_id="emergency_doctor_001",
        user_id="dr_fatima_omar",
        name="د. فاطمة عمر",  # Dr. Fatima Omar in Arabic
        role=ParticipantRole.DOCTOR,
        department="Emergency Medicine",
        organization="King Abdulaziz Medical City",
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Emergency healthcare context
    emergency_context = HealthcareContext(
        patient_id="EMRG-2024-001",
        urgency_level="emergency",
        consultation_type="emergency",
        cultural_considerations=["emergency_protocol", "family_notification"]
    )
    
    video_service = VideoHIPAAService()
    
    # Create emergency session
    session = await video_service.create_video_session(
        VideoCallType.EMERGENCY_CONSULTATION,
        emergency_doctor,
        healthcare_context=emergency_context,
        quality=VideoQuality.STANDARD,  # Optimize for speed
        max_participants=15,  # Allow multiple specialists
        user_id="emergency_admin"
    )
    
    print(f"🚨 Emergency session created: {session.session_id}")
    
    # Add specialist (bypass waiting room for emergency)
    specialist = VideoParticipant(
        participant_id="specialist_001",
        user_id="dr_mohammed_ibrahim",
        name="د. محمد إبراهيم",  # Dr. Mohammed Ibrahim in Arabic
        role=ParticipantRole.SPECIALIST,
        department="Neurology",
        preferred_language="ar"
    )
    
    specialist_result = await video_service.add_participant(
        session.session_id,
        specialist,
        bypass_waiting_room=True,  # Emergency bypass
        user_id="emergency_admin"
    )
    
    print(f"🚨 Specialist added (emergency bypass)")
    
    # Auto-start recording for emergency documentation
    recording = await video_service.start_recording(
        session.session_id,
        user_id="emergency_system",
        encryption_required=True
    )
    
    print(f"🚨 Emergency recording started: {recording['recording_sid']}")
    
    # Get audit trail for emergency compliance
    audit_trail = await video_service.get_audit_trail(
        session_id=session.session_id,
        action_type="video_session_created"
    )
    
    print(f"📋 Audit events recorded: {len(audit_trail)}")
    
    # End emergency session
    emergency_summary = await video_service.end_session(
        session.session_id,
        ended_by="emergency_system",
        reason="emergency_resolved",
        user_id="emergency_admin"
    )
    
    print(f"✅ Emergency session completed")
    print(f"   Duration: {emergency_summary['duration_minutes']} minutes")
    
    return emergency_summary


async def example_family_consultation():
    """
    Example: Family consultation with cultural considerations
    """
    print("\n=== Family Video Consultation Example ===")
    
    # Pediatrician
    pediatrician = VideoParticipant(
        participant_id="pediatrician_001",
        user_id="dr_layla_hassan",
        name="د. ليلى حسن",  # Dr. Layla Hassan in Arabic
        role=ParticipantRole.DOCTOR,
        department="Pediatrics",
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Child patient (represented by parent)
    child_patient = VideoParticipant(
        participant_id="child_patient_001",
        user_id="child_omar_ali",
        name="عمر علي",  # Omar Ali in Arabic
        role=ParticipantRole.PATIENT,
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Father
    father = VideoParticipant(
        participant_id="father_001",
        user_id="ali_mohammed",
        name="علي محمد",  # Ali Mohammed in Arabic
        role=ParticipantRole.FAMILY_MEMBER,
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Mother
    mother = VideoParticipant(
        participant_id="mother_001",
        user_id="aisha_ali",
        name="عائشة علي",  # Aisha Ali in Arabic
        role=ParticipantRole.FAMILY_MEMBER,
        is_saudi_resident=True,
        preferred_language="ar"
    )
    
    # Family consultation context
    family_context = HealthcareContext(
        patient_id="CHILD-2024-001",
        consultation_type="family_consultation",
        family_consent=True,
        cultural_considerations=[
            "family_involvement_preferred",
            "arabic_language_primary",
            "islamic_family_values",
            "both_parents_present"
        ]
    )
    
    video_service = VideoHIPAAService()
    
    # Create family consultation
    session = await video_service.create_video_session(
        VideoCallType.FAMILY_CONSULTATION,
        pediatrician,
        healthcare_context=family_context,
        max_participants=8,  # Extended family support
        user_id="family_coordinator"
    )
    
    print(f"👨‍👩‍👧‍👦 Family consultation created: {session.session_id}")
    
    # Add family members
    for family_member in [child_patient, father, mother]:
        result = await video_service.add_participant(
            session.session_id,
            family_member,
            bypass_waiting_room=True,  # Family members can join directly
            user_id="family_coordinator"
        )
        print(f"   ✅ {family_member.name} joined consultation")
    
    # Start recording with family consent
    recording = await video_service.start_recording(
        session.session_id,
        user_id=pediatrician.user_id,
        encryption_required=True
    )
    
    print(f"📹 Family consultation recording started")
    
    # Simulate consultation completion
    await asyncio.sleep(1)  # Simulate consultation time
    
    # End family session
    family_summary = await video_service.end_session(
        session.session_id,
        ended_by=pediatrician.participant_id,
        reason="family_consultation_completed",
        user_id="family_coordinator"
    )
    
    print(f"✅ Family consultation completed")
    print(f"   Total participants: {family_summary['participants_count']}")
    
    return family_summary


async def example_quality_management():
    """
    Example: Video quality management and network adaptation
    """
    print("\n=== Video Quality Management Example ===")
    
    doctor = VideoParticipant(
        participant_id="doctor_quality_test",
        user_id="dr_test",
        name="Test Doctor",
        role=ParticipantRole.DOCTOR,
        preferred_language="en"
    )
    
    video_service = VideoHIPAAService()
    
    # Create session with high quality initially
    session = await video_service.create_video_session(
        VideoCallType.DOCTOR_PATIENT,
        doctor,
        quality=VideoQuality.HD,
        user_id="quality_admin"
    )
    
    print(f"🎥 Session created with HD quality")
    
    # Simulate network issues - reduce quality
    quality_result = await video_service.update_video_quality(
        session.session_id,
        VideoQuality.STANDARD,
        user_id="quality_admin"
    )
    
    print(f"📶 Quality adjusted due to network conditions")
    print(f"   From: {quality_result['old_quality']}")
    print(f"   To: {quality_result['new_quality']}")
    
    # Get session status
    status = await video_service.get_session_status(session.session_id)
    print(f"📊 Current session status: {status['status']}")
    
    # Health check
    health = await video_service.health_check()
    print(f"💚 Video service health: {health['status']}")
    print(f"   Active sessions: {health['active_sessions']}")
    print(f"   Encryption enabled: {health['encryption_enabled']}")
    
    # Clean up
    await video_service.end_session(
        session.session_id,
        ended_by="system",
        reason="test_completed",
        user_id="quality_admin"
    )
    
    return health


async def main():
    """
    Run all video consultation examples
    """
    print("🏥 BrainSAIT Healthcare Platform - Video Consultation Examples")
    print("=" * 70)
    
    try:
        # Run examples
        doctor_patient_result = await example_doctor_patient_consultation()
        emergency_result = await example_emergency_consultation()
        family_result = await example_family_consultation()
        quality_result = await example_quality_management()
        
        print("\n" + "=" * 70)
        print("📋 SUMMARY OF ALL EXAMPLES")
        print("=" * 70)
        print(f"✅ Doctor-Patient Consultation: {doctor_patient_result['duration_minutes']} min")
        print(f"🚨 Emergency Consultation: {emergency_result['duration_minutes']} min")
        print(f"👨‍👩‍👧‍👦 Family Consultation: {family_result['participants_count']} participants")
        print(f"🎥 Video Service Health: {quality_result['status']}")
        print("\n🎉 All video consultation examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())