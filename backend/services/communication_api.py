"""
BrainSAIT Healthcare Platform - Communication API Endpoints
FastAPI endpoints for the comprehensive patient communication workflow system

This API provides:
1. RESTful endpoints for all communication workflows
2. Integration with the main BrainSAIT healthcare platform
3. HIPAA-compliant API security and audit logging
4. Real-time workflow monitoring and management
5. Comprehensive reporting and analytics
6. NPHIES-compliant communication management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os

from .communication.workflow_orchestrator import CommunicationWorkflowOrchestrator
from .communication.patient_communication_service import (
    PatientCommunicationData, AppointmentData, Language, CommunicationChannel, MessagePriority
)
from .communication.workflows.visit_workflow import ProviderData, ProviderType
from .communication.workflows.post_visit_workflow import PostVisitData, FollowUpType
from .communication.workflows.clinical_results_workflow import (
    ClinicalResult, ResultType, ResultSeverity, ProviderNotificationData
)
from .communication.workflows.emergency_workflow import (
    EmergencyEvent, EmergencyType, EmergencyLevel, EmergencyContact, ContactRole
)

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Initialize router
communication_router = APIRouter(
    prefix="/api/v1/communication",
    tags=["Patient Communication Workflows"],
    responses={404: {"description": "Not found"}},
)

# Global orchestrator instance (in production, this would be dependency-injected)
orchestrator: Optional[CommunicationWorkflowOrchestrator] = None

def get_orchestrator() -> CommunicationWorkflowOrchestrator:
    """Get communication orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        # Initialize with environment variables
        orchestrator = CommunicationWorkflowOrchestrator(
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER", ""),
            encryption_key=os.getenv("HEALTHCARE_ENCRYPTION_KEY")
        )
    return orchestrator

# ==================== REQUEST/RESPONSE MODELS ====================

class PatientCommunicationRequest(BaseModel):
    """Patient communication data request model"""
    patient_id: str = Field(..., description="Unique patient identifier")
    national_id: Optional[str] = Field(None, description="Saudi National ID")
    nphies_id: Optional[str] = Field(None, description="NPHIES patient identifier")
    phone_number: str = Field(..., description="Patient phone number")
    email: Optional[str] = Field(None, description="Patient email address")
    preferred_language: Language = Field(Language.ARABIC, description="Preferred communication language")
    preferred_channels: List[CommunicationChannel] = Field(
        default=[CommunicationChannel.SMS], 
        description="Preferred communication channels"
    )
    emergency_contact: Optional[str] = Field(None, description="Emergency contact phone number")
    consent_sms: bool = Field(True, description="SMS communication consent")
    consent_voice: bool = Field(True, description="Voice communication consent")
    consent_whatsapp: bool = Field(False, description="WhatsApp communication consent")
    consent_email: bool = Field(True, description="Email communication consent")

class AppointmentRequest(BaseModel):
    """Appointment data request model"""
    appointment_id: str = Field(..., description="Unique appointment identifier")
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Provider identifier")
    provider_name: str = Field(..., description="Provider name in English")
    provider_name_ar: Optional[str] = Field(None, description="Provider name in Arabic")
    appointment_datetime: datetime = Field(..., description="Appointment date and time")
    appointment_type: str = Field(..., description="Type of appointment")
    department: str = Field(..., description="Department name in English")
    department_ar: Optional[str] = Field(None, description="Department name in Arabic")
    location: str = Field(..., description="Appointment location in English")
    location_ar: Optional[str] = Field(None, description="Appointment location in Arabic")
    estimated_duration: int = Field(30, description="Estimated duration in minutes")
    instructions: Optional[str] = Field(None, description="Special instructions in English")
    instructions_ar: Optional[str] = Field(None, description="Special instructions in Arabic")

