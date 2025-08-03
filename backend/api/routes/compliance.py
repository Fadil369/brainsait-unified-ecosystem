"""
BrainSAIT Compliance Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from models.communication import ConsentRequest
from services.compliance_service import ComplianceService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])


@router.get("/audit", response_model=dict)
async def get_audit_logs(
    service: ComplianceService = Depends()
):
    """Get audit logs for compliance reporting"""
    try:
        return await service.get_audit_logs()
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.post("/consent", response_model=dict)
async def manage_consent(
    consent: ConsentRequest,
    service: ComplianceService = Depends()
):
    """Manage patient consent for data processing"""
    try:
        return await service.manage_consent(consent)
    except ValueError as e:
        logger.warning(f"Invalid consent request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error managing consent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to manage consent"
        )


@router.get("/phi-check", response_model=dict)
async def phi_check(
    text: str,
    service: ComplianceService = Depends()
):
    """Check text for PHI (Personal Health Information)"""
    try:
        return await service.check_phi(text)
    except Exception as e:
        logger.error(f"Error checking PHI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check PHI"
        )