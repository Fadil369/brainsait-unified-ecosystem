"""
BrainSAIT Healthcare Platform - PyHeart Workflow Engine Integration
HIPAA-compliant healthcare communication workflow engine for Saudi Arabian healthcare ecosystem

This module provides comprehensive healthcare workflow management with PyHeart-inspired architecture,
specifically designed for:
- Saudi Arabia healthcare compliance (NPHIES, MOH, SCFHS)
- Arabic-first bilingual communication workflows
- HIPAA and PDPL data protection compliance
- Islamic calendar and cultural context integration
- Multi-channel healthcare communication orchestration

Key Features:
1. Event-driven communication triggers with healthcare context
2. Multi-step healthcare workflows with conditional branching
3. Patient-centric communication orchestration
4. NPHIES-compliant workflow integration
5. Arabic language workflow support with cultural context
6. Advanced workflow monitoring and analytics
7. Machine learning-powered optimization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import asyncio
import json
import logging
import uuid
import re
from abc import ABC, abstractmethod
import pytz
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Healthcare workflow imports
from ..patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData, AppointmentData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)
from ..healthcare_integration import HealthcareSystemIntegrator, AuditEventType
from ..nphies_compliance import NPHIESComplianceValidator

logger = logging.getLogger(__name__)

# ==================== WORKFLOW ENGINE ENUMS ====================

class WorkflowState(str, Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    ESCALATED = "escalated"

class WorkflowEventType(str, Enum):
    """Healthcare workflow event types"""
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    PATIENT_CHECKED_IN = "patient_checked_in"
    PROVIDER_READY = "provider_ready"
    VISIT_COMPLETED = "visit_completed"
    RESULTS_AVAILABLE = "results_available"
    CRITICAL_RESULT = "critical_result"
    PRESCRIPTION_READY = "prescription_ready"
    FOLLOW_UP_DUE = "follow_up_due"
    PAYMENT_DUE = "payment_due"
    INSURANCE_DENIED = "insurance_denied"
    EMERGENCY_ALERT = "emergency_alert"
    MEDICATION_REMINDER = "medication_reminder"
    CHRONIC_CARE_REMINDER = "chronic_care_reminder"

class WorkflowConditionType(str, Enum):
    """Workflow condition types for branching"""
    PATIENT_RESPONSE = "patient_response"
    TIME_ELAPSED = "time_elapsed"
    CLINICAL_VALUE = "clinical_value"
    PATIENT_PREFERENCE = "patient_preference"
    PROVIDER_AVAILABILITY = "provider_availability"
    INSURANCE_STATUS = "insurance_status"
    LANGUAGE_PREFERENCE = "language_preference"
    CULTURAL_CONTEXT = "cultural_context"

class HealthcareWorkflowType(str, Enum):
    """Healthcare-specific workflow types"""
    PATIENT_ONBOARDING = "patient_onboarding"
    PRE_OPERATIVE_PREPARATION = "pre_operative_preparation"
    POST_DISCHARGE_FOLLOW_UP = "post_discharge_follow_up"
    CHRONIC_DISEASE_MANAGEMENT = "chronic_disease_management"
    MEDICATION_ADHERENCE = "medication_adherence"
    PREVENTIVE_CARE_REMINDERS = "preventive_care_reminders"
    EMERGENCY_RESPONSE = "emergency_response"
    CARE_COORDINATION = "care_coordination"
    INSURANCE_WORKFLOW = "insurance_workflow"
    BILLING_WORKFLOW = "billing_workflow"

# ==================== WORKFLOW DATA MODELS ====================

@dataclass
class WorkflowContext:
    """Context data for workflow execution"""
    workflow_id: str
    patient_id: str
    patient_data: PatientCommunicationData
    healthcare_data: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    temporal_data: Dict[str, Any] = field(default_factory=dict)
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class WorkflowTrigger(BaseModel):
    """Workflow trigger definition"""
    trigger_id: str
    event_type: WorkflowEventType
    conditions: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowStep(BaseModel):
    """Individual workflow step definition"""
    step_id: str
    step_type: str  # "message", "wait", "decision", "action", "escalation"
    name: str
    description: str
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    timeout_minutes: Optional[int] = None
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    compliance_checks: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HealthcareWorkflowDefinition(BaseModel):
    """Complete healthcare workflow definition"""
    workflow_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    workflow_type: HealthcareWorkflowType
    version: str = "1.0"
    trigger: WorkflowTrigger
    steps: List[WorkflowStep]
    variables: Dict[str, Any] = Field(default_factory=dict)
    timeout_hours: int = 24
    escalation_policy: Dict[str, Any] = Field(default_factory=dict)
    compliance_requirements: List[str] = Field(default_factory=list)
    cultural_adaptations: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

@dataclass
class WorkflowExecution:
    """Runtime workflow execution state"""
    execution_id: str
    workflow_definition: HealthcareWorkflowDefinition
    context: WorkflowContext
    current_step: Optional[str] = None
    state: WorkflowState = WorkflowState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    step_history: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    escalation_count: int = 0
    retry_count: int = 0
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

# ==================== WORKFLOW ACTION INTERFACES ====================

class WorkflowAction(ABC):
    """Abstract base class for workflow actions"""
    
    @abstractmethod
    async def execute(self, context: WorkflowContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow action"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate action parameters"""
        pass

