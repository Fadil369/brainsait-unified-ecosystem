# NPHIES Integration Service
# Core service for Saudi Arabia healthcare platform integration
from typing import Dict, List, Optional, Any
import httpx
import json
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class NPHIESEligibilityRequest(BaseModel):
    patient_nphies_id: str
    insurance_id: str
    provider_nphies_id: str
    check_type: str = "benefits"

class NPHIESEligibilityResponse(BaseModel):
    is_eligible: bool
    coverage_details: Dict[str, Any]
    limitations: List[str]
    response_code: str
    response_message: str

class NPHIESClaimsSubmission(BaseModel):
    claim_id: str
    patient_nphies_id: str
    provider_nphies_id: str
    claim_type: str
    procedures: List[Dict[str, Any]]
    diagnosis_codes: List[str]
    total_amount: float

class NPHIESService:
    """
    Core NPHIES integration service implementing Saudi healthcare standards
    Supports Build-Operate-Transfer phases with comprehensive claims management
    """
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        
    async def authenticate(self) -> str:
        """Authenticate with NPHIES OAuth 2.0"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {self._get_basic_auth()}"
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "eligibility preauth claims provider"
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.token_expires_at = datetime.now().timestamp() + token_data["expires_in"]
                return self.access_token
            else:
                raise Exception(f"NPHIES authentication failed: {response.text}")
    
    async def check_eligibility(self, request: NPHIESEligibilityRequest) -> NPHIESEligibilityResponse:
        """Check patient eligibility for services"""
        if not self._is_token_valid():
            await self.authenticate()
            
        eligibility_bundle = self._create_eligibility_fhir_bundle(request)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/EligibilityRequest",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/fhir+json",
                    "Accept": "application/fhir+json",
                    "X-Request-ID": self._generate_request_id()
                },
                json=eligibility_bundle
            )
            
            if response.status_code == 200:
                return self._parse_eligibility_response(response.json())
            else:
                logger.error(f"NPHIES eligibility check failed: {response.text}")
                raise Exception(f"Eligibility check failed: {response.text}")
    
    async def submit_claim(self, claim: NPHIESClaimsSubmission) -> Dict[str, Any]:
        """Submit claim to NPHIES platform"""
        if not self._is_token_valid():
            await self.authenticate()
            
        claim_bundle = self._create_claim_fhir_bundle(claim)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Claim",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/fhir+json",
                    "Accept": "application/fhir+json",
                    "X-Request-ID": self._generate_request_id()
                },
                json=claim_bundle
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"NPHIES claim submission failed: {response.text}")
                raise Exception(f"Claim submission failed: {response.text}")
    
    async def request_preauthorization(self, claim: NPHIESClaimsSubmission) -> Dict[str, Any]:
        """Request pre-authorization for procedures"""
        if not self._is_token_valid():
            await self.authenticate()
            
        preauth_bundle = self._create_preauth_fhir_bundle(claim)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Claim/$submit",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/fhir+json",
                    "Accept": "application/fhir+json",
                    "X-Request-ID": self._generate_request_id()
                },
                json=preauth_bundle
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"NPHIES pre-authorization failed: {response.text}")
                raise Exception(f"Pre-authorization failed: {response.text}")
    
    def _create_eligibility_fhir_bundle(self, request: NPHIESEligibilityRequest) -> Dict[str, Any]:
        """Create FHIR R4 bundle for eligibility request"""
        return {
            "resourceType": "Bundle",
            "id": f"eligibility-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "EligibilityRequest",
                        "id": f"req-{request.patient_nphies_id}",
                        "status": "active",
                        "purpose": ["benefits"],
                        "patient": {
                            "reference": f"Patient/{request.patient_nphies_id}"
                        },
                        "insurer": {
                            "reference": f"Organization/{request.insurance_id}"
                        },
                        "provider": {
                            "reference": f"Organization/{request.provider_nphies_id}"
                        },
                        "created": datetime.now().isoformat()
                    }
                }
            ]
        }
    
    def _create_claim_fhir_bundle(self, claim: NPHIESClaimsSubmission) -> Dict[str, Any]:
        """Create FHIR R4 bundle for claim submission"""
        return {
            "resourceType": "Bundle",
            "id": f"claim-{claim.claim_id}",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Claim",
                        "id": claim.claim_id,
                        "status": "active",
                        "type": {
                            "coding": [
                                {
                                    "system": "http://nphies.sa/terminology/claim-type",
                                    "code": claim.claim_type
                                }
                            ]
                        },
                        "patient": {
                            "reference": f"Patient/{claim.patient_nphies_id}"
                        },
                        "provider": {
                            "reference": f"Organization/{claim.provider_nphies_id}"
                        },
                        "created": datetime.now().isoformat(),
                        "diagnosis": [
                            {
                                "sequence": i + 1,
                                "diagnosisCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "http://hl7.org/fhir/sid/icd-10",
                                            "code": code
                                        }
                                    ]
                                }
                            }
                            for i, code in enumerate(claim.diagnosis_codes)
                        ],
                        "item": [
                            {
                                "sequence": i + 1,
                                "productOrService": {
                                    "coding": [
                                        {
                                            "system": "http://nphies.sa/terminology/procedure",
                                            "code": proc["code"]
                                        }
                                    ]
                                },
                                "unitPrice": {
                                    "value": proc["price"],
                                    "currency": "SAR"
                                },
                                "net": {
                                    "value": proc["price"],
                                    "currency": "SAR"
                                }
                            }
                            for i, proc in enumerate(claim.procedures)
                        ],
                        "total": {
                            "value": claim.total_amount,
                            "currency": "SAR"
                        }
                    }
                }
            ]
        }
    
    def _create_preauth_fhir_bundle(self, claim: NPHIESClaimsSubmission) -> Dict[str, Any]:
        """Create FHIR R4 bundle for pre-authorization"""
        bundle = self._create_claim_fhir_bundle(claim)
        bundle["entry"][0]["resource"]["use"] = "preauthorization"
        return bundle
    
    def _parse_eligibility_response(self, response_data: Dict[str, Any]) -> NPHIESEligibilityResponse:
        """Parse NPHIES eligibility response"""
        # Simplified parsing - would need full FHIR parsing in production
        return NPHIESEligibilityResponse(
            is_eligible=True,  # Parse from response
            coverage_details={},
            limitations=[],
            response_code="200",
            response_message="Success"
        )
    
    def _is_token_valid(self) -> bool:
        """Check if current access token is valid"""
        return (
            self.access_token is not None and
            self.token_expires_at is not None and
            datetime.now().timestamp() < self.token_expires_at - 300  # 5 minute buffer
        )
    
    def _get_basic_auth(self) -> str:
        """Generate basic auth header"""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return f"brainsait-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"