#!/usr/bin/env python3
"""
BrainSAIT NPHIES MCP Server
Healthcare-specific Model Context Protocol server for Saudi NPHIES integration
Provides Copilot with real-time access to NPHIES healthcare services
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timezone
from typing import Any, Sequence

# MCP Server imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, ListToolsRequest
)
import mcp.types as types

# Healthcare-specific imports
from ..services.nphies_service import NPHIESService
from ..models.healthcare import PatientEligibility, Claim, PreAuthorization
from ..core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITNPHIESMCPServer:
    """
    NPHIES MCP Server for BrainSAIT Healthcare Platform
    
    Provides GitHub Copilot with tools to:
    - Validate patient eligibility
    - Submit preauthorizations
    - Process claims
    - Check claim status
    - Access provider information
    - Validate NPHIES data formats
    """
    
    def __init__(self):
        self.server = Server("brainsait-nphies-mcp-server")
        self.settings = get_settings()
        self.nphies_service = NPHIESService()
        self.setup_tools()
        self.setup_resources()

    def setup_tools(self):
        """Register all NPHIES-related tools for Copilot"""
        
        @self.server.tool("validate_patient_eligibility")
        async def validate_patient_eligibility(
            patient_id: str,
            insurance_id: str,
            service_date: str,
            provider_id: str = None
        ) -> list[types.TextContent]:
            """
            Validate patient eligibility through NPHIES
            
            Args:
                patient_id: Patient national ID or medical record number
                insurance_id: Insurance policy ID
                service_date: Date of service (YYYY-MM-DD)
                provider_id: Healthcare provider ID (optional)
            
            Returns:
                Eligibility status with coverage details
            """
            try:
                logger.info(f"Validating eligibility for patient {patient_id}")
                
                eligibility = await self.nphies_service.check_eligibility(
                    patient_id=patient_id,
                    insurance_id=insurance_id,
                    service_date=service_date,
                    provider_id=provider_id or self.settings.HEALTHCARE_PROVIDER_ID
                )
                
                result_text = f"""
🏥 NPHIES Patient Eligibility Validation

✅ Patient ID: {patient_id}
📋 Insurance ID: {insurance_id}
📅 Service Date: {service_date}
🏥 Provider: {provider_id or 'Default'}

📊 Eligibility Status: {eligibility.status}
🔒 Coverage Type: {eligibility.coverage_type}
💰 Coverage Amount: {eligibility.coverage_amount} SAR
📅 Valid Until: {eligibility.valid_until}
🔗 NPHIES Response ID: {eligibility.response_id}

💡 Additional Information:
- Copayment: {eligibility.copayment_amount} SAR
- Deductible: {eligibility.deductible_amount} SAR
- Network Status: {eligibility.network_status}
- Special Authorization Required: {eligibility.auth_required}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error validating eligibility: {str(e)}")
                return [types.TextContent(
                    type="text", 
                    text=f"❌ NPHIES Eligibility Validation Error: {str(e)}"
                )]

        @self.server.tool("submit_preauthorization")
        async def submit_preauthorization(
            patient_id: str,
            provider_id: str,
            service_codes: str,  # JSON string of service codes
            diagnosis_codes: str,  # JSON string of diagnosis codes
            estimated_cost: float = None,
            urgency_level: str = "routine"
        ) -> list[types.TextContent]:
            """
            Submit preauthorization request to NPHIES
            
            Args:
                patient_id: Patient identifier
                provider_id: Healthcare provider ID
                service_codes: JSON array of CPT/HCPCS service codes
                diagnosis_codes: JSON array of ICD-10 diagnosis codes
                estimated_cost: Estimated treatment cost in SAR
                urgency_level: urgent|routine|emergency
            """
            try:
                logger.info(f"Submitting preauth for patient {patient_id}")
                
                # Parse JSON strings
                services = json.loads(service_codes) if isinstance(service_codes, str) else service_codes
                diagnoses = json.loads(diagnosis_codes) if isinstance(diagnosis_codes, str) else diagnosis_codes
                
                preauth = await self.nphies_service.submit_preauthorization(
                    patient_id=patient_id,
                    provider_id=provider_id,
                    service_codes=services,
                    diagnosis_codes=diagnoses,
                    estimated_cost=estimated_cost,
                    urgency_level=urgency_level
                )
                
                result_text = f"""
📋 NPHIES Preauthorization Submitted

🔗 Reference Number: {preauth.reference_number}
📊 Status: {preauth.status}
👤 Patient ID: {patient_id}
🏥 Provider ID: {provider_id}

✅ Approved Services:
{chr(10).join([f"  • {service}" for service in preauth.approved_services])}

⚠️ Pending Services:
{chr(10).join([f"  • {service}" for service in preauth.pending_services])}

❌ Denied Services:
{chr(10).join([f"  • {service}" for service in preauth.denied_services])}

💰 Financial Information:
- Approved Amount: {preauth.approved_amount} SAR
- Patient Responsibility: {preauth.patient_responsibility} SAR
- Valid Until: {preauth.valid_until}

📝 Notes: {preauth.notes or 'None'}
🕐 Submitted: {preauth.submission_date}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error submitting preauthorization: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ NPHIES Preauthorization Error: {str(e)}"
                )]

        @self.server.tool("process_claim")
        async def process_claim(
            patient_id: str,
            provider_id: str,
            service_date: str,
            service_codes: str,
            diagnosis_codes: str,
            charges: str,  # JSON string of charges
            preauth_number: str = None
        ) -> list[types.TextContent]:
            """
            Process medical claim through NPHIES
            
            Args:
                patient_id: Patient identifier
                provider_id: Healthcare provider ID
                service_date: Date services were provided
                service_codes: JSON array of service codes with quantities
                diagnosis_codes: JSON array of diagnosis codes
                charges: JSON object with charge details
                preauth_number: Preauthorization reference number (if applicable)
            """
            try:
                logger.info(f"Processing claim for patient {patient_id}")
                
                # Parse JSON inputs
                services = json.loads(service_codes)
                diagnoses = json.loads(diagnosis_codes)
                charge_details = json.loads(charges)
                
                claim = await self.nphies_service.submit_claim(
                    patient_id=patient_id,
                    provider_id=provider_id,
                    service_date=service_date,
                    service_codes=services,
                    diagnosis_codes=diagnoses,
                    charges=charge_details,
                    preauth_number=preauth_number
                )
                
                result_text = f"""