class ProviderRequest(BaseModel):
    """Provider data request model"""
    provider_id: str = Field(..., description="Provider identifier")
    name: str = Field(..., description="Provider name in English")
    name_ar: Optional[str] = Field(None, description="Provider name in Arabic")
    phone_number: str = Field(..., description="Provider phone number")
    email: Optional[str] = Field(None, description="Provider email")
    provider_type: ProviderType = Field(ProviderType.PRIMARY_PROVIDER, description="Provider type")
    preferred_language: Language = Field(Language.ENGLISH, description="Provider preferred language")
    notification_preferences: List[CommunicationChannel] = Field(
        default=[CommunicationChannel.SMS], 
        description="Provider notification preferences"
    )

class ClinicalResultRequest(BaseModel):
    """Clinical result data request model"""
    result_id: str = Field(..., description="Unique result identifier")
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Provider identifier")
    result_type: ResultType = Field(..., description="Type of clinical result")
    test_name: str = Field(..., description="Test name in English")
    test_name_ar: Optional[str] = Field(None, description="Test name in Arabic")
    result_value: Optional[str] = Field(None, description="Result value")
    reference_range: Optional[str] = Field(None, description="Reference range")
    severity: ResultSeverity = Field(ResultSeverity.NORMAL, description="Result severity")
    abnormal_flags: List[str] = Field(default=[], description="Abnormal flags")
    interpretation: Optional[str] = Field(None, description="Result interpretation in English")
    interpretation_ar: Optional[str] = Field(None, description="Result interpretation in Arabic")
    follow_up_required: bool = Field(False, description="Whether follow-up is required")
    follow_up_timeframe: Optional[str] = Field(None, description="Follow-up timeframe")
    result_date: Optional[datetime] = Field(None, description="Result date")

class EmergencyEventRequest(BaseModel):
    """Emergency event data request model"""
    event_id: str = Field(..., description="Unique emergency event identifier")
    emergency_type: EmergencyType = Field(..., description="Type of emergency")
    emergency_level: EmergencyLevel = Field(..., description="Emergency severity level")
    patient_id: Optional[str] = Field(None, description="Patient ID if patient-specific emergency")
    location: str = Field(..., description="Emergency location in English")
    location_ar: Optional[str] = Field(None, description="Emergency location in Arabic")
    description: str = Field(..., description="Emergency description in English")
    description_ar: Optional[str] = Field(None, description="Emergency description in Arabic")
    initiated_by: str = Field(..., description="Person who initiated the emergency")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    affected_areas: List[str] = Field(default=[], description="Affected facility areas")
    required_actions: List[str] = Field(default=[], description="Required actions")
    contact_emergency_services: bool = Field(False, description="Whether to contact emergency services")
    evacuation_required: bool = Field(False, description="Whether evacuation is required")

class EmergencyContactRequest(BaseModel):
    """Emergency contact data request model"""
    contact_id: str = Field(..., description="Contact identifier")
    name: str = Field(..., description="Contact name in English")
    name_ar: Optional[str] = Field(None, description="Contact name in Arabic")
    role: ContactRole = Field(..., description="Contact role")
    phone_number: str = Field(..., description="Contact phone number")
    backup_phone: Optional[str] = Field(None, description="Backup phone number")
    email: Optional[str] = Field(None, description="Contact email")
    preferred_language: Language = Field(Language.ENGLISH, description="Preferred language")
    notification_preferences: List[CommunicationChannel] = Field(
        default=[CommunicationChannel.VOICE, CommunicationChannel.SMS],
        description="Notification preferences"
    )
    priority_order: int = Field(1, description="Contact priority order")

class WorkflowResponse(BaseModel):
    """Standard workflow response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    execution_id: Optional[str] = Field(None, description="Workflow execution identifier")
    workflow_id: Optional[str] = Field(None, description="Workflow identifier")
    status: str = Field(..., description="Workflow status")
    message: Optional[str] = Field(None, description="Status message")
    audit_id: Optional[str] = Field(None, description="Audit record identifier")
    compliance_status: Optional[str] = Field(None, description="HIPAA compliance status")
    errors: List[str] = Field(default=[], description="Error messages if any")
    warnings: List[str] = Field(default=[], description="Warning messages if any")

# ==================== AUTHENTICATION AND AUTHORIZATION ====================

async def verify_healthcare_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify healthcare API token"""
    try:
        token = credentials.credentials
        # In production, this would validate against a proper auth service
        if not token or len(token) < 32:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==================== MAIN WORKFLOW ENDPOINTS ====================

