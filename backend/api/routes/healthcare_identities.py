"""
BrainSAIT Healthcare Identities Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models.healthcare import HealthcareIdentity
from services.healthcare_service import HealthcareIdentityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/healthcare-identities", tags=["Healthcare Identities"])


@router.get("", response_model=List[HealthcareIdentity])
async def get_healthcare_identities(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    service: HealthcareIdentityService = Depends()
):
    """Retrieve healthcare identities with filtering and pagination"""
    try:
        return await service.get_identities(
            skip=skip, 
            limit=limit, 
            entity_type=entity_type
        )
    except Exception as e:
        logger.error(f"Error retrieving healthcare identities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve healthcare identities"
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def register_healthcare_identity(
    identity: HealthcareIdentity,
    service: HealthcareIdentityService = Depends()
):
    """Register a new healthcare identity in the system"""
    try:
        return await service.register_identity(identity)
    except ValueError as e:
        logger.warning(f"Invalid healthcare identity data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering healthcare identity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register healthcare identity"
        )


@router.put("/{identity_id}", response_model=dict)
async def update_healthcare_identity(
    identity_id: str,
    identity: HealthcareIdentity,
    service: HealthcareIdentityService = Depends()
):
    """Update an existing healthcare identity"""
    try:
        return await service.update_identity(identity_id, identity)
    except ValueError as e:
        logger.warning(f"Invalid healthcare identity update: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating healthcare identity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update healthcare identity"
        )


@router.delete("/{identity_id}", response_model=dict)
async def revoke_healthcare_identity(
    identity_id: str,
    service: HealthcareIdentityService = Depends()
):
    """Revoke (soft delete) a healthcare identity"""
    try:
        return await service.revoke_identity(identity_id)
    except ValueError as e:
        logger.warning(f"Healthcare identity not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error revoking healthcare identity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke healthcare identity"
        )