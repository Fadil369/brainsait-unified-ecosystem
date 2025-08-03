"""
BrainSAIT Communication Routes - Container Components  
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models.communication import (
    SMSRequest, VoiceCallRequest, VideoSessionRequest, 
    CommunicationPreferences
)
from services.communication_service import CommunicationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/communication", tags=["Communication"])


@router.post("/sms/send", response_model=dict)
async def send_sms(
    sms_request: SMSRequest,
    service: CommunicationService = Depends()
):
    """Send HIPAA-compliant SMS message"""
    try:
        return await service.send_sms(sms_request)
    except ValueError as e:
        logger.warning(f"Invalid SMS request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send SMS"
        )


@router.post("/voice/call", response_model=dict)
async def make_voice_call(
    call_request: VoiceCallRequest,
    service: CommunicationService = Depends()
):
    """Initiate HIPAA-compliant voice call"""
    try:
        return await service.make_voice_call(call_request)
    except ValueError as e:
        logger.warning(f"Invalid voice call request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error making voice call: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate voice call"
        )


@router.post("/video/session", response_model=dict)
async def create_video_session(
    video_request: VideoSessionRequest,
    service: CommunicationService = Depends()
):
    """Create HIPAA-compliant video consultation session"""
    try:
        return await service.create_video_session(video_request)
    except ValueError as e:
        logger.warning(f"Invalid video session request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating video session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video session"
        )


@router.get("/history/{patient_id}", response_model=List[dict])
async def get_communication_history(
    patient_id: str,
    service: CommunicationService = Depends()
):
    """Get communication history for a patient"""
    try:
        return await service.get_communication_history(patient_id)
    except Exception as e:
        logger.error(f"Error retrieving communication history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication history"
        )


@router.post("/preferences", response_model=dict)
async def set_communication_preferences(
    preferences: CommunicationPreferences,
    service: CommunicationService = Depends()
):
    """Set patient communication preferences"""
    try:
        return await service.set_preferences(preferences)
    except ValueError as e:
        logger.warning(f"Invalid communication preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error setting communication preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set communication preferences"
        )