@communication_router.post("/patient-journey", response_model=WorkflowResponse)
async def initiate_patient_journey(
    patient_data: PatientCommunicationRequest,
    appointment_data: AppointmentRequest,
    provider_data: ProviderRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = Query(None, description="User ID initiating the journey"),
    token: str = Depends(verify_healthcare_token)
) -> WorkflowResponse:
    """
    Initiate complete patient communication journey from pre-visit through post-visit
    
    This is the main endpoint for starting comprehensive patient communications
    """
    try:
        orchestrator = get_orchestrator()
        
        # Convert request models to internal models
        patient_comm_data = PatientCommunicationData(
            patient_id=patient_data.patient_id,
            national_id=patient_data.national_id,
            nphies_id=patient_data.nphies_id,
            phone_number=patient_data.phone_number,
            email=patient_data.email,
            preferred_language=patient_data.preferred_language,
            preferred_channels=patient_data.preferred_channels,
            emergency_contact=patient_data.emergency_contact,
            consent_sms=patient_data.consent_sms,
            consent_voice=patient_data.consent_voice,
            consent_whatsapp=patient_data.consent_whatsapp,
            consent_email=patient_data.consent_email
        )
        
        appointment_internal = AppointmentData(
            appointment_id=appointment_data.appointment_id,
            patient_id=appointment_data.patient_id,
            provider_id=appointment_data.provider_id,
            provider_name=appointment_data.provider_name,
            provider_name_ar=appointment_data.provider_name_ar,
            appointment_datetime=appointment_data.appointment_datetime,
            appointment_type=appointment_data.appointment_type,
            department=appointment_data.department,
            department_ar=appointment_data.department_ar,
            location=appointment_data.location,
            location_ar=appointment_data.location_ar,
            estimated_duration=appointment_data.estimated_duration,
            instructions=appointment_data.instructions,
            instructions_ar=appointment_data.instructions_ar
        )
        
        provider_internal = ProviderData(
            provider_id=provider_data.provider_id,
            name=provider_data.name,
            name_ar=provider_data.name_ar,
            phone_number=provider_data.phone_number,
            email=provider_data.email,
            provider_type=provider_data.provider_type,
            preferred_language=provider_data.preferred_language,
            notification_preferences=provider_data.notification_preferences
        )
        
        # Execute patient journey
        result = await orchestrator.initiate_patient_journey(
            patient_comm_data, appointment_internal, provider_internal, user_id
        )
        
        if result["success"]:
            return WorkflowResponse(
                success=True,
                execution_id=result.get("journey_id"),
                status="initiated",
                message="Patient journey initiated successfully",
                compliance_status="compliant"
            )
        else:
            return WorkflowResponse(
                success=False,
                status="failed",
                message="Failed to initiate patient journey",
                errors=[result.get("error", "Unknown error")]
            )
            
    except Exception as e:
        logger.error(f"Patient journey initiation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate patient journey: {str(e)}"
        )

@communication_router.post("/pre-visit-workflow", response_model=WorkflowResponse)
async def execute_pre_visit_workflow(
    patient_data: PatientCommunicationRequest,
    appointment_data: AppointmentRequest,
    user_id: Optional[str] = Query(None, description="User ID executing the workflow"),
    token: str = Depends(verify_healthcare_token)
) -> WorkflowResponse:
    """Execute pre-visit communication workflow"""
    try:
        orchestrator = get_orchestrator()
        
        # Convert to internal models
        patient_comm_data = PatientCommunicationData(**patient_data.dict())
        appointment_internal = AppointmentData(**appointment_data.dict())
        
        # Execute workflow
        result = await orchestrator.execute_pre_visit_workflow(
            patient_comm_data, appointment_internal, user_id
        )
        
        return WorkflowResponse(
            success=result.get("status") != "failed",
            execution_id=result.get("execution_id"),
            status=result.get("status", "unknown"),
            message="Pre-visit workflow executed",
            errors=[result.get("error")] if result.get("error") else []
        )
        
    except Exception as e:
        logger.error(f"Pre-visit workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pre-visit workflow failed: {str(e)}"
        )

