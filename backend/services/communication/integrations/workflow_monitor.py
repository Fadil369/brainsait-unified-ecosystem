"""
BrainSAIT Healthcare Platform - Workflow Monitoring and Analytics System
Advanced monitoring, analytics, and optimization for healthcare communication workflows

This module provides comprehensive workflow monitoring capabilities:
1. Real-time workflow execution monitoring
2. Performance analytics and optimization insights
3. Patient engagement and communication effectiveness tracking
4. Healthcare outcome correlation analysis
5. HIPAA-compliant audit reporting and compliance monitoring
6. Arabic language communication analytics
7. Saudi healthcare regulation compliance reporting
8. Machine learning-powered workflow optimization recommendations

Key Features:
- Real-time workflow execution dashboards
- Performance metrics and KPI tracking
- Patient satisfaction and engagement analytics
- Communication channel effectiveness analysis
- Predictive analytics for workflow optimization
- Compliance monitoring and automated reporting
- Cultural context analytics for Saudi healthcare
- Integration with business intelligence systems
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import asyncio
import json
import logging
import uuid
import statistics
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Healthcare workflow imports
from .pyheart_integration import (
    PyHeartHealthcareWorkflowEngine, WorkflowExecution, WorkflowState, 
    HealthcareWorkflowType, WorkflowEventType
)
from .workflow_triggers import HealthcareWorkflowTriggerManager, HealthcareEvent
from ..patient_communication_service import PatientCommunicationData, CommunicationChannel, Language
from ..healthcare_integration import HealthcareSystemIntegrator, AuditEventType

logger = logging.getLogger(__name__)

# ==================== MONITORING ENUMS ====================

class MetricType(str, Enum):
    """Types of workflow metrics"""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    PATIENT_ENGAGEMENT = "patient_engagement"
    COMMUNICATION_EFFECTIVENESS = "communication_effectiveness"
    COMPLIANCE_SCORE = "compliance_score"
    RESOURCE_UTILIZATION = "resource_utilization"
    COST_EFFECTIVENESS = "cost_effectiveness"
    CLINICAL_OUTCOME = "clinical_outcome"

class AnalyticsTimeframe(str, Enum):
    """Analytics time frames"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ReportType(str, Enum):
    """Types of generated reports"""
    PERFORMANCE_SUMMARY = "performance_summary"
    COMPLIANCE_AUDIT = "compliance_audit"
    PATIENT_ENGAGEMENT = "patient_engagement"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    COST_ANALYSIS = "cost_analysis"
    CLINICAL_OUTCOMES = "clinical_outcomes"
    CULTURAL_ANALYTICS = "cultural_analytics"

# ==================== MONITORING DATA MODELS ====================

