"""
BrainSAIT Healthcare Platform - Communication Workflow Orchestrator
Main orchestrator for all patient communication workflows with comprehensive healthcare integration

This orchestrator manages:
1. Coordination of all communication workflows (Pre-Visit, Visit, Post-Visit, Clinical Results, Emergency)
2. Integration with BrainSAIT healthcare systems
3. HIPAA compliance enforcement across all communications
4. Arabic/English message delivery with NPHIES compliance
5. Real-time workflow state management
6. Automated escalation and error handling
7. Comprehensive audit logging and reporting
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
import json
from dataclasses import dataclass, field
from enum import Enum

from .patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData, AppointmentData, ClinicalResultData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)
from .workflows.pre_visit_workflow import PreVisitWorkflow
from .workflows.visit_workflow import VisitWorkflow, VisitData, ProviderData
from .workflows.post_visit_workflow import PostVisitWorkflow, PostVisitData
from .workflows.clinical_results_workflow import ClinicalResultsWorkflow, ClinicalResult, ProviderNotificationData
from .workflows.emergency_workflow import EmergencyWorkflow, EmergencyEvent, EmergencyContact
from .healthcare_integration import HealthcareSystemIntegrator, AuditEventType
from .nphies_compliance import ArabicMessageTemplateManager, NPHIESComplianceValidator

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

class WorkflowPriority(str, Enum):
    """Workflow execution priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    execution_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    patient_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[str] = field(default_factory=list)

@dataclass
class OrchestratorConfig:
    """Orchestrator configuration"""
    max_concurrent_workflows: int = 50
    workflow_timeout_minutes: int = 60
    retry_delay_seconds: int = 30
    escalation_enabled: bool = True
    escalation_timeout_minutes: int = 30
    audit_retention_days: int = 2555  # 7 years HIPAA requirement
    enable_real_time_monitoring: bool = True

