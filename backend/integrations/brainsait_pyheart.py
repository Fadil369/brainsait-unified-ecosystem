#!/usr/bin/env python3
"""
BrainSAIT PyHeart Integration Module
Unified Workflow and Process Management for the BrainSAIT Healthcare Ecosystem

This module provides the brainsait-pyheart functionality by integrating:
- Advanced healthcare workflow orchestration
- Intelligent process automation
- Real-time workflow monitoring and optimization
- Cultural context-aware workflow management
- HIPAA-compliant process execution
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
from collections import defaultdict, deque

# Workflow and async processing
try:
    import celery
    from celery import Celery
    from redis import Redis
    WORKFLOW_LIBRARIES_AVAILABLE = True
except ImportError:
    WORKFLOW_LIBRARIES_AVAILABLE = False

# Import existing services
from ..services.communication.integrations.pyheart_integration import (
    PyHeartHealthcareWorkflowEngine, HealthcareWorkflowDefinition,
    WorkflowEventType, HealthcareWorkflowType, WorkflowState
)
from ..services.communication.workflow_orchestrator import (
    CommunicationWorkflowOrchestrator, WorkflowExecution
)
from ..services.communication.patient_communication_service import MessagePriority

logger = logging.getLogger(__name__)

class BrainSAITWorkflowStatus(str, Enum):
    """Enhanced workflow status for BrainSAIT ecosystem"""
    INITIALIZED = "initialized"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"
    ARCHIVED = "archived"

class WorkflowPriority(str, Enum):
    """Workflow execution priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    CRITICAL = "critical"

class WorkflowComplexity(str, Enum):
    """Workflow complexity levels for resource allocation"""
    SIMPLE = "simple"        # Single step, minimal resources
    MODERATE = "moderate"    # Multiple steps, standard resources
    COMPLEX = "complex"      # Many steps, high resources
    ENTERPRISE = "enterprise" # Multi-system integration

@dataclass
class BrainSAITWorkflowMetrics:
    """Comprehensive workflow performance metrics"""
    workflow_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time_ms: float = 0.0
    median_execution_time_ms: float = 0.0
    max_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    success_rate: float = 0.0
    average_queue_time_ms: float = 0.0
    resource_utilization: float = 0.0
    cost_per_execution: float = 0.0
    patient_satisfaction_score: float = 0.0
    last_execution: Optional[datetime] = None
    peak_usage_hours: List[int] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WorkflowResourceRequirements:
    """Resource requirements for workflow execution"""
    cpu_cores: int = 1
    memory_mb: int = 512
    storage_mb: int = 100
    network_bandwidth_mbps: int = 10
    concurrent_executions: int = 10
    estimated_duration_minutes: int = 5
    requires_gpu: bool = False
    requires_secure_environment: bool = True
    hipaa_compliance_level: str = "standard"  # standard, enhanced, maximum

