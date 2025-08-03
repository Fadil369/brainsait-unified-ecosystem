"""
BrainSAIT CORS Middleware - Control Components
Following OidTree 5-component pattern
"""

from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logger = logging.getLogger(__name__)


def setup_cors_middleware(app):
    """Setup CORS middleware with enhanced security for healthcare platform"""
    
    # Get allowed origins from environment
    from core.config import get_settings
    settings = get_settings()
    allowed_origins = settings.allowed_origins.split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Audit-Trail"]
    )
    
    logger.info(f"CORS middleware configured for origins: {allowed_origins}")
    return allowed_origins