@communication_router.post("/clinical-results-workflow", response_model=WorkflowResponse)
async def execute_clinical_results_workflow(
    patient_data: PatientCommunicationRequest,
    clinical_result: ClinicalResultRequest,
    provider_data: ProviderRequest,
    user_id: Optional[str] = Query(None, description="User ID executing the workflow"),
    token: str = Depends(verify_healthcare_token)
) -> WorkflowResponse:
    """Execute clinical results communication workflow"""
    try:
        orchestrator = get_orchestrator()
        
        # Convert to internal models
        patient_comm_data = PatientCommunicationData(**patient_data.dict())
        
        clinical_result_internal = ClinicalResult(
            result_id=clinical_result.result_id,
            patient_id=clinical_result.patient_id,
            provider_id=clinical_result.provider_id,
            result_type=clinical_result.result_type,
            test_name=clinical_result.test_name,
            test_name_ar=clinical_result.test_name_ar,
            result_value=clinical_result.result_value,
            reference_range=clinical_result.reference_range,
            severity=clinical_result.severity,
            abnormal_flags=clinical_result.abnormal_flags,
            interpretation=clinical_result.interpretation,
            interpretation_ar=clinical_result.interpretation_ar,
            follow_up_required=clinical_result.follow_up_required,
            follow_up_timeframe=clinical_result.follow_up_timeframe,
            result_date=clinical_result.result_date or datetime.now()
        )
        
        provider_notification = ProviderNotificationData(
            provider_id=provider_data.provider_id,
            name=provider_data.name,
            name_ar=provider_data.name_ar,
            phone_number=provider_data.phone_number,
            email=provider_data.email,
            preferred_language=provider_data.preferred_language,
            notification_preferences=provider_data.notification_preferences
        )
        
        # Execute workflow
        result = await orchestrator.execute_clinical_results_workflow(
            patient_comm_data, clinical_result_internal, provider_notification, user_id
        )
        
        return WorkflowResponse(
            success=result.get("status") != "failed",
            execution_id=result.get("execution_id"),
            status=result.get("status", "unknown"),
            message="Clinical results workflow executed",
            errors=[result.get("error")] if result.get("error") else []
        )
        
    except Exception as e:
        logger.error(f"Clinical results workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical results workflow failed: {str(e)}"
        )

@communication_router.post("/emergency-workflow", response_model=WorkflowResponse)
async def execute_emergency_workflow(
    emergency_event: EmergencyEventRequest,
    emergency_contacts: List[EmergencyContactRequest],
    patient_data: Optional[PatientCommunicationRequest] = None,
    user_id: Optional[str] = Query(None, description="User ID executing the workflow"),
    token: str = Depends(verify_healthcare_token)
) -> WorkflowResponse:
    """Execute emergency communication workflow"""
    try:
        orchestrator = get_orchestrator()
        
        # Convert to internal models
        emergency_event_internal = EmergencyEvent(
            event_id=emergency_event.event_id,
            emergency_type=emergency_event.emergency_type,
            emergency_level=emergency_event.emergency_level,
            patient_id=emergency_event.patient_id,
            location=emergency_event.location,
            location_ar=emergency_event.location_ar,
            description=emergency_event.description,
            description_ar=emergency_event.description_ar,
            initiated_by=emergency_event.initiated_by,
            estimated_duration=emergency_event.estimated_duration,
            affected_areas=emergency_event.affected_areas,
            required_actions=emergency_event.required_actions,
            contact_emergency_services=emergency_event.contact_emergency_services,
            evacuation_required=emergency_event.evacuation_required
        )
        
        emergency_contacts_internal = [
            EmergencyContact(
                contact_id=contact.contact_id,
                name=contact.name,
                name_ar=contact.name_ar,
                role=contact.role,
                phone_number=contact.phone_number,
                backup_phone=contact.backup_phone,
                email=contact.email,
                preferred_language=contact.preferred_language,
                notification_preferences=contact.notification_preferences,
                priority_order=contact.priority_order
            ) for contact in emergency_contacts
        ]
        
        patient_comm_data = None
        if patient_data:
            patient_comm_data = PatientCommunicationData(**patient_data.dict())
        
        # Execute workflow
        result = await orchestrator.execute_emergency_workflow(
            emergency_event_internal, emergency_contacts_internal, patient_comm_data, user_id
        )
        
        return WorkflowResponse(
            success=result.get("status") != "failed",
            execution_id=result.get("execution_id"),
            status=result.get("status", "unknown"),
            message="Emergency workflow executed",
            errors=[result.get("error")] if result.get("error") else []
        )
        
    except Exception as e:
        logger.error(f"Emergency workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Emergency workflow failed: {str(e)}"
        )

