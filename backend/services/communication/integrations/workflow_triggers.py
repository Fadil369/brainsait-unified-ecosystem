"""
BrainSAIT Healthcare Platform - Workflow Event Trigger Management
Advanced event trigger system for healthcare communication workflows

This module provides comprehensive event trigger management for:
1. Healthcare system event detection and processing
2. Real-time workflow triggering based on clinical events
3. Patient journey milestone tracking and automation
4. NPHIES integration event handling
5. Emergency situation detection and response
6. Cultural and temporal context-aware triggering
7. Intelligent event correlation and workflow orchestration

Key Features:
- Real-time healthcare event processing
- Multi-source event integration (EMR, NPHIES, IoT devices, patient apps)
- Intelligent event filtering and correlation
- Cultural context-aware trigger timing
- Arabic language event processing
- HIPAA-compliant event logging and processing
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
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
from collections import defaultdict

# Healthcare workflow imports
from .pyheart_integration import (
    PyHeartHealthcareWorkflowEngine, WorkflowEventType, HealthcareWorkflowType,
    WorkflowTrigger, HealthcareWorkflowDefinition
)
from ..patient_communication_service import PatientCommunicationData, MessagePriority
from ..healthcare_integration import HealthcareSystemIntegrator, AuditEventType

logger = logging.getLogger(__name__)

# ==================== EVENT TRIGGER ENUMS ====================

class TriggerConditionType(str, Enum):
    """Types of trigger conditions"""
    EXACT_MATCH = "exact_match"
    PATTERN_MATCH = "pattern_match"
    RANGE_CHECK = "range_check"
    TIME_BASED = "time_based"
    FREQUENCY_BASED = "frequency_based"
    CORRELATION_BASED = "correlation_based"
    ML_PREDICTION = "ml_prediction"

class EventSource(str, Enum):
    """Sources of healthcare events"""
    EMR_SYSTEM = "emr_system"
    NPHIES_PLATFORM = "nphies_platform"
    PATIENT_APP = "patient_app"
    IOT_DEVICE = "iot_device"
    LABORATORY = "laboratory"
    PHARMACY = "pharmacy"
    IMAGING_SYSTEM = "imaging_system"
    SCHEDULER = "scheduler"
    BILLING_SYSTEM = "billing_system"
    EMERGENCY_SYSTEM = "emergency_system"
    PROVIDER_PORTAL = "provider_portal"
    MANUAL_ENTRY = "manual_entry"

class TriggerStatus(str, Enum):
    """Trigger processing status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TESTING = "testing"
    ARCHIVED = "archived"

class EventPriority(str, Enum):
    """Event processing priority"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"

# ==================== EVENT DATA MODELS ====================

@dataclass
class HealthcareEvent:
    """Healthcare event data model"""
    event_id: str
    event_type: WorkflowEventType
    source: EventSource
    timestamp: datetime
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    organization_id: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    processed: bool = False
    processing_timestamp: Optional[datetime] = None

class TriggerCondition(BaseModel):
    """Individual trigger condition definition"""
    condition_id: str
    condition_type: TriggerConditionType
    field_path: str  # JSONPath-style field reference
    operator: str  # "equals", "greater_than", "contains", "matches", etc.
    value: Any
    case_sensitive: bool = True
    cultural_context_aware: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TriggerRule(BaseModel):
    """Complete trigger rule with multiple conditions"""
    rule_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    conditions: List[TriggerCondition]
    logical_operator: str = "AND"  # "AND", "OR", "NOT"
    temporal_constraints: Dict[str, Any] = Field(default_factory=dict)
    cultural_constraints: Dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    enabled: bool = True
    testing_mode: bool = False

class AdvancedWorkflowTrigger(BaseModel):
    """Advanced workflow trigger with complex rules"""
    trigger_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    workflow_id: str
    event_types: List[WorkflowEventType]
    event_sources: List[EventSource] = Field(default_factory=list)
    trigger_rules: List[TriggerRule]
    cooldown_period_minutes: int = 0
    max_triggers_per_hour: int = 100
    max_triggers_per_day: int = 1000
    temporal_restrictions: Dict[str, Any] = Field(default_factory=dict)
    cultural_restrictions: Dict[str, Any] = Field(default_factory=dict)
    patient_filters: Dict[str, Any] = Field(default_factory=dict)
    provider_filters: Dict[str, Any] = Field(default_factory=dict)
    status: TriggerStatus = TriggerStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    statistics: Dict[str, Any] = Field(default_factory=dict)

# ==================== EVENT PROCESSORS ====================

class EventProcessor(ABC):
    """Abstract base class for event processors"""
    
    @abstractmethod
    async def process_event(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process a healthcare event"""
        pass
    
    @abstractmethod
    def can_process(self, event: HealthcareEvent) -> bool:
        """Check if this processor can handle the event"""
        pass