💳 NPHIES Claim Processing Result

🔗 Claim Number: {claim.claim_number}
📊 Status: {claim.status}
👤 Patient ID: {patient_id}
🏥 Provider ID: {provider_id}
📅 Service Date: {service_date}

💰 Financial Summary:
- Total Charges: {claim.total_charges} SAR
- Covered Amount: {claim.covered_amount} SAR
- Patient Responsibility: {claim.patient_responsibility} SAR
- Copayment: {claim.copayment} SAR
- Deductible: {claim.deductible} SAR

📋 Processing Details:
- Adjudication Date: {claim.adjudication_date}
- Payment Status: {claim.payment_status}
- Check Number: {claim.check_number or 'Pending'}

⚠️ Adjustment Codes:
{chr(10).join([f"  • {code}: {desc}" for code, desc in claim.adjustment_codes.items()]) if claim.adjustment_codes else "None"}

📝 Remarks: {claim.remarks or 'None'}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error processing claim: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ NPHIES Claim Processing Error: {str(e)}"
                )]

        @self.server.tool("check_claim_status")
        async def check_claim_status(
            claim_number: str,
            provider_id: str = None
        ) -> list[types.TextContent]:
            """
            Check status of submitted claim
            
            Args:
                claim_number: NPHIES claim reference number
                provider_id: Healthcare provider ID (optional)
            """
            try:
                logger.info(f"Checking status for claim {claim_number}")
                
                status = await self.nphies_service.get_claim_status(
                    claim_number=claim_number,
                    provider_id=provider_id or self.settings.HEALTHCARE_PROVIDER_ID
                )
                
                result_text = f"""
📊 NPHIES Claim Status Check

🔗 Claim Number: {claim_number}
📊 Current Status: {status.current_status}
📅 Last Updated: {status.last_updated}
🏥 Provider ID: {provider_id or 'Default'}

📋 Status History:
{chr(10).join([f"  • {item.date}: {item.status} - {item.notes}" for item in status.status_history])}

💰 Payment Information:
- Payment Status: {status.payment_status}
- Payment Date: {status.payment_date or 'Pending'}
- Payment Amount: {status.payment_amount} SAR
- Payment Method: {status.payment_method or 'Not specified'}

⚠️ Outstanding Issues:
{chr(10).join([f"  • {issue}" for issue in status.outstanding_issues]) if status.outstanding_issues else "None"}

📱 Next Actions Required:
{chr(10).join([f"  • {action}" for action in status.required_actions]) if status.required_actions else "None"}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error checking claim status: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ NPHIES Claim Status Error: {str(e)}"
                )]

        @self.server.tool("validate_nphies_format")
        async def validate_nphies_format(
            data_type: str,  # "eligibility"|"preauth"|"claim"|"patient"|"provider"
            data_payload: str  # JSON string of data to validate
        ) -> list[types.TextContent]:
            """
            Validate data format against NPHIES standards
            
            Args:
                data_type: Type of data to validate
                data_payload: JSON string containing data to validate
            """
            try:
                logger.info(f"Validating NPHIES format for {data_type}")
                
                data = json.loads(data_payload)
                validation_result = await self.nphies_service.validate_format(
                    data_type=data_type,
                    data=data
                )
                
                result_text = f"""
