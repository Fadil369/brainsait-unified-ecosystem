"""
BrainSAIT NPHIES Routes - Container Components
Following OidTree 5-component pattern  
"""

from fastapi import APIRouter, HTTPException, status, Depends
from models.healthcare import NPHIESClaim
from services.enhanced_nphies_service import NPHIESService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nphies", tags=["NPHIES"])


@router.post("/claims", response_model=dict)
async def submit_nphies_claim(
    claim: NPHIESClaim,
    service: NPHIESService = Depends()
):
    """Submit NPHIES claim for processing"""
    try:
        return await service.submit_claim(claim)
    except ValueError as e:
        logger.warning(f"Invalid NPHIES claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting NPHIES claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit NPHIES claim"
        )


@router.get("/claims/{claim_id}", response_model=dict)
async def get_nphies_claim(
    claim_id: str,
    service: NPHIESService = Depends()
):
    """Retrieve NPHIES claim status and details"""
    try:
        return await service.get_claim(claim_id)
    except ValueError as e:
        logger.warning(f"NPHIES claim not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving NPHIES claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve NPHIES claim"
        )