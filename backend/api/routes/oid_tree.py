"""
BrainSAIT OID Tree Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from services.oid_service import OIDTreeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oid-tree", tags=["OID Tree"])


@router.get("", response_model=dict)
async def get_oid_tree(
    service: OIDTreeService = Depends()
):
    """Get OID tree structure for healthcare identities"""
    try:
        return await service.get_tree_structure()
    except Exception as e:
        logger.error(f"Error retrieving OID tree: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve OID tree structure"
        )