"""
BrainSAIT Enhanced NPHIES Service - Business Logic Components
Following OidTree 5-component pattern
Integrates with existing NPHIES service
"""

from models.healthcare import NPHIESClaim
from core.database import get_db_connection
import logging
import json

logger = logging.getLogger(__name__)


class NPHIESService:
    """Enhanced NPHIES service with modular architecture"""
    
    def __init__(self):
        # Try to import existing NPHIES service for integration
        try:
            from services.nphies_service import NPHIESService as ExistingNPHIESService
            self.existing_service = ExistingNPHIESService()
            logger.info("Integrated with existing NPHIES service")
        except ImportError:
            self.existing_service = None
            logger.info("Using standalone NPHIES service")
    
    async def submit_claim(self, claim: NPHIESClaim) -> dict:
        """Submit NPHIES claim"""
        try:
            # Use existing service if available
            if self.existing_service and hasattr(self.existing_service, 'submit_claim'):
                return await self.existing_service.submit_claim(claim)
            
            # Fallback implementation
            with get_db_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO nphies_claims 
                    (claim_id, patient_nphies_id, provider_nphies_id, claim_type,
                     amount, currency, diagnosis_codes, procedure_codes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    claim.claim_id, claim.patient_nphies_id, claim.provider_nphies_id,
                    claim.claim_type, claim.amount, claim.currency,
                    json.dumps(claim.diagnosis_codes), json.dumps(claim.procedure_codes),
                    claim.status
                ))
                
                return {
                    "success": True,
                    "claim_id": claim.claim_id,
                    "status": "submitted",
                    "message": "NPHIES claim submitted successfully"
                }
                
        except Exception as e:
            logger.error(f"Error submitting NPHIES claim: {e}")
            raise
    
    async def get_claim(self, claim_id: str) -> dict:
        """Get NPHIES claim details"""
        try:
            # Use existing service if available
            if self.existing_service and hasattr(self.existing_service, 'get_claim'):
                return await self.existing_service.get_claim(claim_id)
            
            # Fallback implementation
            with get_db_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT * FROM nphies_claims WHERE claim_id = ?
                """, (claim_id,))
                
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"NPHIES claim {claim_id} not found")
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"Error retrieving NPHIES claim: {e}")
            raise