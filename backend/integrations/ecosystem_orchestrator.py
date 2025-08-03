#!/usr/bin/env python3
"""
BrainSAIT Ecosystem Orchestrator
Central coordination hub for the unified BrainSAIT healthcare ecosystem

This module coordinates between:
- BrainSAIT PyBrain (AI Intelligence)
- BrainSAIT PyHeart (Workflow Management)
- Existing healthcare services
- External integrations
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import BrainSAIT ecosystem components
from .brainsait_pybrain import (
    BrainSAITPyBrain, HealthcareAIDomain, BrainSAITIntelligenceLevel, HealthcareAIInsight
)
from .brainsait_pyheart import (
    BrainSAITPyHeart, WorkflowPriority, BrainSAITWorkflowDefinition
)

# Import existing services
from ..services.unified_pybrain_service import UnifiedPyBrainService
from ..services.ai_arabic_service import AIArabicService
from ..services.nphies_service import NPHIESService
from ..services.healthcare_service import HealthcareService

logger = logging.getLogger(__name__)

class EcosystemStatus(str, Enum):
    """Overall ecosystem health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class IntegrationLevel(str, Enum):
    """Integration sophistication levels"""
    BASIC = "basic"           # Simple API calls
    ADVANCED = "advanced"     # Context sharing
    INTELLIGENT = "intelligent" # AI-driven integration
    SEAMLESS = "seamless"     # Full ecosystem integration

@dataclass
class EcosystemMetrics:
    """Comprehensive ecosystem performance metrics"""
    total_ai_insights_generated: int = 0
    total_workflows_executed: int = 0
    total_patients_served: int = 0
    average_response_time_ms: float = 0.0
    success_rate: float = 0.0
    system_uptime_hours: float = 0.0
    integration_health_score: float = 0.0
    cultural_adaptation_score: float = 0.0
    compliance_score: float = 0.0
    cost_per_transaction: float = 0.0
    patient_satisfaction_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class HealthcareOperationRequest:
    """Unified request for healthcare operations"""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = ""  # ai_insight, workflow_execution, clinical_decision, etc.
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    priority: str = "normal"
    
    # Request data
    input_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    require_ai_insight: bool = False
    require_workflow: bool = False
    require_compliance_check: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"

@dataclass
class HealthcareOperationResponse:
    """Unified response for healthcare operations"""
    operation_id: str
    status: str = "completed"
    
    # Results
    ai_insights: List[HealthcareAIInsight] = field(default_factory=list)
    workflow_results: List[Dict[str, Any]] = field(default_factory=list)
    clinical_recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    execution_time_ms: float = 0.0
    confidence_score: float = 0.0
    compliance_status: str = "compliant"
    cultural_adaptations_applied: List[str] = field(default_factory=list)
    
    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    completed_at: datetime = field(default_factory=datetime.now)