@dataclass
class WorkflowMetric:
    """Individual workflow metric data point"""
    metric_id: str
    workflow_id: str
    execution_id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    patient_id: Optional[str] = None
    provider_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """Performance monitoring alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowAnalytics(BaseModel):
    """Comprehensive workflow analytics data"""
    workflow_id: str
    workflow_type: HealthcareWorkflowType
    timeframe: AnalyticsTimeframe
    start_date: datetime
    end_date: datetime
    
    # Execution metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time_seconds: float = 0.0
    median_execution_time_seconds: float = 0.0
    
    # Patient engagement metrics
    patient_response_rate: float = 0.0
    average_response_time_minutes: float = 0.0
    communication_satisfaction_score: float = 0.0
    preferred_communication_channels: Dict[str, int] = Field(default_factory=dict)
    
    # Language and cultural metrics
    arabic_communication_percentage: float = 0.0
    english_communication_percentage: float = 0.0
    prayer_time_delays: int = 0
    cultural_adaptations_applied: int = 0
    
    # Clinical outcome metrics
    clinical_adherence_rate: float = 0.0
    appointment_show_rate: float = 0.0
    medication_adherence_rate: float = 0.0
    patient_satisfaction_score: float = 0.0
    
    # Cost and efficiency metrics
    cost_per_communication: float = 0.0
    resource_utilization_rate: float = 0.0
    automation_rate: float = 0.0
    
    # Compliance metrics
    hipaa_compliance_score: float = 100.0
    nphies_compliance_score: float = 100.0
    audit_findings_count: int = 0

class PatientEngagementProfile(BaseModel):
    """Patient engagement analytics profile"""
    patient_id: str
    total_communications_received: int = 0
    total_responses_sent: int = 0
    response_rate: float = 0.0
    average_response_time_hours: float = 0.0
    preferred_language: Language = Language.ARABIC
    preferred_channels: List[CommunicationChannel] = Field(default_factory=list)
    engagement_score: float = 0.0
    satisfaction_scores: List[float] = Field(default_factory=list)
    workflow_completion_rate: float = 0.0
    last_engagement: Optional[datetime] = None
    communication_history: List[Dict[str, Any]] = Field(default_factory=list)

# ==================== ANALYTICS ENGINES ====================

class AnalyticsEngine(ABC):
    """Abstract base class for analytics engines"""
    
    @abstractmethod
    async def calculate_metrics(self, data: Any) -> Dict[str, Any]:
        """Calculate metrics from data"""
        pass
    
    @abstractmethod
    def get_supported_metrics(self) -> List[MetricType]:
        """Get list of supported metric types"""
        pass

class WorkflowPerformanceEngine(AnalyticsEngine):
    """Analytics engine for workflow performance metrics"""
    
    async def calculate_metrics(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate workflow performance metrics"""
        try:
            if not executions:
                return {}
            
            # Basic execution metrics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.state == WorkflowState.COMPLETED])
            failed_executions = len([e for e in executions if e.state == WorkflowState.FAILED])
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Execution time metrics
            completed_executions = [e for e in executions if e.completed_at and e.started_at]
            execution_times = [
                (e.completed_at - e.started_at).total_seconds() 
                for e in completed_executions
            ]
            
            avg_execution_time = statistics.mean(execution_times) if execution_times else 0
            median_execution_time = statistics.median(execution_times) if execution_times else 0
            
            # Step analysis
            total_steps = sum(len(e.step_history) for e in executions)
            avg_steps_per_execution = total_steps / total_executions if total_executions > 0 else 0
            
            # Error analysis
            error_patterns = Counter()
            for execution in executions:
                if execution.state == WorkflowState.FAILED and execution.error_message:
                    error_patterns[execution.error_message] += 1
            
            return {
                "execution_metrics": {
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "success_rate_percent": round(success_rate, 2),
                    "average_execution_time_seconds": round(avg_execution_time, 2),
                    "median_execution_time_seconds": round(median_execution_time, 2),
                    "average_steps_per_execution": round(avg_steps_per_execution, 2)
                },
                "error_analysis": {
                    "top_errors": dict(error_patterns.most_common(5)),
                    "error_rate_percent": round((failed_executions / total_executions * 100), 2) if total_executions > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {e}")
            return {"error": str(e)}
    
    def get_supported_metrics(self) -> List[MetricType]:
        """Get supported metric types"""
        return [
            MetricType.EXECUTION_TIME,
            MetricType.SUCCESS_RATE,
            MetricType.RESOURCE_UTILIZATION
        ]

class PatientEngagementEngine(AnalyticsEngine):
    """Analytics engine for patient engagement metrics"""
    
    async def calculate_metrics(self, patient_profiles: List[PatientEngagementProfile]) -> Dict[str, Any]:
        """Calculate patient engagement metrics"""
        try:
            if not patient_profiles:
                return {}
            
            # Response rate metrics
            response_rates = [p.response_rate for p in patient_profiles if p.response_rate > 0]
            avg_response_rate = statistics.mean(response_rates) if response_rates else 0
            
            # Response time metrics
            response_times = [p.average_response_time_hours for p in patient_profiles if p.average_response_time_hours > 0]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Engagement score metrics
            engagement_scores = [p.engagement_score for p in patient_profiles if p.engagement_score > 0]
            avg_engagement_score = statistics.mean(engagement_scores) if engagement_scores else 0
            
            # Language preference analysis
            language_preferences = Counter()
            for profile in patient_profiles:
                language_preferences[profile.preferred_language.value] += 1
            
            # Channel preference analysis
            channel_preferences = Counter()
            for profile in patient_profiles:
                for channel in profile.preferred_channels:
                    channel_preferences[channel.value] += 1
            
            # Satisfaction analysis
            all_satisfaction_scores = []
            for profile in patient_profiles:
                all_satisfaction_scores.extend(profile.satisfaction_scores)
            
            avg_satisfaction = statistics.mean(all_satisfaction_scores) if all_satisfaction_scores else 0
            
            return {
                "engagement_metrics": {
                    "total_patients": len(patient_profiles),
                    "average_response_rate_percent": round(avg_response_rate, 2),
                    "average_response_time_hours": round(avg_response_time, 2),
                    "average_engagement_score": round(avg_engagement_score, 2),
                    "average_satisfaction_score": round(avg_satisfaction, 2)
                },
                "language_distribution": dict(language_preferences),
                "channel_preferences": dict(channel_preferences.most_common()),
                "engagement_segments": {
                    "high_engagement": len([p for p in patient_profiles if p.engagement_score >= 80]),
                    "medium_engagement": len([p for p in patient_profiles if 50 <= p.engagement_score < 80]),
                    "low_engagement": len([p for p in patient_profiles if p.engagement_score < 50])
                }
            }
            
        except Exception as e:
            logger.error(f"Patient engagement metrics calculation failed: {e}")
            return {"error": str(e)}
    
    def get_supported_metrics(self) -> List[MetricType]:
        """Get supported metric types"""
        return [
            MetricType.PATIENT_ENGAGEMENT,
            MetricType.COMMUNICATION_EFFECTIVENESS
        ]

class CulturalAnalyticsEngine(AnalyticsEngine):
    """Analytics engine for cultural context and Arabic language metrics"""
    
    async def calculate_metrics(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """Calculate cultural analytics metrics"""
        try:
            if not executions:
                return {}
            
            # Language distribution
            arabic_executions = 0
            english_executions = 0
            
            for execution in executions:
                patient_language = execution.context.patient_data.preferred_language
                if patient_language == Language.ARABIC:
                    arabic_executions += 1
                else:
                    english_executions += 1
            
            total_executions = len(executions)
            arabic_percentage = (arabic_executions / total_executions * 100) if total_executions > 0 else 0
            english_percentage = (english_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Prayer time considerations
            prayer_time_delays = 0
            cultural_adaptations = 0
            
            for execution in executions:
                cultural_context = execution.context.cultural_context
                if cultural_context.get("prayer_time_delays"):
                    prayer_time_delays += len(cultural_context["prayer_time_delays"])
                
                if cultural_context.get("cultural_adaptations_applied"):
                    cultural_adaptations += cultural_context["cultural_adaptations_applied"]
            
            # Ramadan period analysis
            ramadan_executions = 0
            for execution in executions:
                if execution.context.cultural_context.get("ramadan_period"):
                    ramadan_executions += 1
            
            # Family involvement analysis
            family_communications = 0
            for execution in executions:
                if execution.context.cultural_context.get("family_involvement"):
                    family_communications += 1
            
            return {
                "cultural_metrics": {
                    "arabic_communication_percentage": round(arabic_percentage, 2),
                    "english_communication_percentage": round(english_percentage, 2),
                    "prayer_time_delays_total": prayer_time_delays,
                    "cultural_adaptations_applied": cultural_adaptations,
                    "ramadan_period_executions": ramadan_executions,
                    "family_involvement_communications": family_communications
                },
                "cultural_effectiveness": {
                    "arabic_success_rate": self._calculate_language_success_rate(executions, Language.ARABIC),
                    "english_success_rate": self._calculate_language_success_rate(executions, Language.ENGLISH),
                    "cultural_adaptation_impact": self._calculate_cultural_adaptation_impact(executions)
                }
            }
            
        except Exception as e:
            logger.error(f"Cultural analytics calculation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_language_success_rate(self, executions: List[WorkflowExecution], language: Language) -> float:
        """Calculate success rate for specific language"""
        language_executions = [
            e for e in executions 
            if e.context.patient_data.preferred_language == language
        ]
        
        if not language_executions:
            return 0.0
        
        successful = len([e for e in language_executions if e.state == WorkflowState.COMPLETED])
        return (successful / len(language_executions) * 100)
    
    def _calculate_cultural_adaptation_impact(self, executions: List[WorkflowExecution]) -> Dict[str, float]:
        """Calculate impact of cultural adaptations on success rate"""
        with_adaptations = [
            e for e in executions 
            if e.context.cultural_context.get("cultural_adaptations_applied", 0) > 0
        ]
        
        without_adaptations = [
            e for e in executions 
            if e.context.cultural_context.get("cultural_adaptations_applied", 0) == 0
        ]
        
        with_success_rate = 0.0
        if with_adaptations:
            successful_with = len([e for e in with_adaptations if e.state == WorkflowState.COMPLETED])
            with_success_rate = (successful_with / len(with_adaptations) * 100)
        
        without_success_rate = 0.0
        if without_adaptations:
            successful_without = len([e for e in without_adaptations if e.state == WorkflowState.COMPLETED])
            without_success_rate = (successful_without / len(without_adaptations) * 100)
        
        return {
            "with_cultural_adaptations": round(with_success_rate, 2),
            "without_cultural_adaptations": round(without_success_rate, 2),
            "improvement_percentage": round(with_success_rate - without_success_rate, 2)
        }
    
    def get_supported_metrics(self) -> List[MetricType]:
        """Get supported metric types"""
        return [
            MetricType.COMMUNICATION_EFFECTIVENESS,
            MetricType.PATIENT_ENGAGEMENT
        ]

class ComplianceAnalyticsEngine(AnalyticsEngine):
    """Analytics engine for compliance monitoring and reporting"""
    
    async def calculate_metrics(self, audit_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate compliance metrics"""
        try:
            if not audit_events:
                return {}
            
            # HIPAA compliance analysis
            hipaa_violations = 0
            phi_exposures = 0
            
            for event in audit_events:
                if event.get("hipaa_violation"):
                    hipaa_violations += 1
                if event.get("phi_exposure"):
                    phi_exposures += 1
            
            total_events = len(audit_events)
            hipaa_compliance_rate = ((total_events - hipaa_violations) / total_events * 100) if total_events > 0 else 100
            
            # NPHIES compliance analysis
            nphies_errors = 0
            for event in audit_events:
                if event.get("nphies_error"):
                    nphies_errors += 1
            
            nphies_compliance_rate = ((total_events - nphies_errors) / total_events * 100) if total_events > 0 else 100
            
            # Audit trail completeness
            complete_audit_trails = 0
            for event in audit_events:
                if self._is_complete_audit_trail(event):
                    complete_audit_trails += 1
            
            audit_completeness_rate = (complete_audit_trails / total_events * 100) if total_events > 0 else 100
            
            # Data retention compliance
            retention_violations = 0
            for event in audit_events:
                if self._check_retention_violation(event):
                    retention_violations += 1
            
            return {
                "compliance_metrics": {
                    "hipaa_compliance_rate_percent": round(hipaa_compliance_rate, 2),
                    "nphies_compliance_rate_percent": round(nphies_compliance_rate, 2),
                    "audit_completeness_rate_percent": round(audit_completeness_rate, 2),
                    "total_audit_events": total_events,
                    "hipaa_violations": hipaa_violations,
                    "nphies_errors": nphies_errors,
                    "retention_violations": retention_violations
                },
                "compliance_score": {
                    "overall_score": round((hipaa_compliance_rate + nphies_compliance_rate + audit_completeness_rate) / 3, 2),
                    "risk_level": self._calculate_risk_level(hipaa_violations, nphies_errors, retention_violations)
                }
            }
            
        except Exception as e:
            logger.error(f"Compliance metrics calculation failed: {e}")
            return {"error": str(e)}
    
    def _is_complete_audit_trail(self, event: Dict[str, Any]) -> bool:
        """Check if audit trail is complete"""
        required_fields = ["timestamp", "user_id", "action", "patient_id", "data_accessed"]
        return all(field in event for field in required_fields)
    
    def _check_retention_violation(self, event: Dict[str, Any]) -> bool:
        """Check for data retention policy violations"""
        # This would implement retention policy checking
        return False  # Placeholder
    
    def _calculate_risk_level(self, hipaa_violations: int, nphies_errors: int, retention_violations: int) -> str:
        """Calculate overall compliance risk level"""
        total_violations = hipaa_violations + nphies_errors + retention_violations
        
        if total_violations == 0:
            return "low"
        elif total_violations <= 5:
            return "medium"
        elif total_violations <= 15:
            return "high"
        else:
            return "critical"
    
    def get_supported_metrics(self) -> List[MetricType]:
        """Get supported metric types"""
        return [
            MetricType.COMPLIANCE_SCORE
        ]

# ==================== MAIN MONITORING SYSTEM ====================

class HealthcareWorkflowMonitor:
    """
    Comprehensive healthcare workflow monitoring and analytics system
    
    Provides real-time monitoring, performance analytics, and compliance reporting
    for healthcare communication workflows with Saudi Arabian context
    """
    
    def __init__(self, 
                 workflow_engine: PyHeartHealthcareWorkflowEngine,
                 trigger_manager: HealthcareWorkflowTriggerManager,
                 healthcare_integrator: HealthcareSystemIntegrator):
        """
        Initialize the workflow monitor
        
        Args:
            workflow_engine: PyHeart workflow engine instance
            trigger_manager: Workflow trigger manager
            healthcare_integrator: Healthcare system integrator
        """
        self.workflow_engine = workflow_engine
        self.trigger_manager = trigger_manager
        self.healthcare_integrator = healthcare_integrator
        
        # Analytics engines
        self.analytics_engines = {
            "performance": WorkflowPerformanceEngine(),
            "engagement": PatientEngagementEngine(),
            "cultural": CulturalAnalyticsEngine(),
            "compliance": ComplianceAnalyticsEngine()
        }
        
        # Monitoring data
        self.metrics_history: List[WorkflowMetric] = []
        self.performance_alerts: List[PerformanceAlert] = []
        self.patient_profiles: Dict[str, PatientEngagementProfile] = {}
        
        # Configuration
        self.config = {
            "metrics_retention_days": 365,
            "alert_thresholds": {
                "success_rate_minimum": 85.0,
                "response_time_maximum": 300.0,  # 5 minutes
                "engagement_score_minimum": 60.0
            },
            "real_time_monitoring_enabled": True,
            "automated_reporting_enabled": True,
            "ml_optimization_enabled": True
        }
        
        logger.info("Healthcare Workflow Monitor initialized")
    
    # ==================== REAL-TIME MONITORING ====================
    
    async def start_real_time_monitoring(self):
        """Start real-time workflow monitoring"""
        try:
            if not self.config["real_time_monitoring_enabled"]:
                return
            
            # Start monitoring tasks
            monitoring_tasks = [
                self._monitor_workflow_executions(),
                self._monitor_performance_alerts(),
                self._update_patient_engagement_profiles(),
                self._generate_automated_reports()
            ]
            
            await asyncio.gather(*monitoring_tasks)
            
        except Exception as e:
            logger.error(f"Real-time monitoring failed: {e}")
    
    async def _monitor_workflow_executions(self):
        """Monitor active workflow executions"""
        while True:
            try:
                # Get active workflows
                active_workflows = await self.workflow_engine.get_active_workflows()
                
                # Check for performance issues
                for workflow_status in active_workflows:
                    await self._check_workflow_performance(workflow_status)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Workflow execution monitoring failed: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_workflow_performance(self, workflow_status: Dict[str, Any]):
        """Check individual workflow performance"""
        try:
            execution_id = workflow_status.get("execution_id")
            duration_seconds = workflow_status.get("duration_seconds", 0)
            
            # Check for long-running workflows
            if duration_seconds > 3600:  # 1 hour
                await self._create_performance_alert(
                    AlertSeverity.WARNING,
                    "Long-running workflow detected",
                    f"Workflow {execution_id} has been running for {duration_seconds/3600:.1f} hours",
                    execution_id=execution_id
                )
            
            # Check for stuck workflows
            if workflow_status.get("state") == "running" and duration_seconds > 7200:  # 2 hours
                await self._create_performance_alert(
                    AlertSeverity.ERROR,
                    "Stuck workflow detected",
                    f"Workflow {execution_id} appears to be stuck (running for {duration_seconds/3600:.1f} hours)",
                    execution_id=execution_id
                )
            
        except Exception as e:
            logger.error(f"Workflow performance check failed: {e}")
    
    async def _monitor_performance_alerts(self):
        """Monitor and process performance alerts"""
        while True:
            try:
                # Process unacknowledged alerts
                unacknowledged_alerts = [a for a in self.performance_alerts if not a.acknowledged]
                
                for alert in unacknowledged_alerts:
                    await self._process_performance_alert(alert)
                
                # Clean up old resolved alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance alert monitoring failed: {e}")
                await asyncio.sleep(300)
    
    async def _create_performance_alert(self, 
                                      severity: AlertSeverity, 
                                      title: str, 
                                      description: str,
                                      workflow_id: Optional[str] = None,
                                      execution_id: Optional[str] = None):
        """Create a new performance alert"""
        try:
            alert = PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                severity=severity,
                title=title,
                description=description,
                workflow_id=workflow_id,
                execution_id=execution_id
            )
            
            self.performance_alerts.append(alert)
            
            # Log critical alerts immediately
            if severity == AlertSeverity.CRITICAL:
                logger.critical(f"CRITICAL ALERT: {title} - {description}")
            
            # Send notifications for high-severity alerts
            if severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR]:
                await self._send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"Failed to create performance alert: {e}")
    
    async def _process_performance_alert(self, alert: PerformanceAlert):
        """Process a performance alert"""
        try:
            # Auto-acknowledge info alerts after 1 hour
            if alert.severity == AlertSeverity.INFO:
                if (datetime.now() - alert.triggered_at).total_seconds() > 3600:
                    alert.acknowledged = True
            
            # Auto-resolve warning alerts if conditions improve
            if alert.severity == AlertSeverity.WARNING and alert.execution_id:
                workflow_status = await self.workflow_engine.get_workflow_execution_status(alert.execution_id)
                if workflow_status.get("state") in ["completed", "failed", "cancelled"]:
                    alert.resolved = True
            
        except Exception as e:
            logger.error(f"Alert processing failed: {e}")
    
    async def _send_alert_notification(self, alert: PerformanceAlert):
        """Send notification for high-severity alert"""
        try:
            # This would integrate with notification systems
            notification_data = {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "timestamp": alert.triggered_at.isoformat()
            }
            
            # Log for now (would send to notification service)
            logger.warning(f"ALERT NOTIFICATION: {json.dumps(notification_data)}")
            
        except Exception as e:
            logger.error(f"Alert notification failed: {e}")
    
    # ==================== ANALYTICS AND REPORTING ====================
    
    async def generate_workflow_analytics(self, 
                                        workflow_id: Optional[str] = None,
                                        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> WorkflowAnalytics:
        """Generate comprehensive workflow analytics"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            
            if not start_date:
                if timeframe == AnalyticsTimeframe.DAILY:
                    start_date = end_date - timedelta(days=1)
                elif timeframe == AnalyticsTimeframe.WEEKLY:
                    start_date = end_date - timedelta(weeks=1)
                elif timeframe == AnalyticsTimeframe.MONTHLY:
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(days=1)
            
            # Get workflow executions for analysis
            executions = await self._get_workflow_executions(workflow_id, start_date, end_date)
            
            if not executions:
                return WorkflowAnalytics(
                    workflow_id=workflow_id or "all",
                    workflow_type=HealthcareWorkflowType.PATIENT_ONBOARDING,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Run analytics engines
            performance_metrics = await self.analytics_engines["performance"].calculate_metrics(executions)
            cultural_metrics = await self.analytics_engines["cultural"].calculate_metrics(executions)
            
            # Get patient engagement data
            patient_profiles = []
            for execution in executions:
                if execution.context.patient_id in self.patient_profiles:
                    patient_profiles.append(self.patient_profiles[execution.context.patient_id])
            
            engagement_metrics = await self.analytics_engines["engagement"].calculate_metrics(patient_profiles)
            
            # Build analytics object
            analytics = WorkflowAnalytics(
                workflow_id=workflow_id or "all",
                workflow_type=executions[0].workflow_definition.workflow_type if executions else HealthcareWorkflowType.PATIENT_ONBOARDING,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            # Populate execution metrics
            exec_metrics = performance_metrics.get("execution_metrics", {})
            analytics.total_executions = exec_metrics.get("total_executions", 0)
            analytics.successful_executions = exec_metrics.get("successful_executions", 0)
            analytics.failed_executions = exec_metrics.get("failed_executions", 0)
            analytics.average_execution_time_seconds = exec_metrics.get("average_execution_time_seconds", 0.0)
            analytics.median_execution_time_seconds = exec_metrics.get("median_execution_time_seconds", 0.0)
            
            # Populate engagement metrics
            engage_metrics = engagement_metrics.get("engagement_metrics", {})
            analytics.patient_response_rate = engage_metrics.get("average_response_rate_percent", 0.0)
            analytics.average_response_time_minutes = engage_metrics.get("average_response_time_hours", 0.0) * 60
            analytics.communication_satisfaction_score = engage_metrics.get("average_satisfaction_score", 0.0)
            analytics.preferred_communication_channels = engagement_metrics.get("channel_preferences", {})
            
            # Populate cultural metrics
            cultural_data = cultural_metrics.get("cultural_metrics", {})
            analytics.arabic_communication_percentage = cultural_data.get("arabic_communication_percentage", 0.0)
            analytics.english_communication_percentage = cultural_data.get("english_communication_percentage", 0.0)
            analytics.prayer_time_delays = cultural_data.get("prayer_time_delays_total", 0)
            analytics.cultural_adaptations_applied = cultural_data.get("cultural_adaptations_applied", 0)
            
            # Calculate derived metrics
            analytics = await self._calculate_derived_metrics(analytics, executions)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Workflow analytics generation failed: {e}")
            # Return empty analytics object
            return WorkflowAnalytics(
                workflow_id=workflow_id or "all",
                workflow_type=HealthcareWorkflowType.PATIENT_ONBOARDING,
                timeframe=timeframe,
                start_date=start_date or datetime.now(),
                end_date=end_date or datetime.now()
            )
    
    async def _get_workflow_executions(self, 
                                     workflow_id: Optional[str],
                                     start_date: datetime,
                                     end_date: datetime) -> List[WorkflowExecution]:
        """Get workflow executions for analysis"""
        try:
            # Get all active executions from workflow engine
            all_executions = list(self.workflow_engine.active_executions.values())
            
            # Filter by date range
            filtered_executions = []
            for execution in all_executions:
                if execution.started_at and start_date <= execution.started_at <= end_date:
                    if not workflow_id or execution.workflow_definition.workflow_id == workflow_id:
                        filtered_executions.append(execution)
            
            return filtered_executions
            
        except Exception as e:
            logger.error(f"Failed to get workflow executions: {e}")
            return []
    
    async def _calculate_derived_metrics(self, analytics: WorkflowAnalytics, executions: List[WorkflowExecution]) -> WorkflowAnalytics:
        """Calculate derived metrics from base analytics"""
        try:
            # Clinical adherence rate (placeholder - would integrate with clinical systems)
            analytics.clinical_adherence_rate = 85.0
            
            # Appointment show rate (placeholder)
            analytics.appointment_show_rate = 90.0
            
            # Medication adherence rate (placeholder)
            analytics.medication_adherence_rate = 80.0
            
            # Patient satisfaction score (calculated from engagement)
            analytics.patient_satisfaction_score = analytics.communication_satisfaction_score
            
            # Cost per communication (placeholder)
            analytics.cost_per_communication = 0.50  # $0.50 per communication
            
            # Resource utilization rate
            total_execution_time = sum(
                (e.completed_at - e.started_at).total_seconds() 
                for e in executions 
                if e.completed_at and e.started_at
            )
            available_time = (analytics.end_date - analytics.start_date).total_seconds()
            analytics.resource_utilization_rate = (total_execution_time / available_time * 100) if available_time > 0 else 0
            
            # Automation rate (percentage of fully automated workflows)
            automated_workflows = len([e for e in executions if e.escalation_count == 0])
            analytics.automation_rate = (automated_workflows / len(executions) * 100) if executions else 0
            
            return analytics
            
        except Exception as e:
            logger.error(f"Derived metrics calculation failed: {e}")
            return analytics
    
    async def generate_compliance_report(self, 
                                       start_date: datetime,
                                       end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            # Get audit events from healthcare integrator
            audit_events = await self._get_audit_events(start_date, end_date)
            
            # Calculate compliance metrics
            compliance_metrics = await self.analytics_engines["compliance"].calculate_metrics(audit_events)
            
            # Get workflow analytics for compliance context
            workflow_analytics = await self.generate_workflow_analytics(
                timeframe=AnalyticsTimeframe.MONTHLY,
                start_date=start_date,
                end_date=end_date
            )
            
            # Build comprehensive compliance report
            report = {
                "report_metadata": {
                    "report_type": ReportType.COMPLIANCE_AUDIT.value,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "generated_at": datetime.now().isoformat(),
                    "report_id": str(uuid.uuid4())
                },
                "compliance_summary": compliance_metrics.get("compliance_metrics", {}),
                "risk_assessment": compliance_metrics.get("compliance_score", {}),
                "workflow_compliance": {
                    "total_workflows_analyzed": workflow_analytics.total_executions,
                    "hipaa_compliant_workflows": workflow_analytics.total_executions - compliance_metrics.get("compliance_metrics", {}).get("hipaa_violations", 0),
                    "nphies_compliant_workflows": workflow_analytics.total_executions - compliance_metrics.get("compliance_metrics", {}).get("nphies_errors", 0)
                },
                "recommendations": await self._generate_compliance_recommendations(compliance_metrics),
                "action_items": await self._generate_compliance_action_items(compliance_metrics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return {"error": str(e)}
    
    async def _get_audit_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get audit events for compliance analysis"""
        try:
            # This would integrate with the audit logging system
            # For now, return placeholder data
            return []
            
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    async def _generate_compliance_recommendations(self, compliance_metrics: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        compliance_data = compliance_metrics.get("compliance_metrics", {})
        
        # HIPAA recommendations
        hipaa_rate = compliance_data.get("hipaa_compliance_rate_percent", 100)
        if hipaa_rate < 95:
            recommendations.append("Implement additional HIPAA training for staff handling patient communications")
            recommendations.append("Review and strengthen PHI protection protocols in workflow systems")
        
        # NPHIES recommendations
        nphies_rate = compliance_data.get("nphies_compliance_rate_percent", 100)
        if nphies_rate < 98:
            recommendations.append("Enhance NPHIES integration testing and validation procedures")
            recommendations.append("Implement automated NPHIES compliance checking in workflows")
        
        # Audit recommendations
        audit_rate = compliance_data.get("audit_completeness_rate_percent", 100)
        if audit_rate < 99:
            recommendations.append("Implement comprehensive audit trail logging for all patient communications")
            recommendations.append("Regular audit trail completeness verification procedures")
        
        return recommendations
    
    async def _generate_compliance_action_items(self, compliance_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific compliance action items"""
        action_items = []
        
        compliance_data = compliance_metrics.get("compliance_metrics", {})
        risk_level = compliance_metrics.get("compliance_score", {}).get("risk_level", "low")
        
        if risk_level in ["high", "critical"]:
            action_items.append({
                "priority": "critical",
                "action": "Immediate compliance audit and remediation",
                "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                "responsible_team": "compliance_team"
            })
        
        if compliance_data.get("hipaa_violations", 0) > 0:
            action_items.append({
                "priority": "high",
                "action": "Investigate and remediate HIPAA violations",
                "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
                "responsible_team": "privacy_team"
            })
        
        return action_items
    
    # ==================== UTILITY METHODS ====================
    
    async def _update_patient_engagement_profiles(self):
        """Update patient engagement profiles"""
        while True:
            try:
                # Get recent workflow executions
                recent_executions = await self._get_workflow_executions(
                    workflow_id=None,
                    start_date=datetime.now() - timedelta(hours=1),
                    end_date=datetime.now()
                )
                
                # Update patient profiles based on recent activity
                for execution in recent_executions:
                    patient_id = execution.context.patient_id
                    
                    if patient_id not in self.patient_profiles:
                        self.patient_profiles[patient_id] = PatientEngagementProfile(
                            patient_id=patient_id,
                            preferred_language=execution.context.patient_data.preferred_language,
                            preferred_channels=execution.context.patient_data.preferred_channels
                        )
                    
                    # Update profile metrics
                    profile = self.patient_profiles[patient_id]
                    profile.total_communications_received += len(execution.step_history)
                    profile.last_engagement = datetime.now()
                    
                    # Update engagement score
                    profile.engagement_score = await self._calculate_engagement_score(profile, execution)
                
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Patient engagement profile update failed: {e}")
                await asyncio.sleep(3600)
    
    async def _calculate_engagement_score(self, profile: PatientEngagementProfile, execution: WorkflowExecution) -> float:
        """Calculate patient engagement score"""
        try:
            # Base score components
            response_score = min(profile.response_rate, 100) * 0.3
            completion_score = profile.workflow_completion_rate * 0.3
            satisfaction_score = (sum(profile.satisfaction_scores) / len(profile.satisfaction_scores)) if profile.satisfaction_scores else 50
            satisfaction_component = satisfaction_score * 0.4
            
            total_score = response_score + completion_score + satisfaction_component
            return min(total_score, 100.0)
            
        except Exception as e:
            logger.error(f"Engagement score calculation failed: {e}")
            return 50.0  # Default neutral score
    
    async def _generate_automated_reports(self):
        """Generate automated periodic reports"""
        while True:
            try:
                if not self.config["automated_reporting_enabled"]:
                    await asyncio.sleep(3600)
                    continue
                
                current_time = datetime.now()
                
                # Daily reports at 6 AM
                if current_time.hour == 6 and current_time.minute < 5:
                    await self._generate_daily_report()
                
                # Weekly reports on Sunday at 7 AM
                if current_time.weekday() == 6 and current_time.hour == 7 and current_time.minute < 5:
                    await self._generate_weekly_report()
                
                # Monthly reports on 1st at 8 AM
                if current_time.day == 1 and current_time.hour == 8 and current_time.minute < 5:
                    await self._generate_monthly_report()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Automated report generation failed: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_daily_report(self):
        """Generate daily performance report"""
        try:
            analytics = await self.generate_workflow_analytics(timeframe=AnalyticsTimeframe.DAILY)
            
            report_data = {
                "report_type": "daily_performance",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "analytics": analytics.dict(),
                "alerts_generated": len([a for a in self.performance_alerts if a.triggered_at.date() == datetime.now().date()])
            }
            
            logger.info(f"Daily report generated: {json.dumps(report_data, default=str)}")
            
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
    
    async def _generate_weekly_report(self):
        """Generate weekly performance report"""
        try:
            analytics = await self.generate_workflow_analytics(timeframe=AnalyticsTimeframe.WEEKLY)
            
            report_data = {
                "report_type": "weekly_performance",
                "week_ending": datetime.now().strftime("%Y-%m-%d"),
                "analytics": analytics.dict(),
                "trends": await self._calculate_weekly_trends()
            }
            
            logger.info(f"Weekly report generated: {json.dumps(report_data, default=str)}")
            
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
    
    async def _generate_monthly_report(self):
        """Generate monthly performance report"""
        try:
            analytics = await self.generate_workflow_analytics(timeframe=AnalyticsTimeframe.MONTHLY)
            
            # Generate compliance report for the month
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            compliance_report = await self.generate_compliance_report(start_of_month, datetime.now())
            
            report_data = {
                "report_type": "monthly_performance",
                "month": datetime.now().strftime("%Y-%m"),
                "analytics": analytics.dict(),
                "compliance": compliance_report,
                "optimization_recommendations": await self._generate_optimization_recommendations(analytics)
            }
            
            logger.info(f"Monthly report generated: {json.dumps(report_data, default=str)}")
            
        except Exception as e:
            logger.error(f"Monthly report generation failed: {e}")
    
    async def _calculate_weekly_trends(self) -> Dict[str, Any]:
        """Calculate weekly performance trends"""
        try:
            # This would compare current week to previous week
            # For now, return placeholder trends
            return {
                "success_rate_trend": "increasing",
                "response_time_trend": "improving",
                "engagement_trend": "stable"
            }
            
        except Exception as e:
            logger.error(f"Weekly trends calculation failed: {e}")
            return {}
    
    async def _generate_optimization_recommendations(self, analytics: WorkflowAnalytics) -> List[str]:
        """Generate workflow optimization recommendations"""
        recommendations = []
        
        # Success rate optimization
        if analytics.successful_executions / analytics.total_executions < 0.9:
            recommendations.append("Review failed workflow patterns and implement error handling improvements")
        
        # Response time optimization
        if analytics.average_response_time_minutes > 60:
            recommendations.append("Implement automated reminder escalation to improve patient response times")
        
        # Engagement optimization
        if analytics.communication_satisfaction_score < 80:
            recommendations.append("Review communication templates and personalization strategies")
        
        # Cultural optimization
        if analytics.prayer_time_delays > 0:
            recommendations.append("Optimize timing algorithms to better respect prayer times")
        
        return recommendations
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Remove old resolved alerts
            self.performance_alerts = [
                alert for alert in self.performance_alerts
                if not (alert.resolved and alert.triggered_at < cutoff_date)
            ]
            
        except Exception as e:
            logger.error(f"Alert cleanup failed: {e}")

# Export main class
__all__ = ["HealthcareWorkflowMonitor", "WorkflowAnalytics", "PatientEngagementProfile", "PerformanceAlert"]