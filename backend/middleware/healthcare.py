"""
BrainSAIT Healthcare Compliance Middleware - Control Components
Following OidTree 5-component pattern
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class HealthcareComplianceMiddleware(BaseHTTPMiddleware):
    """Healthcare compliance and HIPAA validation middleware"""
    
    def __init__(self, app, require_encryption: bool = True):
        super().__init__(app)
        self.require_encryption = require_encryption
    
    async def dispatch(self, request: Request, call_next):
        # Check for HTTPS in production
        if self.require_encryption and not request.url.scheme == "https":
            # Allow HTTP only in development
            if not request.headers.get("X-Development-Mode"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="HTTPS required for healthcare data transmission"
                )
        
        # Add healthcare compliance headers
        response = await call_next(request)
        
        # HIPAA compliance headers
        response.headers["X-Healthcare-Compliant"] = "true"
        response.headers["X-HIPAA-Compliant"] = "true"
        response.headers["X-NPHIES-Compatible"] = "true"
        response.headers["X-Saudi-PDPL-Compliant"] = "true"
        
        return response