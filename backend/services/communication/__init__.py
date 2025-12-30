"""
BrainSAIT Healthcare Communication Module
HIPAA-compliant communication services with Twilio integration for Saudi Arabia healthcare
"""

__version__ = "1.0.0"
__author__ = "BrainSAIT Healthcare Platform"

__all__ = []

# NOTE:
# Avoid importing optional/heavy integrations at package import time.
# This keeps `import services.communication` safe in minimal environments (e.g., CI),
# while still exposing conveniences when dependencies are installed.

# Optional Twilio HIPAA components
try:
    from .twilio_hipaa.base import TwilioHIPAAClient  # noqa: F401
    from .twilio_hipaa.sms import TwilioHIPAASMS  # noqa: F401
    from .twilio_hipaa.voice import TwilioHIPAAVoice  # noqa: F401
    from .twilio_hipaa.compliance import HIPAACompliance  # noqa: F401

    __all__ += [
        "TwilioHIPAAClient",
        "TwilioHIPAASMS",
        "TwilioHIPAAVoice",
        "HIPAACompliance",
    ]
except Exception:
    # Twilio (or its transitive deps) isn't installed/available.
    pass

# Core communication services (kept lightweight)
try:
    from .workflow_orchestrator import CommunicationWorkflowOrchestrator as WorkflowOrchestrator  # noqa: F401
    from .patient_communication_service import PatientCommunicationService  # noqa: F401
    from .nphies_compliance import NPHIESComplianceValidator as NPHIESCompliance  # noqa: F401

    __all__ += ["WorkflowOrchestrator", "PatientCommunicationService", "NPHIESCompliance"]
except Exception:
    # Keep import resilient; individual modules may require optional deps.
    pass
