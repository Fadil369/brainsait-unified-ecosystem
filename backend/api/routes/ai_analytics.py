"""
BrainSAIT AI Analytics Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from models.healthcare import AIAnalysis
from services.ai_service import AIAnalyticsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-analytics", tags=["AI Analytics"])


@router.post("/analyze", response_model=dict)
async def perform_ai_analysis(
    analysis: AIAnalysis,
    service: AIAnalyticsService = Depends()
):
    """Perform AI analysis on healthcare data"""
    try:
        return await service.perform_analysis(analysis)
    except ValueError as e:
        logger.warning(f"Invalid AI analysis request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error performing AI analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform AI analysis"
        )