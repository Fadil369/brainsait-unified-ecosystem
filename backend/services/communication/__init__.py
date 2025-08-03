"""
BrainSAIT Healthcare Communication Module
HIPAA-compliant communication services with Twilio integration for Saudi Arabia healthcare
"""

from .twilio_hipaa.base import TwilioHIPAAClient
from .twilio_hipaa.sms import TwilioHIPAASMS  
from .twilio_hipaa.voice import TwilioHIPAAVoice
from .twilio_hipaa.compliance import HIPAACompliance
from .arabic.processor import ArabicProcessor
from .workflows.patient_journey import PatientJourneyWorkflow
from .utils.encryption import HealthcareEncryption
from .utils.audit import CommunicationAudit

__version__ = "1.0.0"
__author__ = "BrainSAIT Healthcare Platform"

__all__ = [
    "TwilioHIPAAClient",
    "TwilioHIPAASMS", 
    "TwilioHIPAAVoice",
    "HIPAACompliance",
    "ArabicProcessor",
    "PatientJourneyWorkflow",
    "HealthcareEncryption",
    "CommunicationAudit"
]