class NPHIESEventProcessor(EventProcessor):
    """Process NPHIES-specific events"""
    
    async def process_event(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process NPHIES event"""
        try:
            if event.event_type == WorkflowEventType.APPOINTMENT_SCHEDULED:
                # Handle NPHIES appointment scheduling
                return await self._process_nphies_appointment(event)
            
            elif event.event_type == WorkflowEventType.RESULTS_AVAILABLE:
                # Handle NPHIES lab results
                return await self._process_nphies_results(event)
            
            elif event.event_type == WorkflowEventType.INSURANCE_DENIED:
                # Handle NPHIES insurance denial
                return await self._process_nphies_insurance_denial(event)
            
            return {"success": True, "processed": True}
            
        except Exception as e:
            logger.error(f"NPHIES event processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def can_process(self, event: HealthcareEvent) -> bool:
        """Check if event is from NPHIES"""
        return event.source == EventSource.NPHIES_PLATFORM
    
    async def _process_nphies_appointment(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process NPHIES appointment event"""
        # Extract NPHIES-specific appointment data
        nphies_data = event.data.get("nphies_data", {})
        
        # Validate NPHIES compliance
        if not self._validate_nphies_appointment(nphies_data):
            return {"success": False, "error": "NPHIES validation failed"}
        
        # Enrich event with NPHIES context
        event.metadata["nphies_validated"] = True
        event.metadata["nphies_appointment_id"] = nphies_data.get("appointment_id")
        
        return {"success": True, "nphies_processed": True}
    
    async def _process_nphies_results(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process NPHIES results event"""
        # Handle NPHIES lab results with proper compliance
        results_data = event.data.get("results", {})
        
        # Check for critical values that require immediate notification
        if self._is_critical_result(results_data):
            event.priority = EventPriority.CRITICAL
            event.metadata["critical_result"] = True
        
        return {"success": True, "results_processed": True}
    
    async def _process_nphies_insurance_denial(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process NPHIES insurance denial"""
        denial_data = event.data.get("denial_info", {})
        
        # Enrich with denial reason and next steps
        event.metadata["denial_reason"] = denial_data.get("reason")
        event.metadata["appeal_deadline"] = denial_data.get("appeal_deadline")
        
        return {"success": True, "denial_processed": True}
    
    def _validate_nphies_appointment(self, nphies_data: Dict[str, Any]) -> bool:
        """Validate NPHIES appointment data"""
        required_fields = ["appointment_id", "provider_id", "patient_national_id"]
        return all(field in nphies_data for field in required_fields)
    
    def _is_critical_result(self, results_data: Dict[str, Any]) -> bool:
        """Check if lab result is critical"""
        critical_indicators = [
            "critical_high", "critical_low", "panic_value", "immediate_attention"
        ]
        result_flags = results_data.get("flags", [])
        return any(flag in critical_indicators for flag in result_flags)

class ClinicalEventProcessor(EventProcessor):
    """Process clinical events from EMR systems"""
    
    async def process_event(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process clinical event"""
        try:
            if event.event_type == WorkflowEventType.CRITICAL_RESULT:
                return await self._process_critical_result(event)
            
            elif event.event_type == WorkflowEventType.MEDICATION_REMINDER:
                return await self._process_medication_reminder(event)
            
            elif event.event_type == WorkflowEventType.CHRONIC_CARE_REMINDER:
                return await self._process_chronic_care_reminder(event)
            
            return {"success": True, "processed": True}
            
        except Exception as e:
            logger.error(f"Clinical event processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def can_process(self, event: HealthcareEvent) -> bool:
        """Check if event is clinical"""
        clinical_sources = [EventSource.EMR_SYSTEM, EventSource.LABORATORY, EventSource.IMAGING_SYSTEM]
        return event.source in clinical_sources
    
    async def _process_critical_result(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process critical clinical result"""
        result_data = event.data.get("clinical_result", {})
        
        # Determine urgency level
        severity = result_data.get("severity", "normal")
        if severity in ["critical", "panic"]:
            event.priority = EventPriority.CRITICAL
            event.metadata["immediate_notification"] = True
        
        # Add clinical context
        event.metadata["result_type"] = result_data.get("test_type")
        event.metadata["abnormal_values"] = result_data.get("abnormal_values", [])
        
        return {"success": True, "critical_result_processed": True}
    
    async def _process_medication_reminder(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process medication reminder event"""
        medication_data = event.data.get("medication", {})
        
        # Check for adherence patterns
        adherence_rate = medication_data.get("adherence_rate", 100)
        if adherence_rate < 70:
            event.priority = EventPriority.HIGH
            event.metadata["poor_adherence"] = True
        
        return {"success": True, "medication_reminder_processed": True}
    
    async def _process_chronic_care_reminder(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process chronic care reminder event"""
        chronic_data = event.data.get("chronic_care", {})
        
        # Add chronic care context
        event.metadata["condition_type"] = chronic_data.get("condition")
        event.metadata["care_plan_id"] = chronic_data.get("care_plan_id")
        
        return {"success": True, "chronic_care_processed": True}

class PatientAppEventProcessor(EventProcessor):
    """Process events from patient mobile app"""
    
    async def process_event(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process patient app event"""
        try:
            app_data = event.data.get("app_data", {})
            
            # Add patient engagement context
            event.metadata["app_version"] = app_data.get("app_version")
            event.metadata["device_type"] = app_data.get("device_type")
            event.metadata["engagement_score"] = app_data.get("engagement_score", 0)
            
            return {"success": True, "patient_app_processed": True}
            
        except Exception as e:
            logger.error(f"Patient app event processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def can_process(self, event: HealthcareEvent) -> bool:
        """Check if event is from patient app"""
        return event.source == EventSource.PATIENT_APP

# ==================== MAIN TRIGGER MANAGER ====================

class HealthcareWorkflowTriggerManager:
    """
    Comprehensive healthcare workflow trigger management system
    
    Handles real-time event processing, trigger evaluation, and workflow initiation
    with full support for Saudi healthcare ecosystem and Arabic language processing
    """
    
    def __init__(self, 
                 workflow_engine: PyHeartHealthcareWorkflowEngine,
                 healthcare_integrator: HealthcareSystemIntegrator):
        """
        Initialize the trigger manager
        
        Args:
            workflow_engine: PyHeart workflow engine instance
            healthcare_integrator: Healthcare system integrator
        """
        self.workflow_engine = workflow_engine
        self.healthcare_integrator = healthcare_integrator
        
        # Trigger management
        self.active_triggers: Dict[str, AdvancedWorkflowTrigger] = {}
        self.trigger_rules: Dict[str, TriggerRule] = {}
        self.event_queue: List[HealthcareEvent] = []
        self.processing_stats: Dict[str, Any] = defaultdict(int)
        
        # Event processors
        self.event_processors: List[EventProcessor] = [
            NPHIESEventProcessor(),
            ClinicalEventProcessor(),
            PatientAppEventProcessor()
        ]
        
        # Cultural and temporal context
        self.saudi_timezone = pytz.timezone('Asia/Riyadh')
        self.islamic_calendar_enabled = True
        self.prayer_time_respect = True
        
        # Configuration
        self.config = {
            "max_concurrent_events": 100,
            "event_retention_hours": 24,
            "trigger_evaluation_interval_seconds": 5,
            "correlation_window_minutes": 30,
            "max_workflow_triggers_per_minute": 50
        }
        
        logger.info("Healthcare Workflow Trigger Manager initialized")
    
    # ==================== TRIGGER REGISTRATION ====================
    
    async def register_workflow_trigger(self, trigger: AdvancedWorkflowTrigger) -> Dict[str, Any]:
        """Register a new workflow trigger"""
        try:
            # Validate trigger
            validation_result = await self._validate_trigger(trigger)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Trigger validation failed",
                    "validation_errors": validation_result["errors"]
                }
            
            # Register trigger
            self.active_triggers[trigger.trigger_id] = trigger
            
            # Register associated rules
            for rule in trigger.trigger_rules:
                self.trigger_rules[rule.rule_id] = rule
            
            # Initialize statistics
            trigger.statistics = {
                "total_evaluations": 0,
                "total_matches": 0,
                "total_workflows_triggered": 0,
                "last_triggered": None,
                "average_evaluation_time_ms": 0
            }
            
            logger.info(f"Workflow trigger registered: {trigger.trigger_id}")
            
            return {
                "success": True,
                "trigger_id": trigger.trigger_id,
                "registered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to register workflow trigger: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_trigger(self, trigger: AdvancedWorkflowTrigger) -> Dict[str, Any]:
        """Validate workflow trigger"""
        errors = []
        
        # Check required fields
        if not trigger.name:
            errors.append("Trigger name is required")
        
        if not trigger.workflow_id:
            errors.append("Workflow ID is required")
        
        if not trigger.event_types:
            errors.append("At least one event type is required")
        
        if not trigger.trigger_rules:
            errors.append("At least one trigger rule is required")
        
        # Validate trigger rules
        for rule in trigger.trigger_rules:
            rule_validation = await self._validate_trigger_rule(rule)
            if not rule_validation["valid"]:
                errors.extend(rule_validation["errors"])
        
        # Validate temporal restrictions
        if trigger.temporal_restrictions:
            temporal_validation = self._validate_temporal_restrictions(trigger.temporal_restrictions)
            if not temporal_validation["valid"]:
                errors.extend(temporal_validation["errors"])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _validate_trigger_rule(self, rule: TriggerRule) -> Dict[str, Any]:
        """Validate individual trigger rule"""
        errors = []
        
        if not rule.conditions:
            errors.append(f"Rule {rule.rule_id} must have at least one condition")
        
        # Validate conditions
        for condition in rule.conditions:
            if not condition.field_path:
                errors.append(f"Condition {condition.condition_id} must have a field path")
            
            if not condition.operator:
                errors.append(f"Condition {condition.condition_id} must have an operator")
        
        # Validate logical operator
        if rule.logical_operator not in ["AND", "OR", "NOT"]:
            errors.append(f"Invalid logical operator: {rule.logical_operator}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_temporal_restrictions(self, restrictions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate temporal restrictions"""
        errors = []
        
        # Validate time windows
        if "time_windows" in restrictions:
            time_windows = restrictions["time_windows"]
            for window in time_windows:
                if "start_time" not in window or "end_time" not in window:
                    errors.append("Time window must have start_time and end_time")
        
        # Validate day restrictions
        if "allowed_days" in restrictions:
            allowed_days = restrictions["allowed_days"]
            valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for day in allowed_days:
                if day.lower() not in valid_days:
                    errors.append(f"Invalid day: {day}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    # ==================== EVENT PROCESSING ====================
    
    async def process_healthcare_event(self, event: HealthcareEvent) -> Dict[str, Any]:
        """Process incoming healthcare event"""
        try:
            processing_start = datetime.now()
            
            # Add event to queue
            self.event_queue.append(event)
            
            # Process event through event processors
            for processor in self.event_processors:
                if processor.can_process(event):
                    await processor.process_event(event)
            
            # Evaluate triggers
            triggered_workflows = await self._evaluate_triggers_for_event(event)
            
            # Update processing statistics
            processing_time = (datetime.now() - processing_start).total_seconds() * 1000
            self.processing_stats["total_events_processed"] += 1
            self.processing_stats["total_processing_time_ms"] += processing_time
            self.processing_stats["workflows_triggered"] += len(triggered_workflows)
            
            # Mark event as processed
            event.processed = True
            event.processing_timestamp = datetime.now()
            
            # Audit log
            await self._audit_event_processing(event, triggered_workflows)
            
            return {
                "success": True,
                "event_id": event.event_id,
                "triggered_workflows": triggered_workflows,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Event processing failed for {event.event_id}: {e}")
            return {
                "success": False,
                "event_id": event.event_id,
                "error": str(e)
            }
    
    async def _evaluate_triggers_for_event(self, event: HealthcareEvent) -> List[Dict[str, Any]]:
        """Evaluate all triggers for an event"""
        triggered_workflows = []
        
        for trigger_id, trigger in self.active_triggers.items():
            if trigger.status != TriggerStatus.ACTIVE:
                continue
            
            # Check if event type matches
            if event.event_type not in trigger.event_types:
                continue
            
            # Check event source filter
            if trigger.event_sources and event.source not in trigger.event_sources:
                continue
            
            # Check temporal restrictions
            if not await self._check_temporal_restrictions(trigger, event):
                continue
            
            # Check cultural restrictions
            if not await self._check_cultural_restrictions(trigger, event):
                continue
            
            # Check cooldown period
            if not self._check_cooldown_period(trigger):
                continue
            
            # Check rate limits
            if not self._check_rate_limits(trigger):
                continue
            
            # Evaluate trigger rules
            if await self._evaluate_trigger_rules(trigger, event):
                # Trigger workflow
                workflow_result = await self._trigger_workflow(trigger, event)
                triggered_workflows.append(workflow_result)
                
                # Update trigger statistics
                trigger.statistics["total_matches"] += 1
                trigger.statistics["last_triggered"] = datetime.now().isoformat()
                
                if workflow_result.get("success"):
                    trigger.statistics["total_workflows_triggered"] += 1
        
        return triggered_workflows
    
    async def _check_temporal_restrictions(self, trigger: AdvancedWorkflowTrigger, event: HealthcareEvent) -> bool:
        """Check if event passes temporal restrictions"""
        if not trigger.temporal_restrictions:
            return True
        
        current_time = datetime.now(self.saudi_timezone)
        
        # Check time windows
        if "time_windows" in trigger.temporal_restrictions:
            time_windows = trigger.temporal_restrictions["time_windows"]
            current_time_str = current_time.strftime("%H:%M")
            
            time_allowed = False
            for window in time_windows:
                start_time = window["start_time"]
                end_time = window["end_time"]
                
                if start_time <= current_time_str <= end_time:
                    time_allowed = True
                    break
            
            if not time_allowed:
                return False
        
        # Check allowed days
        if "allowed_days" in trigger.temporal_restrictions:
            allowed_days = trigger.temporal_restrictions["allowed_days"]
            current_day = current_time.strftime("%A").lower()
            
            if current_day not in [day.lower() for day in allowed_days]:
                return False
        
        # Check prayer time restrictions
        if self.prayer_time_respect and "respect_prayer_times" in trigger.temporal_restrictions:
            if trigger.temporal_restrictions["respect_prayer_times"]:
                if self._is_prayer_time(current_time):
                    return False
        
        return True
    
    async def _check_cultural_restrictions(self, trigger: AdvancedWorkflowTrigger, event: HealthcareEvent) -> bool:
        """Check if event passes cultural restrictions"""
        if not trigger.cultural_restrictions:
            return True
        
        # Check Ramadan restrictions
        if "ramadan_aware" in trigger.cultural_restrictions:
            if trigger.cultural_restrictions["ramadan_aware"]:
                if self._is_ramadan_period():
                    # Apply Ramadan-specific timing restrictions
                    current_hour = datetime.now(self.saudi_timezone).hour
                    if 6 <= current_hour <= 18:  # Daylight hours during Ramadan
                        return False
        
        # Check Islamic holidays
        if "islamic_holidays_aware" in trigger.cultural_restrictions:
            if trigger.cultural_restrictions["islamic_holidays_aware"]:
                if self._is_islamic_holiday():
                    return False
        
        return True
    
    def _check_cooldown_period(self, trigger: AdvancedWorkflowTrigger) -> bool:
        """Check trigger cooldown period"""
        if trigger.cooldown_period_minutes == 0:
            return True
        
        last_triggered = trigger.statistics.get("last_triggered")
        if not last_triggered:
            return True
        
        last_triggered_dt = datetime.fromisoformat(last_triggered.replace('Z', '+00:00'))
        cooldown_end = last_triggered_dt + timedelta(minutes=trigger.cooldown_period_minutes)
        
        return datetime.now() >= cooldown_end
    
    def _check_rate_limits(self, trigger: AdvancedWorkflowTrigger) -> bool:
        """Check trigger rate limits"""
        # This would implement rate limiting logic
        # For now, return True
        return True
    
    async def _evaluate_trigger_rules(self, trigger: AdvancedWorkflowTrigger, event: HealthcareEvent) -> bool:
        """Evaluate all trigger rules for an event"""
        try:
            for rule in trigger.trigger_rules:
                if not rule.enabled:
                    continue
                
                rule_result = await self._evaluate_single_rule(rule, event)
                
                # For now, use AND logic between rules
                # Could be enhanced to support more complex rule combinations
                if not rule_result:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule evaluation failed: {e}")
            return False
    
    async def _evaluate_single_rule(self, rule: TriggerRule, event: HealthcareEvent) -> bool:
        """Evaluate a single trigger rule"""
        condition_results = []
        
        for condition in rule.conditions:
            result = await self._evaluate_condition(condition, event)
            condition_results.append(result)
        
        # Apply logical operator
        if rule.logical_operator == "AND":
            return all(condition_results)
        elif rule.logical_operator == "OR":
            return any(condition_results)
        elif rule.logical_operator == "NOT":
            return not any(condition_results)
        
        return False
    
    async def _evaluate_condition(self, condition: TriggerCondition, event: HealthcareEvent) -> bool:
        """Evaluate a single trigger condition"""
        try:
            # Get field value using JSONPath-style field reference
            field_value = self._get_field_value(event, condition.field_path)
            
            if field_value is None:
                return False
            
            # Apply condition based on type and operator
            if condition.condition_type == TriggerConditionType.EXACT_MATCH:
                return self._evaluate_exact_match(field_value, condition)
            
            elif condition.condition_type == TriggerConditionType.PATTERN_MATCH:
                return self._evaluate_pattern_match(field_value, condition)
            
            elif condition.condition_type == TriggerConditionType.RANGE_CHECK:
                return self._evaluate_range_check(field_value, condition)
            
            elif condition.condition_type == TriggerConditionType.TIME_BASED:
                return self._evaluate_time_based(field_value, condition)
            
            elif condition.condition_type == TriggerConditionType.FREQUENCY_BASED:
                return await self._evaluate_frequency_based(field_value, condition, event)
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _get_field_value(self, event: HealthcareEvent, field_path: str) -> Any:
        """Get field value from event using field path"""
        try:
            # Simple dot notation parsing
            parts = field_path.split('.')
            value = event
            
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _evaluate_exact_match(self, field_value: Any, condition: TriggerCondition) -> bool:
        """Evaluate exact match condition"""
        if condition.operator == "equals":
            if isinstance(field_value, str) and not condition.case_sensitive:
                return field_value.lower() == str(condition.value).lower()
            return field_value == condition.value
        
        elif condition.operator == "not_equals":
            return field_value != condition.value
        
        elif condition.operator == "in":
            return field_value in condition.value
        
        elif condition.operator == "not_in":
            return field_value not in condition.value
        
        return False
    
    def _evaluate_pattern_match(self, field_value: Any, condition: TriggerCondition) -> bool:
        """Evaluate pattern match condition"""
        if not isinstance(field_value, str):
            field_value = str(field_value)
        
        pattern = str(condition.value)
        flags = 0 if condition.case_sensitive else re.IGNORECASE
        
        if condition.operator == "matches":
            return bool(re.match(pattern, field_value, flags))
        
        elif condition.operator == "contains":
            return bool(re.search(pattern, field_value, flags))
        
        elif condition.operator == "starts_with":
            return field_value.startswith(pattern)
        
        elif condition.operator == "ends_with":
            return field_value.endswith(pattern)
        
        return False
    
    def _evaluate_range_check(self, field_value: Any, condition: TriggerCondition) -> bool:
        """Evaluate range check condition"""
        try:
            if condition.operator == "greater_than":
                return float(field_value) > float(condition.value)
            
            elif condition.operator == "greater_than_or_equal":
                return float(field_value) >= float(condition.value)
            
            elif condition.operator == "less_than":
                return float(field_value) < float(condition.value)
            
            elif condition.operator == "less_than_or_equal":
                return float(field_value) <= float(condition.value)
            
            elif condition.operator == "between":
                min_val, max_val = condition.value
                return min_val <= float(field_value) <= max_val
            
            return False
            
        except (ValueError, TypeError):
            return False
    
    def _evaluate_time_based(self, field_value: Any, condition: TriggerCondition) -> bool:
        """Evaluate time-based condition"""
        try:
            if isinstance(field_value, str):
                field_time = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
            elif isinstance(field_value, datetime):
                field_time = field_value
            else:
                return False
            
            if condition.operator == "before":
                compare_time = datetime.fromisoformat(condition.value.replace('Z', '+00:00'))
                return field_time < compare_time
            
            elif condition.operator == "after":
                compare_time = datetime.fromisoformat(condition.value.replace('Z', '+00:00'))
                return field_time > compare_time
            
            elif condition.operator == "within_last":
                # condition.value should be like "30_minutes", "2_hours", "1_day"
                time_unit = condition.value
                if time_unit.endswith("_minutes"):
                    minutes = int(time_unit.split("_")[0])
                    cutoff_time = datetime.now() - timedelta(minutes=minutes)
                elif time_unit.endswith("_hours"):
                    hours = int(time_unit.split("_")[0])
                    cutoff_time = datetime.now() - timedelta(hours=hours)
                elif time_unit.endswith("_days"):
                    days = int(time_unit.split("_")[0])
                    cutoff_time = datetime.now() - timedelta(days=days)
                else:
                    return False
                
                return field_time >= cutoff_time
            
            return False
            
        except (ValueError, TypeError):
            return False
    
    async def _evaluate_frequency_based(self, field_value: Any, condition: TriggerCondition, event: HealthcareEvent) -> bool:
        """Evaluate frequency-based condition"""
        # This would implement frequency analysis
        # For now, return True
        return True
    
    async def _trigger_workflow(self, trigger: AdvancedWorkflowTrigger, event: HealthcareEvent) -> Dict[str, Any]:
        """Trigger workflow execution"""
        try:
            # Get patient data if available
            patient_data = None
            if event.patient_id:
                patient_data = await self._get_patient_data(event.patient_id)
            
            # Prepare healthcare context
            healthcare_context = {
                "triggering_event": {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "source": event.source.value,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data
                },
                "trigger_info": {
                    "trigger_id": trigger.trigger_id,
                    "trigger_name": trigger.name,
                    "trigger_name_ar": trigger.name_ar
                }
            }
            
            # Trigger workflow
            if patient_data:
                result = await self.workflow_engine.trigger_workflow(
                    event.event_type,
                    event.data,
                    patient_data,
                    healthcare_context
                )
            else:
                # Handle system-level workflows without patient context
                result = {"success": False, "error": "Patient data required but not available"}
            
            return {
                "success": result.get("success", False),
                "trigger_id": trigger.trigger_id,
                "workflow_id": trigger.workflow_id,
                "event_id": event.event_id,
                "execution_result": result
            }
            
        except Exception as e:
            logger.error(f"Workflow triggering failed: {e}")
            return {
                "success": False,
                "trigger_id": trigger.trigger_id,
                "error": str(e)
            }
    
    async def _get_patient_data(self, patient_id: str) -> Optional[PatientCommunicationData]:
        """Get patient communication data"""
        # This would integrate with the patient data service
        # For now, return a placeholder
        return None
    
    # ==================== CULTURAL AND TEMPORAL UTILITIES ====================
    
    def _is_prayer_time(self, current_time: datetime) -> bool:
        """Check if current time is during prayer hours"""
        # Simplified prayer time check (would integrate with proper prayer time calculation)
        hour = current_time.hour
        # Basic prayer times for Riyadh (would be calculated dynamically)
        prayer_hours = [5, 12, 15, 18, 19]  # Fajr, Dhuhr, Asr, Maghrib, Isha
        return hour in prayer_hours
    
    def _is_ramadan_period(self) -> bool:
        """Check if current period is Ramadan"""
        # This would integrate with Islamic calendar calculation
        return False  # Placeholder
    
    def _is_islamic_holiday(self) -> bool:
        """Check if current date is an Islamic holiday"""
        # This would integrate with Islamic calendar calculation
        return False  # Placeholder
    
    # ==================== MONITORING AND STATISTICS ====================
    
    async def get_trigger_statistics(self, trigger_id: str) -> Dict[str, Any]:
        """Get statistics for a specific trigger"""
        try:
            if trigger_id not in self.active_triggers:
                return {"error": "Trigger not found"}
            
            trigger = self.active_triggers[trigger_id]
            stats = trigger.statistics.copy()
            
            # Calculate additional metrics
            total_evaluations = stats.get("total_evaluations", 0)
            total_matches = stats.get("total_matches", 0)
            
            if total_evaluations > 0:
                stats["match_rate_percent"] = (total_matches / total_evaluations) * 100
            else:
                stats["match_rate_percent"] = 0
            
            stats["trigger_info"] = {
                "trigger_id": trigger.trigger_id,
                "name": trigger.name,
                "status": trigger.status.value,
                "created_at": trigger.created_at.isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get trigger statistics: {e}")
            return {"error": str(e)}
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get overall event processing statistics"""
        try:
            stats = self.processing_stats.copy()
            
            # Calculate derived metrics
            total_events = stats.get("total_events_processed", 0)
            total_time_ms = stats.get("total_processing_time_ms", 0)
            
            if total_events > 0:
                stats["average_processing_time_ms"] = total_time_ms / total_events
            else:
                stats["average_processing_time_ms"] = 0
            
            # Add trigger statistics
            stats["active_triggers_count"] = len(self.active_triggers)
            stats["total_trigger_rules"] = len(self.trigger_rules)
            
            # Add queue statistics
            stats["current_queue_size"] = len(self.event_queue)
            stats["processed_events_in_queue"] = len([e for e in self.event_queue if e.processed])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {"error": str(e)}
    
    async def _audit_event_processing(self, event: HealthcareEvent, triggered_workflows: List[Dict[str, Any]]):
        """Audit event processing for compliance"""
        try:
            audit_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "source": event.source.value,
                "patient_id": event.patient_id,
                "provider_id": event.provider_id,
                "processed_at": event.processing_timestamp.isoformat() if event.processing_timestamp else None,
                "triggered_workflows_count": len(triggered_workflows),
                "triggered_workflow_ids": [tw.get("workflow_id") for tw in triggered_workflows if tw.get("success")]
            }
            
            # Log to healthcare integrator audit system
            await self.healthcare_integrator.audit_logger.log_communication_event(
                AuditEventType.COMMUNICATION_SENT,
                audit_data,
                None,  # patient_data would be passed if available
                None,  # user_id would be passed if available
                True
            )
            
        except Exception as e:
            logger.error(f"Event processing audit failed: {e}")

# Export main class
__all__ = ["HealthcareWorkflowTriggerManager", "AdvancedWorkflowTrigger", "TriggerRule", "TriggerCondition", "HealthcareEvent"]