"""
BrainSAIT CORS Middleware - Control Components
Following OidTree 5-component pattern
"""

from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logger = logging.getLogger(__name__)

def _parse_allowed_origins(raw_origins):
    """
    Normalize ALLOWED_ORIGINS input.
    - Accepts comma-separated strings or lists
    - Trims whitespace
    - Removes trailing slashes (Origin header never includes them)
    - Deduplicates while preserving order
    """
    if raw_origins is None:
        return []

    if isinstance(raw_origins, str):
        candidates = raw_origins.split(",")
    else:
        candidates = list(raw_origins)

    normalized = []
    seen = set()
    for origin in candidates:
        if origin is None:
            continue
        origin = str(origin).strip()
        if not origin:
            continue
        if origin != "*":
            origin = origin.rstrip("/")
        if origin not in seen:
            normalized.append(origin)
            seen.add(origin)

    return normalized


def setup_cors_middleware(app):
    """Setup CORS middleware with enhanced security for healthcare platform"""
    
    # Get allowed origins from environment
    from core.config import get_settings
    settings = get_settings()
    allowed_origins = _parse_allowed_origins(getattr(settings, "allowed_origins", None))

    # CORS spec/security: credentials + "*" is invalid/unsafe. If "*" is present alongside
    # explicit origins, drop "*". If "*" is the only origin, disable credentials.
    allow_credentials = True
    if "*" in allowed_origins:
        if len(allowed_origins) > 1:
            allowed_origins = [o for o in allowed_origins if o != "*"]
            logger.warning(
                "CORS: removed wildcard '*' from ALLOWED_ORIGINS because allow_credentials=True"
            )
        else:
            allow_credentials = False
            logger.warning(
                "CORS: ALLOWED_ORIGINS='*' detected; disabling credentials for safety"
            )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Audit-Trail"]
    )
    
    logger.info(
        f"CORS middleware configured for origins: {allowed_origins} "
        f"(allow_credentials={allow_credentials})"
    )
    return allowed_origins