@dataclass
class BrainSAITWorkflowDefinition:
    """Enhanced workflow definition for BrainSAIT ecosystem"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""
    workflow_type: HealthcareWorkflowType = HealthcareWorkflowType.PATIENT_ONBOARDING
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    complexity: WorkflowComplexity = WorkflowComplexity.MODERATE
    version: str = "1.0.0"
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Core workflow components
    steps: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    error_handlers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance and resource management
    timeout_minutes: int = 60
    retry_attempts: int = 3
    resource_requirements: WorkflowResourceRequirements = field(default_factory=WorkflowResourceRequirements)
    
    # Cultural and compliance
    cultural_adaptations: Dict[str, Any] = field(default_factory=dict)
    compliance_requirements: List[str] = field(default_factory=lambda: ["HIPAA", "PDPL"])
    language_support: List[str] = field(default_factory=lambda: ["ar", "en"])
    
    # Monitoring and analytics
    metrics: Optional[BrainSAITWorkflowMetrics] = None
    enable_monitoring: bool = True
    enable_analytics: bool = True
    
    # Integration points
    integration_endpoints: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)

class WorkflowExecutionEngine:
    """Advanced workflow execution engine with intelligent scheduling"""
    
    def __init__(self, max_concurrent_workflows: int = 100):
        self.max_concurrent_workflows = max_concurrent_workflows
        self.active_workflows = {}
        self.queued_workflows = deque()
        self.completed_workflows = {}
        self.failed_workflows = {}
        
        # Resource management
        self.resource_pool = {
            "cpu_cores": 16,
            "memory_gb": 32,
            "storage_gb": 500,
            "network_bandwidth_gbps": 1
        }
        self.allocated_resources = defaultdict(int)
        
        # Performance tracking
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "resource_utilization": 0.0
        }
        
        # Workflow registry
        self.workflow_registry = {}
        
    async def register_workflow(self, workflow_def: BrainSAITWorkflowDefinition):
        """Register a workflow definition"""
        
        # Validate workflow
        validation_result = await self._validate_workflow_definition(workflow_def)
        if not validation_result["valid"]:
            raise ValueError(f"Workflow validation failed: {validation_result['errors']}")
        
        # Initialize metrics if not present
        if workflow_def.metrics is None:
            workflow_def.metrics = BrainSAITWorkflowMetrics(
                workflow_id=workflow_def.workflow_id
            )
        
        # Register in registry
        self.workflow_registry[workflow_def.workflow_id] = workflow_def
        
        logger.info(f"Workflow registered: {workflow_def.name} ({workflow_def.workflow_id})")
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             context: Dict[str, Any],
                             priority: Optional[WorkflowPriority] = None) -> Dict[str, Any]:
        """Execute a workflow with intelligent resource management"""
        
        if workflow_id not in self.workflow_registry:
            raise ValueError(f"Workflow {workflow_id} not found in registry")
        
        workflow_def = self.workflow_registry[workflow_id]
        execution_id = str(uuid.uuid4())
        
        # Override priority if specified
        effective_priority = priority or workflow_def.priority
        
        # Check resource availability
        if not await self._check_resource_availability(workflow_def.resource_requirements):
            # Queue the workflow
            await self._queue_workflow(execution_id, workflow_id, context, effective_priority)
            return {
                "execution_id": execution_id,
                "status": BrainSAITWorkflowStatus.QUEUED.value,
                "message": "Workflow queued due to resource constraints"
            }
        
        # Execute immediately
        return await self._execute_workflow_immediately(
            execution_id, workflow_def, context, effective_priority
        )
    
    async def _execute_workflow_immediately(self,
                                          execution_id: str,
                                          workflow_def: BrainSAITWorkflowDefinition,
                                          context: Dict[str, Any],
                                          priority: WorkflowPriority) -> Dict[str, Any]:
        """Execute workflow immediately with resource allocation"""
        
        start_time = time.time()
        
        try:
            # Allocate resources
            await self._allocate_resources(workflow_def.resource_requirements)
            
            # Create execution context
            execution_context = {
                "execution_id": execution_id,
                "workflow_id": workflow_def.workflow_id,
                "priority": priority.value,
                "start_time": datetime.now(),
                "context": context,
                "current_step": 0,
                "status": BrainSAITWorkflowStatus.RUNNING.value
            }
            
            # Add to active workflows
            self.active_workflows[execution_id] = execution_context
            
            # Execute workflow steps
            result = await self._execute_workflow_steps(workflow_def, execution_context)
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            await self._update_workflow_metrics(
                workflow_def, execution_time_ms, result["success"]
            )
            
            # Clean up
            await self._deallocate_resources(workflow_def.resource_requirements)
            self.active_workflows.pop(execution_id, None)
            
            if result["success"]:
                self.completed_workflows[execution_id] = execution_context
                self.execution_stats["successful_executions"] += 1
            else:
                self.failed_workflows[execution_id] = execution_context
                self.execution_stats["failed_executions"] += 1
            
            self.execution_stats["total_executions"] += 1
            
            return {
                "execution_id": execution_id,
                "status": BrainSAITWorkflowStatus.COMPLETED.value if result["success"] else BrainSAITWorkflowStatus.FAILED.value,
                "result": result,
                "execution_time_ms": execution_time_ms,
                "steps_completed": result.get("steps_completed", 0),
                "message": result.get("message", "Workflow execution completed")
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Clean up on error
            await self._deallocate_resources(workflow_def.resource_requirements)
            self.active_workflows.pop(execution_id, None)
            self.failed_workflows[execution_id] = execution_context
            self.execution_stats["failed_executions"] += 1
            self.execution_stats["total_executions"] += 1
            
            return {
                "execution_id": execution_id,
                "status": BrainSAITWorkflowStatus.FAILED.value,
                "error": str(e),
                "execution_time_ms": (time.time() - start_time) * 1000
            }
    
    async def _execute_workflow_steps(self,
                                    workflow_def: BrainSAITWorkflowDefinition,
                                    execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow steps"""
        
        steps_completed = 0
        step_results = []
        
        try:
            for i, step in enumerate(workflow_def.steps):
                execution_context["current_step"] = i
                
                # Execute step
                step_result = await self._execute_step(step, execution_context)
                step_results.append(step_result)
                
                if not step_result.get("success", False):
                    # Handle step failure
                    if step.get("continue_on_failure", False):
                        logger.warning(f"Step {i} failed but continuing: {step_result.get('error')}")
                        continue
                    else:
                        return {
                            "success": False,
                            "steps_completed": steps_completed,
                            "step_results": step_results,
                            "message": f"Workflow failed at step {i}: {step_result.get('error')}"
                        }
                
                steps_completed += 1
                
                # Check for early termination conditions
                if step_result.get("terminate_workflow", False):
                    break
            
            return {
                "success": True,
                "steps_completed": steps_completed,
                "step_results": step_results,
                "message": "Workflow completed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "steps_completed": steps_completed,
                "step_results": step_results,
                "message": f"Workflow execution error: {str(e)}"
            }
    
    async def _execute_step(self, 
                          step: Dict[str, Any],
                          execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        step_type = step.get("type", "unknown")
        step_name = step.get("name", f"Step {execution_context['current_step']}")
        
        try:
            # Log step execution
            logger.debug(f"Executing step: {step_name} (type: {step_type})")
            
            # Simulate step execution based on type
            if step_type == "message":
                result = await self._execute_message_step(step, execution_context)
            elif step_type == "wait":
                result = await self._execute_wait_step(step, execution_context)
            elif step_type == "decision":
                result = await self._execute_decision_step(step, execution_context)
            elif step_type == "api_call":
                result = await self._execute_api_call_step(step, execution_context)
            elif step_type == "data_processing":
                result = await self._execute_data_processing_step(step, execution_context)
            elif step_type == "notification":
                result = await self._execute_notification_step(step, execution_context)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown step type: {step_type}"
                }
            
            return {
                "step_name": step_name,
                "step_type": step_type,
                "success": result.get("success", True),
                "result": result,
                "execution_time_ms": result.get("execution_time_ms", 0)
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {step_name} - {e}")
            return {
                "step_name": step_name,
                "step_type": step_type,
                "success": False,
                "error": str(e)
            }
    
    async def _execute_message_step(self, 
                                  step: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a message sending step"""
        
        # Simulate message sending
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            "success": True,
            "message_sent": True,
            "recipient": step.get("parameters", {}).get("recipient", "unknown"),
            "execution_time_ms": 100
        }
    
    async def _execute_wait_step(self,
                               step: Dict[str, Any],
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a wait/delay step"""
        
        wait_params = step.get("parameters", {})
        wait_type = wait_params.get("type", "time")
        
        if wait_type == "time":
            wait_seconds = wait_params.get("seconds", 1)
            await asyncio.sleep(wait_seconds)
        
        return {
            "success": True,
            "wait_type": wait_type,
            "execution_time_ms": wait_params.get("seconds", 1) * 1000
        }
    
    async def _execute_decision_step(self,
                                   step: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a decision/branching step"""
        
        conditions = step.get("parameters", {}).get("conditions", [])
        
        # Evaluate conditions (simplified)
        for condition in conditions:
            if self._evaluate_condition(condition, context):
                return {
                    "success": True,
                    "decision_result": condition.get("result", "default"),
                    "execution_time_ms": 50
                }
        
        return {
            "success": True,
            "decision_result": "default",
            "execution_time_ms": 50
        }
    
    async def _execute_api_call_step(self,
                                   step: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API call step"""
        
        # Simulate API call
        await asyncio.sleep(0.2)  # Simulate network delay
        
        return {
            "success": True,
            "api_response": {"status": "success", "data": {}},
            "execution_time_ms": 200
        }
    
    async def _execute_data_processing_step(self,
                                          step: Dict[str, Any],
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a data processing step"""
        
        # Simulate data processing
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "success": True,
            "processed_records": 100,
            "execution_time_ms": 500
        }
    
    async def _execute_notification_step(self,
                                       step: Dict[str, Any],
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a notification step"""
        
        # Simulate notification sending
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "notification_sent": True,
            "execution_time_ms": 100
        }
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a workflow condition"""
        
        # Simplified condition evaluation
        condition_type = condition.get("type", "always_true")
        
        if condition_type == "always_true":
            return True
        elif condition_type == "always_false":
            return False
        elif condition_type == "context_check":
            key = condition.get("key", "")
            expected_value = condition.get("value", "")
            return context.get("context", {}).get(key) == expected_value
        
        return False
    
    async def _validate_workflow_definition(self, 
                                          workflow_def: BrainSAITWorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition"""
        
        errors = []
        warnings = []
        
        # Basic validation
        if not workflow_def.name:
            errors.append("Workflow name is required")
        
        if not workflow_def.steps:
            errors.append("Workflow must have at least one step")
        
        # Validate steps
        for i, step in enumerate(workflow_def.steps):
            if "type" not in step:
                errors.append(f"Step {i} missing type")
            if "name" not in step:
                warnings.append(f"Step {i} missing name")
        
        # Resource validation
        if workflow_def.resource_requirements.cpu_cores > 16:
            warnings.append("High CPU requirement may cause delays")
        
        if workflow_def.resource_requirements.memory_mb > 8192:
            warnings.append("High memory requirement may cause delays")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _check_resource_availability(self, 
                                         requirements: WorkflowResourceRequirements) -> bool:
        """Check if required resources are available"""
        
        # Check CPU availability
        available_cpu = self.resource_pool["cpu_cores"] - self.allocated_resources["cpu_cores"]
        if available_cpu < requirements.cpu_cores:
            return False
        
        # Check memory availability
        available_memory = (self.resource_pool["memory_gb"] * 1024) - self.allocated_resources["memory_mb"]
        if available_memory < requirements.memory_mb:
            return False
        
        return True
    
    async def _allocate_resources(self, requirements: WorkflowResourceRequirements):
        """Allocate resources for workflow execution"""
        
        self.allocated_resources["cpu_cores"] += requirements.cpu_cores
        self.allocated_resources["memory_mb"] += requirements.memory_mb
        self.allocated_resources["storage_mb"] += requirements.storage_mb
    
    async def _deallocate_resources(self, requirements: WorkflowResourceRequirements):
        """Deallocate resources after workflow execution"""
        
        self.allocated_resources["cpu_cores"] -= requirements.cpu_cores
        self.allocated_resources["memory_mb"] -= requirements.memory_mb
        self.allocated_resources["storage_mb"] -= requirements.storage_mb
        
        # Ensure no negative allocations
        for resource in self.allocated_resources:
            if self.allocated_resources[resource] < 0:
                self.allocated_resources[resource] = 0
    
    async def _queue_workflow(self,
                            execution_id: str,
                            workflow_id: str,
                            context: Dict[str, Any],
                            priority: WorkflowPriority):
        """Queue workflow for later execution"""
        
        queue_item = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "context": context,
            "priority": priority,
            "queued_at": datetime.now()
        }
        
        # Insert based on priority
        if priority in [WorkflowPriority.CRITICAL, WorkflowPriority.EMERGENCY]:
            self.queued_workflows.appendleft(queue_item)
        else:
            self.queued_workflows.append(queue_item)
    
    async def _update_workflow_metrics(self,
                                     workflow_def: BrainSAITWorkflowDefinition,
                                     execution_time_ms: float,
                                     success: bool):
        """Update workflow performance metrics"""
        
        metrics = workflow_def.metrics
        if not metrics:
            return
        
        # Update execution counts
        metrics.total_executions += 1
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
        
        # Update timing metrics
        if metrics.min_execution_time_ms == float('inf'):
            metrics.min_execution_time_ms = execution_time_ms
        else:
            metrics.min_execution_time_ms = min(metrics.min_execution_time_ms, execution_time_ms)
        
        metrics.max_execution_time_ms = max(metrics.max_execution_time_ms, execution_time_ms)
        
        # Update average (simple moving average)
        total_time = metrics.average_execution_time_ms * (metrics.total_executions - 1)
        metrics.average_execution_time_ms = (total_time + execution_time_ms) / metrics.total_executions
        
        # Update success rate
        metrics.success_rate = metrics.successful_executions / metrics.total_executions
        
        # Update last execution
        metrics.last_execution = datetime.now()
        
        # Add to execution history (keep last 100)
        metrics.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": execution_time_ms,
            "success": success
        })
        if len(metrics.execution_history) > 100:
            metrics.execution_history.pop(0)

