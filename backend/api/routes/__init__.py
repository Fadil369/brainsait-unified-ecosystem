# BrainSAIT Healthcare API Routes Module
# Container Components following OidTree 5-component pattern

from .health import router as health_router
from .healthcare_identities import router as healthcare_identities_router
from .nphies import router as nphies_router
from .ai_analytics import router as ai_analytics_router
from .communication import router as communication_router
from .workflows import router as workflows_router
from .compliance import router as compliance_router
from .webhooks import router as webhooks_router
from .oid_tree import router as oid_tree_router

# Export all routers for easy mounting
__all__ = [
    "health_router",
    "healthcare_identities_router", 
    "nphies_router",
    "ai_analytics_router",
    "communication_router",
    "workflows_router", 
    "compliance_router",
    "webhooks_router",
    "oid_tree_router"
]