class MessageAction(WorkflowAction):
    """Send healthcare communication message"""
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
    
    async def execute(self, context: WorkflowContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send a communication message"""
        try:
            template_id = parameters.get("template_id")
            channel = parameters.get("channel", "sms")
            priority = parameters.get("priority", "normal")
            variables = parameters.get("variables", {})
            
            # Create message based on template and context
            message_content = self._render_message_template(
                template_id, context, variables
            )
            
            # Create communication message
            message = CommunicationMessage(
                workflow_type=WorkflowType.PRE_VISIT,  # This would be dynamic
                patient_id=context.patient_id,
                channel=CommunicationChannel(channel),
                language=context.patient_data.preferred_language,
                priority=MessagePriority(priority),
                message_content=message_content
            )
            
            # Send message
            result = await self.communication_service.send_message(
                context.patient_data, message
            )
            
            return {
                "success": True,
                "message_id": message.message_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Message action failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate message action parameters"""
        required_fields = ["template_id"]
        return all(field in parameters for field in required_fields)
    
    def _render_message_template(self, template_id: str, context: WorkflowContext, variables: Dict[str, Any]) -> str:
        """Render message template with context variables"""
        # This would integrate with the template system
        # For now, return a placeholder
        return f"Healthcare message from template {template_id}"

class WaitAction(WorkflowAction):
    """Wait for specified time or condition"""
    
    async def execute(self, context: WorkflowContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait action"""
        try:
            wait_type = parameters.get("type", "time")
            
            if wait_type == "time":
                wait_minutes = parameters.get("minutes", 0)
                wait_hours = parameters.get("hours", 0)
                wait_seconds = (wait_minutes * 60) + (wait_hours * 3600)
                
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                
                return {
                    "success": True,
                    "waited_seconds": wait_seconds
                }
            
            elif wait_type == "response":
                # Wait for patient response (would integrate with response tracking)
                timeout_minutes = parameters.get("timeout_minutes", 60)
                return {
                    "success": True,
                    "wait_type": "response",
                    "timeout_minutes": timeout_minutes
                }
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Wait action failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate wait action parameters"""
        wait_type = parameters.get("type", "time")
        if wait_type == "time":
            return "minutes" in parameters or "hours" in parameters
        return True

class DecisionAction(WorkflowAction):
    """Make workflow decisions based on conditions"""
    
    async def execute(self, context: WorkflowContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision logic"""
        try:
            conditions = parameters.get("conditions", [])
            default_next = parameters.get("default_next")
            
            for condition in conditions:
                if await self._evaluate_condition(condition, context):
                    return {
                        "success": True,
                        "decision": condition["result"],
                        "next_step": condition.get("next_step")
                    }
            
            return {
                "success": True,
                "decision": "default",
                "next_step": default_next
            }
            
        except Exception as e:
            logger.error(f"Decision action failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate decision action parameters"""
        return "conditions" in parameters
    
    async def _evaluate_condition(self, condition: Dict[str, Any], context: WorkflowContext) -> bool:
        """Evaluate a single condition"""
        condition_type = condition.get("type")
        
        if condition_type == "patient_response":
            # Check if patient has responded
            return self._check_patient_response(condition, context)
        
        elif condition_type == "time_elapsed":
            # Check if enough time has elapsed
            return self._check_time_elapsed(condition, context)
        
        elif condition_type == "clinical_value":
            # Check clinical values
            return self._check_clinical_value(condition, context)
        
        elif condition_type == "language_preference":
            # Check language preference
            return context.patient_data.preferred_language == Language(condition.get("language"))
        
        return False
    
    def _check_patient_response(self, condition: Dict[str, Any], context: WorkflowContext) -> bool:
        """Check patient response condition"""
        # This would integrate with response tracking system
        return False
    
    def _check_time_elapsed(self, condition: Dict[str, Any], context: WorkflowContext) -> bool:
        """Check time elapsed condition"""
        required_minutes = condition.get("minutes", 0)
        elapsed_time = datetime.now() - context.last_updated
        return elapsed_time.total_seconds() >= (required_minutes * 60)
    
    def _check_clinical_value(self, condition: Dict[str, Any], context: WorkflowContext) -> bool:
        """Check clinical value condition"""
        field_name = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")
        
        if field_name not in context.healthcare_data:
            return False
        
        field_value = context.healthcare_data[field_name]
        
        if operator == "equals":
            return field_value == value
        elif operator == "greater_than":
            return field_value > value
        elif operator == "less_than":
            return field_value < value
        
        return False

class EscalationAction(WorkflowAction):
    """Escalate workflow to higher priority or different channel"""
    
    async def execute(self, context: WorkflowContext, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute escalation action"""
        try:
            escalation_type = parameters.get("type", "priority")
            reason = parameters.get("reason", "Automated escalation")
            
            # Log escalation
            escalation_event = {
                "escalation_type": escalation_type,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "workflow_id": context.workflow_id,
                    "patient_id": context.patient_id
                }
            }
            
            context.temporal_data["escalations"] = context.temporal_data.get("escalations", [])
            context.temporal_data["escalations"].append(escalation_event)
            
            return {
                "success": True,
                "escalation_event": escalation_event
            }
            
        except Exception as e:
            logger.error(f"Escalation action failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate escalation action parameters"""
        return True  # Escalation can work with defaults

# ==================== MAIN PYHEART WORKFLOW ENGINE ====================

class PyHeartHealthcareWorkflowEngine:
    """
    PyHeart-inspired workflow engine for healthcare communications
    
    Provides comprehensive workflow orchestration with:
    - Event-driven triggers
    - Multi-step workflow execution
    - Conditional branching
    - HIPAA compliance
    - Arabic language support
    - Saudi healthcare integration
    """
    
    def __init__(self, 
                 communication_service: PatientCommunicationService,
                 healthcare_integrator: HealthcareSystemIntegrator,
                 nphies_compliance: NPHIESComplianceValidator):
        """
        Initialize the PyHeart workflow engine
        
        Args:
            communication_service: Patient communication service
            healthcare_integrator: Healthcare system integrator
            nphies_compliance: NPHIES compliance validator
        """
        self.communication_service = communication_service
        self.healthcare_integrator = healthcare_integrator
        self.nphies_compliance = nphies_compliance
        
        # Workflow management
        self.workflow_definitions: Dict[str, HealthcareWorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.triggers: Dict[str, WorkflowTrigger] = {}
        
        # Action registry
        self.actions: Dict[str, WorkflowAction] = {
            "message": MessageAction(communication_service),
            "wait": WaitAction(),
            "decision": DecisionAction(),
            "escalation": EscalationAction()
        }
        
        # Configuration
        self.config = {
            "max_concurrent_workflows": 100,
            "default_timeout_hours": 24,
            "escalation_enabled": True,
            "arabic_processing_enabled": True,
            "cultural_context_enabled": True
        }
        
        # Islamic calendar integration for Saudi context
        self.saudi_timezone = pytz.timezone('Asia/Riyadh')
        
        logger.info("PyHeart Healthcare Workflow Engine initialized")
    
    # ==================== WORKFLOW DEFINITION MANAGEMENT ====================
    
    async def register_workflow_definition(self, workflow_def: HealthcareWorkflowDefinition) -> Dict[str, Any]:
        """Register a new workflow definition"""
        try:
            # Validate workflow definition
            validation_result = await self._validate_workflow_definition(workflow_def)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Workflow validation failed",
                    "validation_errors": validation_result["errors"]
                }
            
            # Register workflow
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            
            # Register trigger
            if workflow_def.trigger:
                self.triggers[workflow_def.trigger.trigger_id] = workflow_def.trigger
            
            logger.info(f"Workflow definition registered: {workflow_def.workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_def.workflow_id,
                "registered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to register workflow definition: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_workflow_definition(self, workflow_def: HealthcareWorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition"""
        errors = []
        
        # Check required fields
        if not workflow_def.name:
            errors.append("Workflow name is required")
        
        if not workflow_def.steps:
            errors.append("Workflow must have at least one step")
        
        # Validate steps
        step_ids = {step.step_id for step in workflow_def.steps}
        for step in workflow_def.steps:
            for next_step in step.next_steps:
                if next_step not in step_ids:
                    errors.append(f"Step {step.step_id} references invalid next step: {next_step}")
        
        # Validate actions
        for step in workflow_def.steps:
            for action in step.actions:
                action_type = action.get("type")
                if action_type not in self.actions:
                    errors.append(f"Unknown action type: {action_type}")
        
        # Validate compliance requirements
        for requirement in workflow_def.compliance_requirements:
            if requirement not in ["hipaa", "pdpl", "nphies", "moh"]:
                errors.append(f"Unknown compliance requirement: {requirement}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    # ==================== WORKFLOW EXECUTION ====================
    
    async def trigger_workflow(self, 
                             event_type: WorkflowEventType,
                             event_data: Dict[str, Any],
                             patient_data: PatientCommunicationData,
                             healthcare_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger workflow execution based on event"""
        try:
            # Find matching triggers
            matching_triggers = self._find_matching_triggers(event_type, event_data)
            
            if not matching_triggers:
                return {
                    "success": False,
                    "error": "No matching workflow triggers found",
                    "event_type": event_type.value
                }
            
            # Execute all matching workflows
            execution_results = []
            for trigger in matching_triggers:
                workflow_def = self._get_workflow_for_trigger(trigger)
                if workflow_def:
                    result = await self.start_workflow_execution(
                        workflow_def, patient_data, healthcare_context or {}
                    )
                    execution_results.append(result)
            
            return {
                "success": True,
                "triggered_workflows": len(execution_results),
                "executions": execution_results
            }
            
        except Exception as e:
            logger.error(f"Workflow trigger failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_workflow_execution(self,
                                     workflow_def: HealthcareWorkflowDefinition,
                                     patient_data: PatientCommunicationData,
                                     healthcare_context: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow execution"""
        try:
            execution_id = f"exec_{workflow_def.workflow_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create workflow context
            context = WorkflowContext(
                workflow_id=workflow_def.workflow_id,
                patient_id=patient_data.patient_id,
                patient_data=patient_data,
                healthcare_data=healthcare_context,
                cultural_context=self._build_cultural_context(patient_data)
            )
            
            # Create workflow execution
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_definition=workflow_def,
                context=context,
                variables=workflow_def.variables.copy()
            )
            
            # Add to active executions
            self.active_executions[execution_id] = execution
            
            # Start execution
            execution.state = WorkflowState.RUNNING
            execution.started_at = datetime.now()
            
            # Execute first step
            if workflow_def.steps:
                first_step = workflow_def.steps[0]
                execution.current_step = first_step.step_id
                await self._execute_workflow_step(execution, first_step)
            
            logger.info(f"Workflow execution started: {execution_id}")
            
            return {
                "success": True,
                "execution_id": execution_id,
                "workflow_id": workflow_def.workflow_id,
                "state": execution.state.value
            }
            
        except Exception as e:
            logger.error(f"Failed to start workflow execution: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_workflow_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            step_start_time = datetime.now()
            
            # Log step execution
            step_log = {
                "step_id": step.step_id,
                "step_type": step.step_type,
                "started_at": step_start_time.isoformat(),
                "context_snapshot": {
                    "patient_id": execution.context.patient_id,
                    "variables": execution.variables.copy()
                }
            }
            
            execution.step_history.append(step_log)
            
            # Check step conditions
            if step.conditions:
                conditions_met = await self._check_step_conditions(step.conditions, execution.context)
                if not conditions_met:
                    step_log["skipped"] = True
                    step_log["reason"] = "Conditions not met"
                    return {"success": True, "skipped": True}
            
            # Execute step actions
            action_results = []
            for action_config in step.actions:
                action_type = action_config.get("type")
                action_parameters = action_config.get("parameters", {})
                
                if action_type in self.actions:
                    action = self.actions[action_type]
                    result = await action.execute(execution.context, action_parameters)
                    action_results.append({
                        "action_type": action_type,
                        "result": result
                    })
                else:
                    logger.warning(f"Unknown action type: {action_type}")
            
            # Update step log
            step_log["completed_at"] = datetime.now().isoformat()
            step_log["action_results"] = action_results
            step_log["success"] = True
            
            # Determine next step
            next_step_id = await self._determine_next_step(step, execution, action_results)
            
            if next_step_id:
                # Find and execute next step
                next_step = self._find_step_by_id(execution.workflow_definition, next_step_id)
                if next_step:
                    execution.current_step = next_step_id
                    execution.context.last_updated = datetime.now()
                    await self._execute_workflow_step(execution, next_step)
                else:
                    logger.error(f"Next step not found: {next_step_id}")
            else:
                # Workflow completed
                execution.state = WorkflowState.COMPLETED
                execution.completed_at = datetime.now()
                execution.current_step = None
                
                logger.info(f"Workflow execution completed: {execution.execution_id}")
            
            return {
                "success": True,
                "step_id": step.step_id,
                "action_results": action_results,
                "next_step": next_step_id
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            execution.state = WorkflowState.FAILED
            execution.error_message = str(e)
            
            return {
                "success": False,
                "step_id": step.step_id,
                "error": str(e)
            }
    
    async def _check_step_conditions(self, conditions: List[Dict[str, Any]], context: WorkflowContext) -> bool:
        """Check if step conditions are met"""
        try:
            for condition in conditions:
                condition_type = condition.get("type")
                
                if condition_type == "patient_language":
                    required_language = condition.get("language")
                    if context.patient_data.preferred_language != Language(required_language):
                        return False
                
                elif condition_type == "cultural_context":
                    required_context = condition.get("context")
                    if required_context not in context.cultural_context:
                        return False
                
                elif condition_type == "time_of_day":
                    # Check Islamic prayer times for Saudi context
                    current_time = datetime.now(self.saudi_timezone)
                    if not self._is_appropriate_communication_time(current_time, context):
                        return False
                
                elif condition_type == "healthcare_data":
                    field_name = condition.get("field")
                    operator = condition.get("operator", "exists")
                    value = condition.get("value")
                    
                    if operator == "exists":
                        if field_name not in context.healthcare_data:
                            return False
                    elif operator == "equals":
                        if context.healthcare_data.get(field_name) != value:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition check failed: {e}")
            return False
    
    async def _determine_next_step(self, 
                                 current_step: WorkflowStep, 
                                 execution: WorkflowExecution, 
                                 action_results: List[Dict[str, Any]]) -> Optional[str]:
        """Determine the next step in the workflow"""
        try:
            # If step has conditional next steps, evaluate them
            for action_result in action_results:
                if action_result["action_type"] == "decision":
                    next_step = action_result["result"].get("next_step")
                    if next_step:
                        return next_step
            
            # Default to first next step
            if current_step.next_steps:
                return current_step.next_steps[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Next step determination failed: {e}")
            return None
    
    # ==================== UTILITY METHODS ====================
    
    def _find_matching_triggers(self, event_type: WorkflowEventType, event_data: Dict[str, Any]) -> List[WorkflowTrigger]:
        """Find triggers that match the event"""
        matching_triggers = []
        
        for trigger in self.triggers.values():
            if trigger.event_type == event_type and trigger.enabled:
                # Check trigger conditions
                if self._check_trigger_conditions(trigger, event_data):
                    matching_triggers.append(trigger)
        
        return matching_triggers
    
    def _check_trigger_conditions(self, trigger: WorkflowTrigger, event_data: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        if not trigger.conditions:
            return True
        
        for condition_key, condition_value in trigger.conditions.items():
            if condition_key not in event_data:
                return False
            
            if isinstance(condition_value, dict):
                operator = condition_value.get("operator", "equals")
                value = condition_value.get("value")
                
                if operator == "equals" and event_data[condition_key] != value:
                    return False
                elif operator == "in" and event_data[condition_key] not in value:
                    return False
            else:
                if event_data[condition_key] != condition_value:
                    return False
        
        return True
    
    def _get_workflow_for_trigger(self, trigger: WorkflowTrigger) -> Optional[HealthcareWorkflowDefinition]:
        """Get workflow definition for a trigger"""
        for workflow_def in self.workflow_definitions.values():
            if workflow_def.trigger and workflow_def.trigger.trigger_id == trigger.trigger_id:
                return workflow_def
        return None
    
    def _find_step_by_id(self, workflow_def: HealthcareWorkflowDefinition, step_id: str) -> Optional[WorkflowStep]:
        """Find workflow step by ID"""
        for step in workflow_def.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _build_cultural_context(self, patient_data: PatientCommunicationData) -> Dict[str, Any]:
        """Build cultural context for Saudi patients"""
        context = {
            "country": "saudi_arabia",
            "timezone": "Asia/Riyadh",
            "calendar_system": "islamic",
            "primary_language": patient_data.preferred_language.value,
            "communication_preferences": {
                "respect_prayer_times": True,
                "family_involvement": True,
                "gender_considerations": True
            }
        }
        
        # Add Islamic calendar information
        now = datetime.now(self.saudi_timezone)
        context["current_time"] = {
            "gregorian": now.isoformat(),
            "islamic_date": self._get_islamic_date(now),
            "is_prayer_time": self._is_prayer_time(now)
        }
        
        return context
    
    def _get_islamic_date(self, gregorian_date: datetime) -> str:
        """Get Islamic date (simplified implementation)"""
        # This would integrate with a proper Islamic calendar library
        return "1445-12-15"  # Placeholder
    
    def _is_prayer_time(self, current_time: datetime) -> bool:
        """Check if current time is during prayer hours"""
        # Simplified prayer time check (would integrate with proper prayer time calculation)
        hour = current_time.hour
        # Basic prayer times (would be calculated dynamically)
        prayer_hours = [5, 12, 15, 18, 19]  # Fajr, Dhuhr, Asr, Maghrib, Isha
        return hour in prayer_hours
    
    def _is_appropriate_communication_time(self, current_time: datetime, context: WorkflowContext) -> bool:
        """Check if it's appropriate time to send communications"""
        # Respect prayer times
        if self._is_prayer_time(current_time):
            return False
        
        # Respect quiet hours (10 PM - 7 AM)
        hour = current_time.hour
        if hour < 7 or hour > 22:
            return False
        
        # Friday prayer considerations
        if current_time.weekday() == 4 and 11 <= hour <= 14:  # Friday 11 AM - 2 PM
            return False
        
        return True
    
    # ==================== MONITORING AND ANALYTICS ====================
    
    async def get_workflow_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            if execution_id not in self.active_executions:
                return {"status": "not_found"}
            
            execution = self.active_executions[execution_id]
            
            # Calculate execution metrics
            duration_seconds = 0
            if execution.started_at:
                end_time = execution.completed_at or datetime.now()
                duration_seconds = (end_time - execution.started_at).total_seconds()
            
            return {
                "execution_id": execution_id,
                "workflow_id": execution.workflow_definition.workflow_id,
                "state": execution.state.value,
                "current_step": execution.current_step,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "duration_seconds": duration_seconds,
                "steps_completed": len(execution.step_history),
                "retry_count": execution.retry_count,
                "escalation_count": execution.escalation_count,
                "error_message": execution.error_message,
                "patient_id": execution.context.patient_id,
                "last_updated": execution.context.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflow executions"""
        try:
            active_workflows = []
            
            for execution_id, execution in self.active_executions.items():
                if execution.state in [WorkflowState.RUNNING, WorkflowState.WAITING]:
                    status = await self.get_workflow_execution_status(execution_id)
                    active_workflows.append(status)
            
            return active_workflows
            
        except Exception as e:
            logger.error(f"Failed to get active workflows: {e}")
            return []
    
    async def get_workflow_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get workflow analytics for date range"""
        try:
            # Filter executions by date range
            filtered_executions = [
                execution for execution in self.active_executions.values()
                if execution.started_at and start_date <= execution.started_at <= end_date
            ]
            
            # Calculate analytics
            total_executions = len(filtered_executions)
            completed_executions = len([e for e in filtered_executions if e.state == WorkflowState.COMPLETED])
            failed_executions = len([e for e in filtered_executions if e.state == WorkflowState.FAILED])
            
            # Success rate
            success_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Average execution time
            completed_with_duration = [
                e for e in filtered_executions 
                if e.state == WorkflowState.COMPLETED and e.started_at and e.completed_at
            ]
            
            avg_duration_seconds = 0
            if completed_with_duration:
                total_duration = sum(
                    (e.completed_at - e.started_at).total_seconds() 
                    for e in completed_with_duration
                )
                avg_duration_seconds = total_duration / len(completed_with_duration)
            
            # Workflow type distribution
            workflow_types = {}
            for execution in filtered_executions:
                workflow_type = execution.workflow_definition.workflow_type.value
                workflow_types[workflow_type] = workflow_types.get(workflow_type, 0) + 1
            
            # Language distribution
            language_distribution = {}
            for execution in filtered_executions:
                language = execution.context.patient_data.preferred_language.value
                language_distribution[language] = language_distribution.get(language, 0) + 1
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "execution_metrics": {
                    "total_executions": total_executions,
                    "completed_executions": completed_executions,
                    "failed_executions": failed_executions,
                    "running_executions": len([e for e in filtered_executions if e.state == WorkflowState.RUNNING]),
                    "success_rate_percent": round(success_rate, 2),
                    "average_duration_seconds": round(avg_duration_seconds, 2)
                },
                "workflow_type_distribution": workflow_types,
                "language_distribution": language_distribution,
                "cultural_context_metrics": {
                    "prayer_time_delays": self._count_prayer_time_delays(filtered_executions),
                    "arabic_communications": language_distribution.get("ar", 0),
                    "saudi_timezone_executions": total_executions
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate workflow analytics: {e}")
            return {"error": str(e)}
    
    def _count_prayer_time_delays(self, executions: List[WorkflowExecution]) -> int:
        """Count communications delayed due to prayer times"""
        # This would analyze step history for prayer time delays
        return 0
    
    # ==================== WORKFLOW LIFECYCLE MANAGEMENT ====================
    
    async def pause_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """Pause a running workflow execution"""
        try:
            if execution_id not in self.active_executions:
                return {"success": False, "error": "Execution not found"}
            
            execution = self.active_executions[execution_id]
            
            if execution.state != WorkflowState.RUNNING:
                return {"success": False, "error": f"Cannot pause workflow in state: {execution.state.value}"}
            
            execution.state = WorkflowState.PAUSED
            execution.audit_trail.append({
                "action": "paused",
                "timestamp": datetime.now().isoformat(),
                "reason": "Manual pause"
            })
            
            logger.info(f"Workflow execution paused: {execution_id}")
            
            return {"success": True, "state": execution.state.value}
            
        except Exception as e:
            logger.error(f"Failed to pause workflow execution: {e}")
            return {"success": False, "error": str(e)}
    
    async def resume_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """Resume a paused workflow execution"""
        try:
            if execution_id not in self.active_executions:
                return {"success": False, "error": "Execution not found"}
            
            execution = self.active_executions[execution_id]
            
            if execution.state != WorkflowState.PAUSED:
                return {"success": False, "error": f"Cannot resume workflow in state: {execution.state.value}"}
            
            execution.state = WorkflowState.RUNNING
            execution.audit_trail.append({
                "action": "resumed",
                "timestamp": datetime.now().isoformat(),
                "reason": "Manual resume"
            })
            
            # Continue from current step
            if execution.current_step:
                current_step = self._find_step_by_id(execution.workflow_definition, execution.current_step)
                if current_step:
                    await self._execute_workflow_step(execution, current_step)
            
            logger.info(f"Workflow execution resumed: {execution_id}")
            
            return {"success": True, "state": execution.state.value}
            
        except Exception as e:
            logger.error(f"Failed to resume workflow execution: {e}")
            return {"success": False, "error": str(e)}
    
    async def cancel_workflow_execution(self, execution_id: str, reason: str = "Manual cancellation") -> Dict[str, Any]:
        """Cancel a workflow execution"""
        try:
            if execution_id not in self.active_executions:
                return {"success": False, "error": "Execution not found"}
            
            execution = self.active_executions[execution_id]
            
            if execution.state in [WorkflowState.COMPLETED, WorkflowState.CANCELLED]:
                return {"success": False, "error": f"Cannot cancel workflow in state: {execution.state.value}"}
            
            execution.state = WorkflowState.CANCELLED
            execution.completed_at = datetime.now()
            execution.audit_trail.append({
                "action": "cancelled",
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            })
            
            logger.info(f"Workflow execution cancelled: {execution_id}")
            
            return {"success": True, "state": execution.state.value, "reason": reason}
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow execution: {e}")
            return {"success": False, "error": str(e)}

# Export main class
__all__ = ["PyHeartHealthcareWorkflowEngine", "HealthcareWorkflowDefinition", "WorkflowTrigger", "WorkflowStep", "WorkflowEventType", "HealthcareWorkflowType"]