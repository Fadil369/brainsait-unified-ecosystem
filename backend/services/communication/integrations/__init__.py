"""
BrainSAIT Healthcare Platform - PyHeart Workflow Engine Integration Module
Comprehensive healthcare communication workflow engine with Saudi Arabian healthcare ecosystem support

This module provides:
1. PyHeart-inspired workflow engine for healthcare communications
2. Pre-built healthcare workflow templates and definitions
3. Advanced event trigger management system
4. Comprehensive workflow monitoring and analytics
5. HIPAA/PDPL compliance integration
6. Arabic language and cultural context support
7. NPHIES and Saudi healthcare regulation compliance

Main Components:
- PyHeartHealthcareWorkflowEngine: Core workflow execution engine
- HealthcareWorkflowTemplates: Pre-built workflow definitions
- HealthcareWorkflowTriggerManager: Event-driven trigger system
- HealthcareWorkflowMonitor: Real-time monitoring and analytics

Usage:
    from backend.services.communication.integrations import (
        PyHeartHealthcareWorkflowEngine,
        HealthcareWorkflowTemplates,
        HealthcareWorkflowTriggerManager,
        HealthcareWorkflowMonitor
    )
"""

from .pyheart_integration import (
    PyHeartHealthcareWorkflowEngine,
    HealthcareWorkflowDefinition,
    WorkflowTrigger,
    WorkflowStep,
    WorkflowEventType,
    HealthcareWorkflowType,
    WorkflowState,
    WorkflowExecution,
    WorkflowContext
)

from .workflow_definitions import (
    HealthcareWorkflowTemplates
)

from .workflow_triggers import (
    HealthcareWorkflowTriggerManager,
    AdvancedWorkflowTrigger,
    TriggerRule,
    TriggerCondition,
    HealthcareEvent,
    EventSource,
    TriggerStatus
)

from .workflow_monitor import (
    HealthcareWorkflowMonitor,
    WorkflowAnalytics,
    PatientEngagementProfile,
    PerformanceAlert,
    MetricType,
    AnalyticsTimeframe,
    AlertSeverity,
    ReportType
)

__version__ = "1.0.0"
__author__ = "BrainSAIT Healthcare Technology Team"

# Export main classes for easy importing
__all__ = [
    # Core workflow engine
    "PyHeartHealthcareWorkflowEngine",
    "HealthcareWorkflowDefinition",
    "WorkflowTrigger",
    "WorkflowStep",
    "WorkflowEventType",
    "HealthcareWorkflowType",
    "WorkflowState",
    "WorkflowExecution",
    "WorkflowContext",
    
    # Workflow templates
    "HealthcareWorkflowTemplates",
    
    # Trigger management
    "HealthcareWorkflowTriggerManager",
    "AdvancedWorkflowTrigger",
    "TriggerRule",
    "TriggerCondition",
    "HealthcareEvent",
    "EventSource",
    "TriggerStatus",
    
    # Monitoring and analytics
    "HealthcareWorkflowMonitor",
    "WorkflowAnalytics",
    "PatientEngagementProfile",
    "PerformanceAlert",
    "MetricType",
    "AnalyticsTimeframe",
    "AlertSeverity",
    "ReportType"
]