class CommunicationWorkflowOrchestrator:
    """
    Main orchestrator for all healthcare communication workflows
    
    Coordinates and manages the execution of all communication workflows
    with full HIPAA compliance and healthcare system integration
    """
    
    def __init__(self, 
                 twilio_account_sid: str,
                 twilio_auth_token: str,
                 twilio_phone_number: str,
                 encryption_key: Optional[str] = None):
        """
        Initialize the communication workflow orchestrator
        
        Args:
            twilio_account_sid: Twilio account SID for communications
            twilio_auth_token: Twilio authentication token
            twilio_phone_number: Twilio phone number for sending messages
            encryption_key: Encryption key for HIPAA compliance
        """
        # Initialize core communication service
        self.communication_service = PatientCommunicationService(
            twilio_account_sid, twilio_auth_token, twilio_phone_number, encryption_key
        )
        
        # Initialize healthcare integration
        self.healthcare_integrator = HealthcareSystemIntegrator(
            self.communication_service, encryption_key
        )
        
        # Initialize workflow managers
        self.pre_visit_workflow = PreVisitWorkflow(self.communication_service)
        self.visit_workflow = VisitWorkflow(self.communication_service)
        self.post_visit_workflow = PostVisitWorkflow(self.communication_service)
        self.clinical_results_workflow = ClinicalResultsWorkflow(self.communication_service)
        self.emergency_workflow = EmergencyWorkflow(self.communication_service)
        
        # Initialize compliance and templates
        self.arabic_templates = ArabicMessageTemplateManager()
        self.nphies_compliance = NPHIESComplianceValidator()
        
        # Orchestrator state
        self.config = OrchestratorConfig()
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.workflow_queue: List[WorkflowExecution] = []
        self.system_status = {
            "status": "operational",
            "last_health_check": datetime.now(),
            "active_workflows": 0,
            "total_executions": 0,
            "error_rate": 0.0
        }
        
        logger.info("Communication Workflow Orchestrator initialized")
    
    # ==================== MAIN WORKFLOW METHODS ====================
    
    async def initiate_patient_journey(self, 
                                     patient_data: PatientCommunicationData,
                                     appointment_data: AppointmentData,
                                     provider_data: ProviderData,
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate complete patient communication journey
        
        This is the main entry point for starting all patient communications
        from appointment booking through post-visit follow-up
        """
        try:
            journey_id = f"journey_{appointment_data.appointment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create journey execution tracking
            journey_execution = WorkflowExecution(
                execution_id=journey_id,
                workflow_type=WorkflowType.PRE_VISIT,
                priority=WorkflowPriority.NORMAL,
                patient_id=patient_data.patient_id,
                metadata={
                    "appointment_id": appointment_data.appointment_id,
                    "provider_id": provider_data.provider_id,
                    "user_id": user_id,
                    "journey_type": "complete_patient_journey"
                }
            )
            
            self.active_executions[journey_id] = journey_execution
            
            # Start with pre-visit workflow
            pre_visit_result = await self.execute_pre_visit_workflow(
                patient_data, appointment_data, user_id
            )
            
            journey_execution.audit_trail.append(f"Pre-visit workflow initiated: {pre_visit_result['workflow_id']}")
            
            # Schedule visit workflow for appointment time
            visit_schedule_result = await self._schedule_visit_workflow(
                patient_data, appointment_data, provider_data, journey_id
            )
            
            journey_execution.audit_trail.append(f"Visit workflow scheduled: {visit_schedule_result}")
            
            # Update journey status
            journey_execution.status = WorkflowStatus.IN_PROGRESS
            journey_execution.started_at = datetime.now()
            
            # Log to healthcare systems
            await self.healthcare_integrator.audit_logger.log_communication_event(
                AuditEventType.COMMUNICATION_SENT,
                journey_execution.metadata,
                patient_data,
                user_id,
                True
            )
            
            logger.info(f"Patient journey initiated: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "pre_visit_workflow": pre_visit_result,
                "scheduled_workflows": visit_schedule_result,
                "status": "initiated"
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate patient journey: {e}")
            return {
                "success": False,
                "error": str(e),
                "journey_id": None
            }
    
    async def execute_pre_visit_workflow(self, 
                                       patient_data: PatientCommunicationData,
                                       appointment_data: AppointmentData,
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute pre-visit communication workflow with full compliance"""
        try:
            execution_id = f"pre_visit_{appointment_data.appointment_id}"
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_type=WorkflowType.PRE_VISIT,
                priority=WorkflowPriority.NORMAL,
                patient_id=patient_data.patient_id,
                metadata={
                    "appointment_id": appointment_data.appointment_id,
                    "user_id": user_id
                }
            )
            
            self.active_executions[execution_id] = execution
            execution.status = WorkflowStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            
            # Execute pre-visit workflow
            workflow_result = await self.pre_visit_workflow.initiate_pre_visit_workflow(
                patient_data, appointment_data
            )
            
            # Check compliance for all messages sent
            compliance_results = []
            if workflow_result.get("confirmation_result"):
                compliance_check = await self._check_message_compliance(
                    workflow_result["confirmation_result"], patient_data, user_id
                )
                compliance_results.append(compliance_check)
            
            # Update execution status
            if workflow_result.get("status") == "initiated":
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Pre-visit workflow initiation failed"
            
            execution.audit_trail.append(f"Workflow completed with status: {execution.status.value}")
            
            return {
                "execution_id": execution_id,
                "workflow_result": workflow_result,
                "compliance_results": compliance_results,
                "status": execution.status.value
            }
            
        except Exception as e:
            logger.error(f"Pre-visit workflow execution failed: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = WorkflowStatus.FAILED
                self.active_executions[execution_id].error_message = str(e)
            
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def execute_visit_workflow(self, 
                                   patient_data: PatientCommunicationData,
                                   appointment_data: AppointmentData,
                                   provider_data: ProviderData,
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute visit communication workflow"""
        try:
            execution_id = f"visit_{appointment_data.appointment_id}"
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_type=WorkflowType.VISIT,
                priority=WorkflowPriority.HIGH,
                patient_id=patient_data.patient_id,
                metadata={
                    "appointment_id": appointment_data.appointment_id,
                    "provider_id": provider_data.provider_id,
                    "user_id": user_id
                }
            )
            
            self.active_executions[execution_id] = execution
            execution.status = WorkflowStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            
            # Execute visit workflow
            workflow_result = await self.visit_workflow.initiate_visit_workflow(
                patient_data, appointment_data, provider_data
            )
            
            # Update execution status
            if workflow_result.get("status") == "initiated":
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Visit workflow initiation failed"
            
            execution.audit_trail.append(f"Visit workflow completed: {workflow_result.get('visit_id')}")
            
            return {
                "execution_id": execution_id,
                "workflow_result": workflow_result,
                "status": execution.status.value
            }
            
        except Exception as e:
            logger.error(f"Visit workflow execution failed: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = WorkflowStatus.FAILED
                self.active_executions[execution_id].error_message = str(e)
            
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def execute_post_visit_workflow(self, 
                                        patient_data: PatientCommunicationData,
                                        appointment_data: AppointmentData,
                                        post_visit_data: PostVisitData,
                                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute post-visit communication workflow"""
        try:
            execution_id = f"post_visit_{post_visit_data.visit_id}"
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_type=WorkflowType.POST_VISIT,
                priority=WorkflowPriority.NORMAL,
                patient_id=patient_data.patient_id,
                metadata={
                    "visit_id": post_visit_data.visit_id,
                    "appointment_id": appointment_data.appointment_id,
                    "user_id": user_id
                }
            )
            
            self.active_executions[execution_id] = execution
            execution.status = WorkflowStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            
            # Execute post-visit workflow
            workflow_result = await self.post_visit_workflow.initiate_post_visit_workflow(
                patient_data, appointment_data, post_visit_data
            )
            
            # Update execution status
            if workflow_result.get("status") == "initiated":
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Post-visit workflow initiation failed"
            
            execution.audit_trail.append(f"Post-visit workflow completed: {workflow_result.get('workflow_id')}")
            
            return {
                "execution_id": execution_id,
                "workflow_result": workflow_result,
                "status": execution.status.value
            }
            
        except Exception as e:
            logger.error(f"Post-visit workflow execution failed: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = WorkflowStatus.FAILED
                self.active_executions[execution_id].error_message = str(e)
            
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def execute_clinical_results_workflow(self, 
                                              patient_data: PatientCommunicationData,
                                              clinical_result: ClinicalResult,
                                              provider_data: ProviderNotificationData,
                                              user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute clinical results communication workflow"""
        try:
            execution_id = f"clinical_{clinical_result.result_id}"
            
            # Determine priority based on result severity
            priority_map = {
                "critical": WorkflowPriority.CRITICAL,
                "abnormal": WorkflowPriority.HIGH,
                "normal": WorkflowPriority.NORMAL
            }
            priority = priority_map.get(clinical_result.severity.value, WorkflowPriority.NORMAL)
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                priority=priority,
                patient_id=patient_data.patient_id,
                metadata={
                    "result_id": clinical_result.result_id,
                    "result_type": clinical_result.result_type.value,
                    "severity": clinical_result.severity.value,
                    "user_id": user_id
                }
            )
            
            self.active_executions[execution_id] = execution
            execution.status = WorkflowStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            
            # Execute clinical results workflow
            workflow_result = await self.clinical_results_workflow.initiate_clinical_results_workflow(
                patient_data, clinical_result, provider_data
            )
            
            # Update execution status
            if workflow_result.get("status") == "initiated":
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Clinical results workflow initiation failed"
            
            execution.audit_trail.append(f"Clinical results workflow completed: {workflow_result.get('workflow_id')}")
            
            return {
                "execution_id": execution_id,
                "workflow_result": workflow_result,
                "status": execution.status.value
            }
            
        except Exception as e:
            logger.error(f"Clinical results workflow execution failed: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = WorkflowStatus.FAILED
                self.active_executions[execution_id].error_message = str(e)
            
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def execute_emergency_workflow(self, 
                                       emergency_event: EmergencyEvent,
                                       emergency_contacts: List[EmergencyContact],
                                       patient_data: Optional[PatientCommunicationData] = None,
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute emergency communication workflow"""
        try:
            execution_id = f"emergency_{emergency_event.event_id}"
            
            # Create execution tracking
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_type=WorkflowType.EMERGENCY,
                priority=WorkflowPriority.CRITICAL,
                patient_id=patient_data.patient_id if patient_data else "system",
                metadata={
                    "event_id": emergency_event.event_id,
                    "emergency_type": emergency_event.emergency_type.value,
                    "emergency_level": emergency_event.emergency_level.value,
                    "user_id": user_id
                }
            )
            
            self.active_executions[execution_id] = execution
            execution.status = WorkflowStatus.IN_PROGRESS
            execution.started_at = datetime.now()
            
            # Execute emergency workflow
            workflow_result = await self.emergency_workflow.initiate_emergency_workflow(
                emergency_event, emergency_contacts, patient_data
            )
            
            # Update execution status
            if workflow_result.get("status") == "initiated":
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Emergency workflow initiation failed"
            
            execution.audit_trail.append(f"Emergency workflow completed: {workflow_result.get('workflow_id')}")
            
            return {
                "execution_id": execution_id,
                "workflow_result": workflow_result,
                "status": execution.status.value
            }
            
        except Exception as e:
            logger.error(f"Emergency workflow execution failed: {e}")
            if execution_id in self.active_executions:
                self.active_executions[execution_id].status = WorkflowStatus.FAILED
                self.active_executions[execution_id].error_message = str(e)
            
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    # ==================== COMPLIANCE AND INTEGRATION METHODS ====================
    
    async def _check_message_compliance(self, 
                                      message_result: Dict[str, Any],
                                      patient_data: PatientCommunicationData,
                                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check message compliance using healthcare integrator"""
        try:
            # Use healthcare integrator for compliance checking
            compliance_result = await self.healthcare_integrator.send_compliant_communication(
                patient_data,
                message_result,
                user_id
            )
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "compliance_status": "unknown"
            }
    
    async def _schedule_visit_workflow(self, 
                                     patient_data: PatientCommunicationData,
                                     appointment_data: AppointmentData,
                                     provider_data: ProviderData,
                                     journey_id: str) -> Dict[str, Any]:
        """Schedule visit workflow for appointment time"""
        try:
            # In a production system, this would integrate with a task scheduler
            # For now, we'll track the scheduling
            
            schedule_time = appointment_data.appointment_datetime
            current_time = datetime.now()
            
            if schedule_time > current_time:
                # Future appointment - schedule workflow
                delay_minutes = (schedule_time - current_time).total_seconds() / 60
                
                return {
                    "status": "scheduled",
                    "appointment_time": schedule_time.isoformat(),
                    "delay_minutes": delay_minutes,
                    "journey_id": journey_id
                }
            else:
                # Immediate appointment - execute now
                visit_result = await self.execute_visit_workflow(
                    patient_data, appointment_data, provider_data
                )
                
                return {
                    "status": "executed_immediately",
                    "visit_workflow": visit_result
                }
            
        except Exception as e:
            logger.error(f"Visit workflow scheduling failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # ==================== MONITORING AND MANAGEMENT METHODS ====================
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            if execution_id not in self.active_executions:
                return {"status": "not_found"}
            
            execution = self.active_executions[execution_id]
            
            # Calculate execution time
            if execution.started_at:
                if execution.completed_at:
                    execution_time = (execution.completed_at - execution.started_at).total_seconds()
                else:
                    execution_time = (datetime.now() - execution.started_at).total_seconds()
            else:
                execution_time = 0
            
            return {
                "execution_id": execution_id,
                "workflow_type": execution.workflow_type.value,
                "status": execution.status.value,
                "priority": execution.priority.value,
                "patient_id": execution.patient_id,
                "created_at": execution.created_at.isoformat(),
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "execution_time_seconds": execution_time,
                "retry_count": execution.retry_count,
                "error_message": execution.error_message,
                "audit_trail": execution.audit_trail,
                "metadata": execution.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {execution_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflow executions"""
        try:
            active_workflows = []
            
            for execution_id, execution in self.active_executions.items():
                if execution.status == WorkflowStatus.IN_PROGRESS:
                    workflow_info = {
                        "execution_id": execution_id,
                        "workflow_type": execution.workflow_type.value,
                        "priority": execution.priority.value,
                        "patient_id": execution.patient_id,
                        "started_at": execution.started_at.isoformat() if execution.started_at else None,
                        "running_time_seconds": (datetime.now() - execution.started_at).total_seconds() if execution.started_at else 0
                    }
                    active_workflows.append(workflow_info)
            
            return active_workflows
            
        except Exception as e:
            logger.error(f"Failed to get active workflows: {e}")
            return []
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            now = datetime.now()
            
            # Count workflow statuses
            status_counts = {}
            for execution in self.active_executions.values():
                status = execution.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate error rate
            total_executions = len(self.active_executions)
            failed_executions = status_counts.get("failed", 0)
            error_rate = (failed_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Update system status
            self.system_status.update({
                "last_health_check": now,
                "active_workflows": status_counts.get("in_progress", 0),
                "total_executions": total_executions,
                "error_rate": round(error_rate, 2)
            })
            
            # Determine overall health
            if error_rate > 10:
                health_status = "degraded"
            elif error_rate > 5:
                health_status = "warning"
            else:
                health_status = "healthy"
            
            return {
                "health_status": health_status,
                "system_status": self.system_status,
                "workflow_counts": status_counts,
                "configuration": {
                    "max_concurrent_workflows": self.config.max_concurrent_workflows,
                    "workflow_timeout_minutes": self.config.workflow_timeout_minutes,
                    "escalation_enabled": self.config.escalation_enabled
                },
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "health_status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    async def generate_compliance_report(self, 
                                       start_date: datetime,
                                       end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            # Get compliance report from healthcare integrator
            compliance_report = await self.healthcare_integrator.get_compliance_report(
                start_date, end_date
            )
            
            # Add workflow-specific metrics
            workflow_executions = [
                execution for execution in self.active_executions.values()
                if start_date <= execution.created_at <= end_date
            ]
            
            workflow_metrics = {
                "total_workflows": len(workflow_executions),
                "successful_workflows": len([e for e in workflow_executions if e.status == WorkflowStatus.COMPLETED]),
                "failed_workflows": len([e for e in workflow_executions if e.status == WorkflowStatus.FAILED]),
                "workflow_types": {}
            }
            
            # Count by workflow type
            for execution in workflow_executions:
                workflow_type = execution.workflow_type.value
                workflow_metrics["workflow_types"][workflow_type] = workflow_metrics["workflow_types"].get(workflow_type, 0) + 1
            
            # Combine reports
            comprehensive_report = {
                "report_metadata": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "generated_at": datetime.now().isoformat(),
                    "report_type": "comprehensive_compliance"
                },
                "compliance_metrics": compliance_report.get("metrics", {}),
                "workflow_metrics": workflow_metrics,
                "system_health": await self.get_system_health(),
                "recommendations": compliance_report.get("recommendations", [])
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    # ==================== UTILITY METHODS ====================
    
    async def cleanup_completed_workflows(self, older_than_hours: int = 24) -> Dict[str, Any]:
        """Clean up completed workflow executions"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            completed_workflows = [
                execution_id for execution_id, execution in self.active_executions.items()
                if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]
                and execution.completed_at
                and execution.completed_at < cutoff_time
            ]
            
            # Archive before deletion (in production, move to long-term storage)
            archived_count = 0
            for execution_id in completed_workflows:
                execution = self.active_executions[execution_id]
                # Archive to audit system
                await self.healthcare_integrator.audit_logger.log_communication_event(
                    AuditEventType.DATA_MODIFICATION,
                    {"action": "workflow_archived", "execution_id": execution_id},
                    None,
                    None,
                    True
                )
                del self.active_executions[execution_id]
                archived_count += 1
            
            logger.info(f"Archived {archived_count} completed workflows")
            
            return {
                "success": True,
                "archived_workflows": archived_count,
                "remaining_active": len(self.active_executions)
            }
            
        except Exception as e:
            logger.error(f"Workflow cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Export main orchestrator class
__all__ = ["CommunicationWorkflowOrchestrator"]