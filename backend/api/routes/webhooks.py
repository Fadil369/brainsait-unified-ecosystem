"""
BrainSAIT Webhooks Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from services.webhook_service import WebhookService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/twilio/status", response_model=dict)
async def twilio_status_webhook(
    request: Request,
    service: WebhookService = Depends()
):
    """Handle Twilio status update webhooks"""
    try:
        return await service.handle_twilio_status(request)
    except Exception as e:
        logger.error(f"Error handling Twilio status webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Twilio status webhook"
        )


@router.post("/twilio/voice", response_model=str)
async def twilio_voice_webhook(
    request: Request,
    service: WebhookService = Depends()
):
    """Handle Twilio voice call webhooks"""
    try:
        return await service.handle_twilio_voice(request)
    except Exception as e:
        logger.error(f"Error handling Twilio voice webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Twilio voice webhook"
        )


@router.post("/twilio/sms", response_model=str)
async def twilio_sms_webhook(
    request: Request,
    service: WebhookService = Depends()
):
    """Handle Twilio SMS reply webhooks"""
    try:
        return await service.handle_twilio_sms(request)
    except Exception as e:
        logger.error(f"Error handling Twilio SMS webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Twilio SMS webhook"
        )