class BrainSAITPyHeart:
    """
    Main BrainSAIT PyHeart Integration Class
    Provides unified workflow and process management for the healthcare ecosystem
    """
    
    def __init__(self, 
                 max_concurrent_workflows: int = 100,
                 enable_distributed_execution: bool = False,
                 redis_url: Optional[str] = None):
        
        # Initialize core components
        self.execution_engine = WorkflowExecutionEngine(max_concurrent_workflows)
        self.pyheart_engine = None
        self.communication_orchestrator = None
        
        # Configuration
        self.enable_distributed = enable_distributed_execution
        self.redis_url = redis_url
        
        # Performance metrics
        self.system_metrics = {
            "total_workflows_registered": 0,
            "total_executions": 0,
            "average_system_load": 0.0,
            "queue_length": 0,
            "active_workflows": 0,
            "system_uptime_hours": 0.0
        }
        
        # Integration status
        self.integrations = {
            "pyheart_engine": False,
            "communication_orchestrator": False,
            "distributed_execution": False,
            "monitoring": True
        }
        
        # Start background tasks
        self._background_tasks = []
        self._start_background_processing()
        
        logger.info("BrainSAIT PyHeart initialized successfully")
    
    async def initialize_healthcare_workflows(self,
                                            pyheart_engine: Optional[PyHeartHealthcareWorkflowEngine] = None,
                                            communication_orchestrator: Optional[CommunicationWorkflowOrchestrator] = None):
        """Initialize healthcare workflow integrations"""
        
        self.pyheart_engine = pyheart_engine
        self.communication_orchestrator = communication_orchestrator
        
        if pyheart_engine:
            self.integrations["pyheart_engine"] = True
            logger.info("PyHeart workflow engine integration initialized")
        
        if communication_orchestrator:
            self.integrations["communication_orchestrator"] = True
            logger.info("Communication workflow orchestrator integration initialized")
        
        # Initialize distributed execution if enabled
        if self.enable_distributed and WORKFLOW_LIBRARIES_AVAILABLE:
            await self._initialize_distributed_execution()
    
    async def register_healthcare_workflow(self,
                                         name: str,
                                         name_ar: str,
                                         workflow_type: HealthcareWorkflowType,
                                         steps: List[Dict[str, Any]],
                                         additional_config: Optional[Dict[str, Any]] = None) -> str:
        """Register a new healthcare workflow"""
        
        # Create workflow definition
        workflow_def = BrainSAITWorkflowDefinition(
            name=name,
            name_ar=name_ar,
            workflow_type=workflow_type,
            steps=steps
        )
        
        # Apply additional configuration
        if additional_config:
            for key, value in additional_config.items():
                if hasattr(workflow_def, key):
                    setattr(workflow_def, key, value)
        
        # Register with execution engine
        await self.execution_engine.register_workflow(workflow_def)
        
        # Update metrics
        self.system_metrics["total_workflows_registered"] += 1
        
        logger.info(f"Healthcare workflow registered: {name} ({workflow_def.workflow_id})")
        
        return workflow_def.workflow_id
    
    async def execute_healthcare_workflow(self,
                                        workflow_id: str,
                                        patient_context: Dict[str, Any],
                                        priority: Optional[WorkflowPriority] = None,
                                        cultural_adaptations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a healthcare workflow with cultural context"""
        
        # Enhance context with cultural adaptations
        enhanced_context = {
            **patient_context,
            "cultural_adaptations": cultural_adaptations or {},
            "execution_timestamp": datetime.now().isoformat(),
            "system_context": {
                "platform": "brainsait",
                "version": "2.0.0",
                "compliance": ["HIPAA", "PDPL"]
            }
        }
        
        # Execute workflow
        result = await self.execution_engine.execute_workflow(
            workflow_id, enhanced_context, priority
        )
        
        # Update system metrics
        self.system_metrics["total_executions"] += 1
        
        return result
    
    async def create_patient_journey_workflow(self,
                                            patient_id: str,
                                            journey_type: str,
                                            milestones: List[Dict[str, Any]]) -> str:
        """Create a personalized patient journey workflow"""
        
        # Convert milestones to workflow steps
        steps = []
        for i, milestone in enumerate(milestones):
            step = {
                "type": "milestone",
                "name": milestone.get("name", f"Milestone {i+1}"),
                "name_ar": milestone.get("name_ar", f"معلم {i+1}"),
                "parameters": {
                    "milestone_type": milestone.get("type", "general"),
                    "description": milestone.get("description", ""),
                    "required_actions": milestone.get("actions", []),
                    "success_criteria": milestone.get("success_criteria", [])
                },
                "timeout_minutes": milestone.get("timeout_minutes", 60)
            }
            steps.append(step)
        
        # Register workflow
        workflow_id = await self.register_healthcare_workflow(
            name=f"Patient Journey - {journey_type}",
            name_ar=f"رحلة المريض - {journey_type}",
            workflow_type=HealthcareWorkflowType.PATIENT_JOURNEY,
            steps=steps,
            additional_config={
                "priority": WorkflowPriority.HIGH,
                "complexity": WorkflowComplexity.COMPLEX,
                "cultural_adaptations": {
                    "patient_id": patient_id,
                    "journey_type": journey_type,
                    "personalized": True
                }
            }
        )
        
        return workflow_id
    
    async def monitor_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """Monitor real-time workflow execution status"""
        
        # Check active workflows
        if execution_id in self.execution_engine.active_workflows:
            workflow_context = self.execution_engine.active_workflows[execution_id]
            return {
                "execution_id": execution_id,
                "status": workflow_context["status"],
                "current_step": workflow_context["current_step"],
                "start_time": workflow_context["start_time"].isoformat(),
                "elapsed_time_ms": (datetime.now() - workflow_context["start_time"]).total_seconds() * 1000,
                "progress": self._calculate_workflow_progress(workflow_context)
            }
        
        # Check completed workflows
        if execution_id in self.execution_engine.completed_workflows:
            return {
                "execution_id": execution_id,
                "status": BrainSAITWorkflowStatus.COMPLETED.value,
                "completed": True
            }
        
        # Check failed workflows
        if execution_id in self.execution_engine.failed_workflows:
            return {
                "execution_id": execution_id,
                "status": BrainSAITWorkflowStatus.FAILED.value,
                "failed": True
            }
        
        return {
            "execution_id": execution_id,
            "status": "not_found",
            "message": "Execution not found"
        }
    
    async def get_workflow_metrics(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive workflow performance metrics"""
        
        if workflow_id:
            # Get specific workflow metrics
            if workflow_id in self.execution_engine.workflow_registry:
                workflow_def = self.execution_engine.workflow_registry[workflow_id]
                return {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_def.name,
                    "metrics": workflow_def.metrics.__dict__ if workflow_def.metrics else {},
                    "resource_requirements": workflow_def.resource_requirements.__dict__,
                    "registered_at": workflow_def.created_at.isoformat()
                }
            else:
                return {"error": f"Workflow {workflow_id} not found"}
        else:
            # Get system-wide metrics
            return {
                "system_metrics": self.system_metrics,
                "execution_engine_stats": self.execution_engine.execution_stats,
                "resource_utilization": {
                    "allocated_cpu_cores": self.execution_engine.allocated_resources["cpu_cores"],
                    "allocated_memory_mb": self.execution_engine.allocated_resources["memory_mb"],
                    "total_cpu_cores": self.execution_engine.resource_pool["cpu_cores"],
                    "total_memory_gb": self.execution_engine.resource_pool["memory_gb"]
                },
                "queue_status": {
                    "queued_workflows": len(self.execution_engine.queued_workflows),
                    "active_workflows": len(self.execution_engine.active_workflows),
                    "completed_workflows": len(self.execution_engine.completed_workflows),
                    "failed_workflows": len(self.execution_engine.failed_workflows)
                },
                "integration_status": self.integrations,
                "timestamp": datetime.now().isoformat()
            }
    
    async def optimize_workflow_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze and optimize workflow performance"""
        
        if workflow_id not in self.execution_engine.workflow_registry:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow_def = self.execution_engine.workflow_registry[workflow_id]
        metrics = workflow_def.metrics
        
        if not metrics or metrics.total_executions < 5:
            return {
                "workflow_id": workflow_id,
                "message": "Insufficient execution data for optimization",
                "recommendations": ["Execute workflow at least 5 times for optimization analysis"]
            }
        
        optimization_recommendations = []
        performance_issues = []
        
        # Analyze execution time
        if metrics.average_execution_time_ms > 30000:  # > 30 seconds
            performance_issues.append("slow_execution")
            optimization_recommendations.extend([
                "Consider breaking down complex steps into smaller ones",
                "Optimize database queries and API calls",
                "Add parallel processing for independent steps"
            ])
        
        # Analyze success rate
        if metrics.success_rate < 0.95:  # < 95%
            performance_issues.append("low_success_rate")
            optimization_recommendations.extend([
                "Add more robust error handling",
                "Implement retry mechanisms for transient failures",
                "Review and strengthen input validation"
            ])
        
        # Analyze resource utilization
        if workflow_def.resource_requirements.cpu_cores > 4:
            performance_issues.append("high_resource_usage")
            optimization_recommendations.append("Consider optimizing CPU-intensive operations")
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_def.name,
            "current_performance": {
                "average_execution_time_ms": metrics.average_execution_time_ms,
                "success_rate": metrics.success_rate,
                "total_executions": metrics.total_executions
            },
            "performance_issues": performance_issues,
            "optimization_recommendations": optimization_recommendations,
            "estimated_improvement": {
                "execution_time_reduction": "20-40%" if "slow_execution" in performance_issues else "5-10%",
                "success_rate_improvement": "2-5%" if "low_success_rate" in performance_issues else "1-2%"
            }
        }
    
    def _calculate_workflow_progress(self, workflow_context: Dict[str, Any]) -> float:
        """Calculate workflow execution progress percentage"""
        
        workflow_id = workflow_context["workflow_id"]
        current_step = workflow_context["current_step"]
        
        if workflow_id in self.execution_engine.workflow_registry:
            workflow_def = self.execution_engine.workflow_registry[workflow_id]
            total_steps = len(workflow_def.steps)
            if total_steps > 0:
                return (current_step / total_steps) * 100
        
        return 0.0
    
    def _start_background_processing(self):
        """Start background processing tasks"""
        
        # Queue processor task
        async def process_queue():
            while True:
                try:
                    if self.execution_engine.queued_workflows:
                        queue_item = self.execution_engine.queued_workflows.popleft()
                        
                        # Check if resources are now available
                        workflow_def = self.execution_engine.workflow_registry.get(queue_item["workflow_id"])
                        if workflow_def and await self.execution_engine._check_resource_availability(workflow_def.resource_requirements):
                            # Execute queued workflow
                            await self.execution_engine._execute_workflow_immediately(
                                queue_item["execution_id"],
                                workflow_def,
                                queue_item["context"],
                                queue_item["priority"]
                            )
                    
                    await asyncio.sleep(1)  # Check queue every second
                    
                except Exception as e:
                    logger.error(f"Queue processing error: {e}")
                    await asyncio.sleep(5)  # Wait longer on error
        
        # System metrics update task
        async def update_system_metrics():
            start_time = datetime.now()
            
            while True:
                try:
                    # Update system metrics
                    self.system_metrics["queue_length"] = len(self.execution_engine.queued_workflows)
                    self.system_metrics["active_workflows"] = len(self.execution_engine.active_workflows)
                    self.system_metrics["system_uptime_hours"] = (datetime.now() - start_time).total_seconds() / 3600
                    
                    # Calculate system load
                    total_resources = self.execution_engine.resource_pool["cpu_cores"]
                    allocated_resources = self.execution_engine.allocated_resources["cpu_cores"]
                    self.system_metrics["average_system_load"] = allocated_resources / total_resources if total_resources > 0 else 0
                    
                    await asyncio.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"System metrics update error: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        
        # Create and store background tasks
        self._background_tasks = [
            asyncio.create_task(process_queue()),
            asyncio.create_task(update_system_metrics())
        ]
    
    async def _initialize_distributed_execution(self):
        """Initialize distributed workflow execution"""
        
        if not WORKFLOW_LIBRARIES_AVAILABLE:
            logger.warning("Celery not available, distributed execution disabled")
            return
        
        try:
            # Initialize Celery for distributed execution
            if self.redis_url:
                celery_app = Celery('brainsait_pyheart', broker=self.redis_url)
                self.integrations["distributed_execution"] = True
                logger.info("Distributed workflow execution initialized")
        except Exception as e:
            logger.error(f"Failed to initialize distributed execution: {e}")

# Export main class
__all__ = [
    "BrainSAITPyHeart",
    "BrainSAITWorkflowDefinition",
    "BrainSAITWorkflowStatus",
    "WorkflowPriority",
    "WorkflowComplexity",
    "BrainSAITWorkflowMetrics"
]