# ==================== MONITORING AND MANAGEMENT ENDPOINTS ====================

@communication_router.get("/workflow/{execution_id}/status")
async def get_workflow_status(
    execution_id: str,
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Get workflow execution status"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.get_workflow_status(execution_id)
        
        if result.get("status") == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution {execution_id} not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@communication_router.get("/workflows/active")
async def get_active_workflows(
    token: str = Depends(verify_healthcare_token)
) -> List[Dict[str, Any]]:
    """Get all active workflow executions"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.get_active_workflows()
        return result
        
    except Exception as e:
        logger.error(f"Failed to get active workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active workflows: {str(e)}"
        )

@communication_router.get("/system/health")
async def get_system_health(
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Get communication system health status"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.get_system_health()
        return result
        
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@communication_router.get("/compliance/report")
async def generate_compliance_report(
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Generate HIPAA compliance report"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.generate_compliance_report(start_date, end_date)
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {str(e)}"
        )

@communication_router.post("/system/cleanup")
async def cleanup_completed_workflows(
    older_than_hours: int = Query(24, description="Clean up workflows older than X hours"),
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Clean up completed workflow executions"""
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.cleanup_completed_workflows(older_than_hours)
        return result
        
    except Exception as e:
        logger.error(f"Failed to cleanup workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup workflows: {str(e)}"
        )

# ==================== TEMPLATE AND COMPLIANCE ENDPOINTS ====================

@communication_router.get("/templates")
async def get_message_templates(
    category: Optional[str] = Query(None, description="Template category filter"),
    language: Optional[str] = Query(None, description="Language filter (ar/en)"),
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Get available message templates"""
    try:
        orchestrator = get_orchestrator()
        
        if category:
            templates = orchestrator.arabic_templates.get_templates_by_category(category)
        else:
            templates = list(orchestrator.arabic_templates.templates.values())
        
        template_list = []
        for template in templates:
            template_info = {
                "template_id": template.template_id,
                "template_name": template.template_name,
                "template_name_ar": template.template_name_ar,
                "category": template.category,
                "compliance_level": template.compliance_level.value,
                "variables": template.variables,
                "nphies_message_type": template.nphies_message_type.value if template.nphies_message_type else None
            }
            
            if language == "ar":
                template_info["subject"] = template.subject_ar
                template_info["content"] = template.content_ar
            elif language == "en":
                template_info["subject"] = template.subject_en
                template_info["content"] = template.content_en
            
            template_list.append(template_info)
        
        return {
            "templates": template_list,
            "total_count": len(template_list),
            "categories": list(set(t.category for t in templates))
        }
        
    except Exception as e:
        logger.error(f"Failed to get message templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message templates: {str(e)}"
        )

@communication_router.get("/templates/{template_id}/validate")
async def validate_template_compliance(
    template_id: str,
    token: str = Depends(verify_healthcare_token)
) -> Dict[str, Any]:
    """Validate template compliance"""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.arabic_templates.validate_template_compliance(template_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to validate template compliance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate template compliance: {str(e)}"
        )

# Export router
__all__ = ["communication_router"]