✅ NPHIES Format Validation

📋 Data Type: {data_type}
✅ Validation Status: {validation_result.is_valid}
📊 NPHIES Version: {validation_result.nphies_version}

{f"✅ Validation Success: Data meets NPHIES standards" if validation_result.is_valid else "❌ Validation Failed"}

⚠️ Validation Issues:
{chr(10).join([f"  • {issue.field}: {issue.message}" for issue in validation_result.issues]) if validation_result.issues else "None"}

💡 Recommendations:
{chr(10).join([f"  • {rec}" for rec in validation_result.recommendations]) if validation_result.recommendations else "Data format is optimal"}

📋 Required Fields: {', '.join(validation_result.required_fields)}
⚠️ Optional Fields: {', '.join(validation_result.optional_fields)}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error validating NPHIES format: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ NPHIES Format Validation Error: {str(e)}"
                )]

        @self.server.tool("get_provider_info")
        async def get_provider_info(
            provider_id: str = None,
            license_number: str = None
        ) -> list[types.TextContent]:
            """
            Get healthcare provider information from NPHIES
            
            Args:
                provider_id: Provider ID in NPHIES system
                license_number: Provider license number
            """
            try:
                search_by = provider_id or license_number or self.settings.HEALTHCARE_PROVIDER_ID
                logger.info(f"Getting provider info for {search_by}")
                
                provider = await self.nphies_service.get_provider_info(
                    provider_id=provider_id,
                    license_number=license_number
                )
                
                result_text = f"""
🏥 NPHIES Provider Information

🆔 Provider ID: {provider.provider_id}
🏥 Name (English): {provider.name_en}
🏥 Name (Arabic): {provider.name_ar}
📋 License Number: {provider.license_number}
📊 Status: {provider.status}

📍 Location Information:
- City: {provider.city}
- Region: {provider.region}
- Address: {provider.address}
- Phone: {provider.phone}
- Email: {provider.email}

🔧 Services & Specialties:
{chr(10).join([f"  • {specialty}" for specialty in provider.specialties])}

📋 Certification Details:
- License Valid Until: {provider.license_expiry}
- NPHIES Registration Date: {provider.registration_date}
- Last Updated: {provider.last_updated}

💰 Financial Information:
- Network Status: {provider.network_status}
- Payment Terms: {provider.payment_terms}
- Settlement Method: {provider.settlement_method}

⚠️ Compliance Status:
{chr(10).join([f"  • {item}" for item in provider.compliance_notes]) if provider.compliance_notes else "All requirements met"}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error getting provider info: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ NPHIES Provider Info Error: {str(e)}"
                )]

    def setup_resources(self):
        """Setup MCP resources for NPHIES documentation and schemas"""
        
        @self.server.resource("nphies://schema/{schema_type}")
        async def get_nphies_schema(uri: str) -> str:
            """Provide NPHIES schema definitions"""
            schema_type = uri.split("/")[-1]
            
            schemas = {
                "eligibility": {
                    "title": "NPHIES Eligibility Schema",
                    "description": "Schema for patient eligibility requests",
                    "required_fields": ["patient_id", "insurance_id", "service_date"],
                    "optional_fields": ["provider_id", "service_type"],
                    "example": {
                        "patient_id": "1234567890",
                        "insurance_id": "INS-123456",
                        "service_date": "2024-01-15",
                        "provider_id": "PROV-789"
                    }
                },
                "preauth": {
                    "title": "NPHIES Preauthorization Schema",
                    "description": "Schema for preauthorization requests",
                    "required_fields": ["patient_id", "provider_id", "service_codes", "diagnosis_codes"],
                    "optional_fields": ["estimated_cost", "urgency_level"],
                    "example": {
                        "patient_id": "1234567890",
                        "provider_id": "PROV-789",
                        "service_codes": ["99213", "85027"],
                        "diagnosis_codes": ["Z00.129"],
                        "estimated_cost": 450.00,
                        "urgency_level": "routine"
                    }
                }
            }
            
            return json.dumps(schemas.get(schema_type, {"error": "Schema not found"}), indent=2)

    async def run(self):
        """Run the NPHIES MCP server"""
        logger.info("Starting BrainSAIT NPHIES MCP Server...")
        
        try:
            from mcp.server.stdio import stdio_server
            
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Server connected and ready")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="brainsait-nphies-mcp-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={
                                "healthcare_integration": True,
                                "nphies_compliance": True,
                                "saudi_healthcare": True
                            },
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {str(e)}")
            raise

def main():
    """Entry point for the NPHIES MCP server"""
    server = BrainSAITNPHIESMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("NPHIES MCP Server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in NPHIES MCP Server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