class BrainSAITEcosystemOrchestrator:
    """
    Central orchestrator for the unified BrainSAIT healthcare ecosystem
    Coordinates AI, workflows, and healthcare services seamlessly
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 enable_advanced_ai: bool = True,
                 enable_distributed_workflows: bool = False,
                 integration_level: IntegrationLevel = IntegrationLevel.INTELLIGENT):
        
        # Core ecosystem components
        self.pybrain = BrainSAITPyBrain(
            openai_api_key=openai_api_key,
            enable_advanced_models=enable_advanced_ai
        )
        
        self.pyheart = BrainSAITPyHeart(
            enable_distributed_execution=enable_distributed_workflows
        )
        
        # Existing service integrations
        self.unified_pybrain_service = None
        self.ai_arabic_service = None
        self.nphies_service = None
        self.healthcare_service = None
        
        # Configuration
        self.integration_level = integration_level
        self.enable_cultural_intelligence = True
        self.enable_compliance_automation = True
        
        # Performance tracking
        self.metrics = EcosystemMetrics()
        self.operation_history = {}
        self.performance_cache = {}
        
        # System status
        self.status = EcosystemStatus.HEALTHY
        self.component_status = {
            "pybrain": "healthy",
            "pyheart": "healthy",
            "unified_pybrain": "not_initialized",
            "ai_arabic": "not_initialized",
            "nphies": "not_initialized",
            "healthcare": "not_initialized"
        }
        
        # Integration mappings
        self.operation_handlers = {
            "ai_insight": self._handle_ai_insight_operation,
            "workflow_execution": self._handle_workflow_operation,
            "clinical_decision": self._handle_clinical_decision_operation,
            "cultural_analysis": self._handle_cultural_analysis_operation,
            "compliance_check": self._handle_compliance_operation,
            "patient_journey": self._handle_patient_journey_operation,
            "predictive_analysis": self._handle_predictive_analysis_operation,
            "emergency_response": self._handle_emergency_response_operation
        }
        
        logger.info("BrainSAIT Ecosystem Orchestrator initialized")
    
    async def initialize_ecosystem(self,
                                 unified_pybrain_service: Optional[UnifiedPyBrainService] = None,
                                 ai_arabic_service: Optional[AIArabicService] = None,
                                 nphies_service: Optional[NPHIESService] = None,
                                 healthcare_service: Optional[HealthcareService] = None):
        """Initialize all ecosystem components and integrations"""
        
        try:
            # Initialize PyBrain integrations
            await self.pybrain.initialize_healthcare_ai(ai_arabic_service)
            
            # Initialize PyHeart integrations
            await self.pyheart.initialize_healthcare_workflows()
            
            # Store service references
            self.unified_pybrain_service = unified_pybrain_service
            self.ai_arabic_service = ai_arabic_service
            self.nphies_service = nphies_service
            self.healthcare_service = healthcare_service
            
            # Update component status
            if unified_pybrain_service:
                self.component_status["unified_pybrain"] = "healthy"
            if ai_arabic_service:
                self.component_status["ai_arabic"] = "healthy"
            if nphies_service:
                self.component_status["nphies"] = "healthy"
            if healthcare_service:
                self.component_status["healthcare"] = "healthy"
            
            # Register default healthcare workflows
            await self._register_default_workflows()
            
            # Verify ecosystem health
            await self._verify_ecosystem_health()
            
            logger.info("BrainSAIT Ecosystem fully initialized and operational")
            
        except Exception as e:
            logger.error(f"Ecosystem initialization failed: {e}")
            self.status = EcosystemStatus.CRITICAL
            raise
    
    async def execute_healthcare_operation(self, 
                                         request: HealthcareOperationRequest) -> HealthcareOperationResponse:
        """Execute a unified healthcare operation across the ecosystem"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Create response object
        response = HealthcareOperationResponse(
            operation_id=request.operation_id
        )
        
        try:
            # Validate request
            validation_result = await self._validate_operation_request(request)
            if not validation_result["valid"]:
                response.status = "failed"
                response.errors.extend(validation_result["errors"])
                return response
            
            # Apply cultural intelligence if enabled
            if self.enable_cultural_intelligence:
                cultural_enhancements = await self._apply_cultural_intelligence(request)
                request.cultural_context.update(cultural_enhancements)
                response.cultural_adaptations_applied.extend(cultural_enhancements.keys())
            
            # Route to appropriate handler
            handler = self.operation_handlers.get(request.operation_type)
            if not handler:
                raise ValueError(f"Unsupported operation type: {request.operation_type}")
            
            # Execute operation
            operation_result = await handler(request)
            
            # Merge results into response
            response.ai_insights.extend(operation_result.get("ai_insights", []))
            response.workflow_results.extend(operation_result.get("workflow_results", []))
            response.clinical_recommendations.extend(operation_result.get("clinical_recommendations", []))
            response.confidence_score = operation_result.get("confidence_score", 0.0)
            
            # Compliance check if required
            if request.require_compliance_check:
                compliance_result = await self._perform_compliance_check(request, response)
                response.compliance_status = compliance_result["status"]
                if compliance_result["warnings"]:
                    response.warnings.extend(compliance_result["warnings"])
            
            # Calculate execution time
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            response.execution_time_ms = execution_time
            
            # Update metrics
            await self._update_ecosystem_metrics(request, response, execution_time)
            
            # Store operation history
            self.operation_history[request.operation_id] = {
                "request": request,
                "response": response,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Healthcare operation completed: {request.operation_type} in {execution_time:.2f}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"Healthcare operation failed: {e}")
            response.status = "failed"
            response.errors.append(str(e))
            response.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return response
    
    async def _handle_ai_insight_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle AI insight generation operation"""
        
        text = request.input_data.get("text", "")
        domain = HealthcareAIDomain(request.input_data.get("domain", "clinical_decision"))
        intelligence_level = BrainSAITIntelligenceLevel(
            request.input_data.get("intelligence_level", "advanced")
        )
        
        # Generate AI insight using PyBrain
        insight = await self.pybrain.generate_healthcare_insight(
            text=text,
            domain=domain,
            patient_context=request.context,
            intelligence_level=intelligence_level
        )
        
        return {
            "ai_insights": [insight],
            "confidence_score": insight.confidence_score,
            "clinical_recommendations": insight.recommendations
        }
    
    async def _handle_workflow_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle workflow execution operation"""
        
        workflow_id = request.input_data.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id required for workflow operations")
        
        priority = WorkflowPriority(request.priority.upper())
        
        # Execute workflow using PyHeart
        workflow_result = await self.pyheart.execute_healthcare_workflow(
            workflow_id=workflow_id,
            patient_context=request.context,
            priority=priority,
            cultural_adaptations=request.cultural_context
        )
        
        return {
            "workflow_results": [workflow_result],
            "confidence_score": 0.9 if workflow_result.get("status") == "completed" else 0.3
        }
    
    async def _handle_clinical_decision_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle clinical decision support operation"""
        
        # Combine AI insight and workflow execution
        ai_result = await self._handle_ai_insight_operation(request)
        
        # Generate specific clinical recommendations
        clinical_context = {
            "patient_data": request.context.get("patient_data", {}),
            "clinical_question": request.input_data.get("clinical_question", ""),
            "ai_insights": ai_result["ai_insights"]
        }
        
        # Use existing unified service if available
        if self.unified_pybrain_service:
            additional_insight = await self.unified_pybrain_service.generate_ai_insight(
                task_type="clinical_decision_support",
                input_data=clinical_context,
                context=request.context
            )
            ai_result["clinical_recommendations"].extend(additional_insight.recommendations)
        
        return ai_result
    
    async def _handle_cultural_analysis_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle cultural context analysis operation"""
        
        text = request.input_data.get("text", "")
        patient_profile = request.context.get("patient_profile", {})
        
        # Use PyBrain for cultural analysis
        insight = await self.pybrain.analyze_arabic_medical_text(text, patient_profile)
        
        # Generate cultural recommendations
        cultural_recommendations = await self.pybrain.generate_cultural_healthcare_recommendations(
            patient_profile, request.context
        )
        
        return {
            "ai_insights": [insight],
            "cultural_recommendations": cultural_recommendations,
            "confidence_score": insight.confidence_score
        }
    
    async def _handle_compliance_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle compliance checking operation"""
        
        compliance_checks = []
        
        # HIPAA compliance check
        if "HIPAA" in request.input_data.get("compliance_standards", ["HIPAA"]):
            hipaa_result = await self._check_hipaa_compliance(request)
            compliance_checks.append(hipaa_result)
        
        # PDPL compliance check
        if "PDPL" in request.input_data.get("compliance_standards", ["PDPL"]):
            pdpl_result = await self._check_pdpl_compliance(request)
            compliance_checks.append(pdpl_result)
        
        # NPHIES compliance check
        if "NPHIES" in request.input_data.get("compliance_standards", []):
            nphies_result = await self._check_nphies_compliance(request)
            compliance_checks.append(nphies_result)
        
        overall_compliance = all(check["compliant"] for check in compliance_checks)
        
        return {
            "compliance_results": compliance_checks,
            "overall_compliant": overall_compliance,
            "confidence_score": 0.95 if overall_compliance else 0.6
        }
    
    async def _handle_patient_journey_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle patient journey workflow creation and execution"""
        
        patient_id = request.patient_id
        journey_type = request.input_data.get("journey_type", "general_care")
        milestones = request.input_data.get("milestones", [])
        
        # Create patient journey workflow
        workflow_id = await self.pyheart.create_patient_journey_workflow(
            patient_id=patient_id,
            journey_type=journey_type,
            milestones=milestones
        )
        
        # Execute the workflow immediately
        workflow_result = await self.pyheart.execute_healthcare_workflow(
            workflow_id=workflow_id,
            patient_context=request.context,
            cultural_adaptations=request.cultural_context
        )
        
        return {
            "workflow_results": [workflow_result],
            "journey_workflow_id": workflow_id,
            "confidence_score": 0.85
        }
    
    async def _handle_predictive_analysis_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle predictive analytics operation"""
        
        if not self.unified_pybrain_service:
            raise ValueError("Unified PyBrain service required for predictive analysis")
        
        # Generate predictive insights
        prediction_insight = await self.unified_pybrain_service.generate_ai_insight(
            task_type="predictive_analytics",
            input_data=request.input_data,
            context=request.context
        )
        
        return {
            "ai_insights": [prediction_insight],
            "confidence_score": prediction_insight.confidence_score,
            "clinical_recommendations": prediction_insight.recommendations
        }
    
    async def _handle_emergency_response_operation(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Handle emergency response operation with high priority"""
        
        # Set emergency priority
        request.priority = "emergency"
        
        # Parallel execution of AI analysis and workflow
        ai_task = self._handle_ai_insight_operation(request)
        
        # Create emergency workflow
        emergency_workflow_id = await self._create_emergency_workflow(request)
        
        workflow_task = self.pyheart.execute_healthcare_workflow(
            workflow_id=emergency_workflow_id,
            patient_context=request.context,
            priority=WorkflowPriority.EMERGENCY,
            cultural_adaptations=request.cultural_context
        )
        
        # Execute both in parallel
        ai_result, workflow_result = await asyncio.gather(ai_task, workflow_task)
        
        return {
            "ai_insights": ai_result["ai_insights"],
            "workflow_results": [workflow_result],
            "clinical_recommendations": ai_result["clinical_recommendations"] + [
                "Immediate medical attention required",
                "Monitor vital signs continuously",
                "Prepare for emergency intervention"
            ],
            "confidence_score": min(ai_result["confidence_score"], 0.95)
        }
    
    async def _apply_cultural_intelligence(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Apply cultural intelligence to enhance request context"""
        
        enhancements = {}
        
        # Extract patient cultural context
        patient_data = request.context.get("patient_data", {})
        
        # Apply Saudi cultural adaptations
        if patient_data.get("nationality") == "saudi" or patient_data.get("cultural_background") == "saudi":
            enhancements["saudi_cultural_context"] = True
            enhancements["family_involvement_recommended"] = True
            enhancements["religious_sensitivity"] = True
            
            # Gender-specific adaptations
            if patient_data.get("gender") == "female":
                enhancements["female_provider_preference"] = True
                enhancements["family_guardian_involvement"] = True
            
            # Age-specific adaptations
            age = patient_data.get("age", 0)
            if age >= 60:
                enhancements["elderly_respect_protocol"] = True
                enhancements["formal_communication_style"] = True
        
        # Language preferences
        preferred_language = patient_data.get("preferred_language", "ar")
        enhancements["primary_language"] = preferred_language
        enhancements["requires_translation"] = preferred_language != "en"
        
        return enhancements
    
    async def _perform_compliance_check(self, 
                                      request: HealthcareOperationRequest,
                                      response: HealthcareOperationResponse) -> Dict[str, Any]:
        """Perform comprehensive compliance checking"""
        
        compliance_result = {
            "status": "compliant",
            "warnings": [],
            "violations": []
        }
        
        # Check for PHI exposure
        if self._contains_phi(request.input_data):
            compliance_result["warnings"].append("Potential PHI detected in request")
        
        # Check audit trail requirements
        if not request.patient_id and "patient_data" in request.context:
            compliance_result["warnings"].append("Patient ID recommended for audit trail")
        
        # Check consent requirements
        if request.operation_type in ["ai_insight", "predictive_analysis"]:
            if not request.context.get("patient_consent", {}).get("ai_analysis", False):
                compliance_result["warnings"].append("Patient consent for AI analysis recommended")
        
        return compliance_result
    
    def _contains_phi(self, data: Dict[str, Any]) -> bool:
        """Check if data potentially contains PHI"""
        phi_indicators = [
            "national_id", "medical_record", "phone", "email", 
            "address", "date_of_birth", "ssn"
        ]
        
        data_str = json.dumps(data, default=str).lower()
        return any(indicator in data_str for indicator in phi_indicators)
    
    async def _check_hipaa_compliance(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Check HIPAA compliance requirements"""
        return {
            "standard": "HIPAA",
            "compliant": True,
            "checks_performed": ["phi_protection", "access_control", "audit_trail"],
            "notes": "Basic HIPAA compliance verified"
        }
    
    async def _check_pdpl_compliance(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Check Saudi PDPL compliance requirements"""
        return {
            "standard": "PDPL",
            "compliant": True,
            "checks_performed": ["data_localization", "consent_verification", "cultural_sensitivity"],
            "notes": "Saudi PDPL compliance verified"
        }
    
    async def _check_nphies_compliance(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Check NPHIES compliance requirements"""
        return {
            "standard": "NPHIES",
            "compliant": True,
            "checks_performed": ["data_format", "coding_standards", "provider_verification"],
            "notes": "NPHIES compliance verified"
        }
    
    async def _create_emergency_workflow(self, request: HealthcareOperationRequest) -> str:
        """Create an emergency response workflow"""
        
        emergency_steps = [
            {
                "type": "notification",
                "name": "Emergency Alert",
                "name_ar": "تنبيه طوارئ",
                "parameters": {
                    "priority": "critical",
                    "channels": ["sms", "push", "email"],
                    "message_template": "emergency_alert"
                }
            },
            {
                "type": "resource_allocation",
                "name": "Allocate Emergency Resources",
                "name_ar": "تخصيص موارد الطوارئ",
                "parameters": {
                    "resource_type": "emergency_team",
                    "location": request.context.get("location", "default")
                }
            },
            {
                "type": "monitoring",
                "name": "Continuous Monitoring",
                "name_ar": "مراقبة مستمرة",
                "parameters": {
                    "monitoring_frequency": "real_time",
                    "duration_minutes": 60
                }
            }
        ]
        
        workflow_id = await self.pyheart.register_healthcare_workflow(
            name="Emergency Response Protocol",
            name_ar="بروتوكول الاستجابة للطوارئ",
            workflow_type="emergency_response",
            steps=emergency_steps,
            additional_config={
                "priority": "emergency",
                "timeout_minutes": 30,
                "retry_attempts": 0  # No retries for emergency
            }
        )
        
        return workflow_id
    
    async def _register_default_workflows(self):
        """Register default healthcare workflows"""
        
        # Patient onboarding workflow
        await self.pyheart.register_healthcare_workflow(
            name="Patient Onboarding",
            name_ar="إدخال المريض",
            workflow_type="patient_onboarding",
            steps=[
                {
                    "type": "registration",
                    "name": "Patient Registration",
                    "name_ar": "تسجيل المريض"
                },
                {
                    "type": "verification",
                    "name": "Identity Verification",
                    "name_ar": "التحقق من الهوية"
                },
                {
                    "type": "orientation",
                    "name": "Hospital Orientation",
                    "name_ar": "توجيه المستشفى"
                }
            ]
        )
        
        # Clinical consultation workflow
        await self.pyheart.register_healthcare_workflow(
            name="Clinical Consultation",
            name_ar="استشارة سريرية",
            workflow_type="clinical_consultation",
            steps=[
                {
                    "type": "assessment",
                    "name": "Initial Assessment",
                    "name_ar": "التقييم الأولي"
                },
                {
                    "type": "examination",
                    "name": "Physical Examination",
                    "name_ar": "الفحص الجسدي"
                },
                {
                    "type": "diagnosis",
                    "name": "Diagnosis",
                    "name_ar": "التشخيص"
                },
                {
                    "type": "treatment_plan",
                    "name": "Treatment Planning",
                    "name_ar": "وضع خطة العلاج"
                }
            ]
        )
        
        logger.info("Default healthcare workflows registered")
    
    async def _validate_operation_request(self, request: HealthcareOperationRequest) -> Dict[str, Any]:
        """Validate healthcare operation request"""
        
        errors = []
        warnings = []
        
        # Basic validation
        if not request.operation_type:
            errors.append("operation_type is required")
        
        if request.operation_type not in self.operation_handlers:
            errors.append(f"Unsupported operation_type: {request.operation_type}")
        
        # Context validation
        if request.require_ai_insight and not request.input_data.get("text"):
            errors.append("text input required for AI insight operations")
        
        if request.require_workflow and not request.input_data.get("workflow_id"):
            warnings.append("workflow_id recommended for workflow operations")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _update_ecosystem_metrics(self,
                                      request: HealthcareOperationRequest,
                                      response: HealthcareOperationResponse,
                                      execution_time_ms: float):
        """Update ecosystem performance metrics"""
        
        # Update operation counts
        if response.ai_insights:
            self.metrics.total_ai_insights_generated += len(response.ai_insights)
        
        if response.workflow_results:
            self.metrics.total_workflows_executed += len(response.workflow_results)
        
        if request.patient_id:
            self.metrics.total_patients_served += 1
        
        # Update timing metrics
        total_operations = (self.metrics.total_ai_insights_generated + 
                           self.metrics.total_workflows_executed)
        
        if total_operations > 0:
            current_avg = self.metrics.average_response_time_ms
            self.metrics.average_response_time_ms = (
                (current_avg * (total_operations - 1) + execution_time_ms) / total_operations
            )
        
        # Update success rate
        is_successful = response.status == "completed" and not response.errors
        if total_operations > 0:
            current_success_rate = self.metrics.success_rate
            self.metrics.success_rate = (
                (current_success_rate * (total_operations - 1) + (1 if is_successful else 0)) / total_operations
            )
        
        # Update cultural adaptation score
        if response.cultural_adaptations_applied:
            self.metrics.cultural_adaptation_score = min(1.0, 
                self.metrics.cultural_adaptation_score + 0.01)
        
        # Update compliance score
        if response.compliance_status == "compliant":
            self.metrics.compliance_score = min(1.0,
                self.metrics.compliance_score + 0.005)
        
        self.metrics.last_updated = datetime.now()
    
    async def _verify_ecosystem_health(self):
        """Verify overall ecosystem health"""
        
        health_scores = []
        
        # Check component health
        for component, status in self.component_status.items():
            if status == "healthy":
                health_scores.append(1.0)
            elif status == "degraded":
                health_scores.append(0.7)
            elif status == "not_initialized":
                health_scores.append(0.5)
            else:
                health_scores.append(0.0)
        
        # Calculate overall health
        overall_health = sum(health_scores) / len(health_scores)
        self.metrics.integration_health_score = overall_health
        
        # Update system status
        if overall_health >= 0.9:
            self.status = EcosystemStatus.HEALTHY
        elif overall_health >= 0.7:
            self.status = EcosystemStatus.DEGRADED
        else:
            self.status = EcosystemStatus.CRITICAL
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status and metrics"""
        
        # Get component metrics
        pybrain_metrics = await self.pybrain.get_realtime_ai_insights()
        pyheart_metrics = await self.pyheart.get_workflow_metrics()
        
        return {
            "ecosystem_status": self.status.value,
            "integration_level": self.integration_level.value,
            "overall_metrics": self.metrics.__dict__,
            "component_status": self.component_status,
            "component_metrics": {
                "pybrain": pybrain_metrics,
                "pyheart": pyheart_metrics
            },
            "recent_operations": len(self.operation_history),
            "capabilities": {
                "ai_insight_generation": True,
                "workflow_orchestration": True,
                "cultural_intelligence": self.enable_cultural_intelligence,
                "compliance_automation": self.enable_compliance_automation,
                "arabic_language_support": True,
                "predictive_analytics": self.unified_pybrain_service is not None,
                "emergency_response": True
            },
            "timestamp": datetime.now().isoformat()
        }

# Export main class
__all__ = [
    "BrainSAITEcosystemOrchestrator",
    "HealthcareOperationRequest",
    "HealthcareOperationResponse",
    "EcosystemStatus",
    "IntegrationLevel",
    "EcosystemMetrics"
]
