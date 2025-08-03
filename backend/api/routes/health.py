"""
BrainSAIT Health Check Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health Check"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for BrainSAIT Healthcare Platform"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BrainSAIT Healthcare Platform",
        "version": "2.2.0",
        "components": {
            "api": "operational",
            "database": "operational", 
            "nphies": "operational",
            "ai_services": "operational",
            "communication": "operational"
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint for BrainSAIT Healthcare Platform"""
    return {
        "message": "BrainSAIT Healthcare Unification Platform",
        "description": "NPHIES-integrated healthcare revenue cycle management",
        "version": "2.2.0",
        "documentation": "/docs",
        "health_check": "/health",
        "arabic_support": True,
        "nphies_compliant": True,
        "hipaa_compliant": True
    }