"""
BrainSAIT Logging Middleware - Control Components
Following OidTree 5-component pattern
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """HIPAA-compliant audit logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID for audit trail
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {response.status_code} in {duration:.3f}s",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": duration
            }
        )
        
        # Add audit headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Audit-Trail"] = "enabled"
        
        return response


def setup_logging_middleware(app):
    """Setup audit logging middleware"""
    app.add_middleware(AuditLoggingMiddleware)
    logger.info("Audit logging middleware enabled")