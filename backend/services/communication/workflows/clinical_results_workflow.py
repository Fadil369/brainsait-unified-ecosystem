"""
BrainSAIT Healthcare Platform - Clinical Results Communication Workflow
Comprehensive clinical results communication including lab results, imaging reports, critical alerts, and referrals

This workflow handles:
1. Lab results notifications with severity-based prioritization
2. Critical result alerts with immediate provider notification
3. Imaging reports and follow-up recommendations
4. Pathology results with care coordination
5. Referral notifications and specialist coordination
6. Abnormal results with patient education and next steps
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from ..patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData, ClinicalResultData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)

logger = logging.getLogger(__name__)

class ResultSeverity(str, Enum):
    """Clinical result severity levels"""
    NORMAL = "normal"
    SLIGHTLY_ABNORMAL = "slightly_abnormal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"
    PANIC_VALUE = "panic_value"

class ResultType(str, Enum):
    """Types of clinical results"""
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PATHOLOGY = "pathology"
    CARDIOLOGY = "cardiology"
    GENETICS = "genetics"
    MICROBIOLOGY = "microbiology"

class NotificationUrgency(str, Enum):
    """Notification urgency levels"""
    IMMEDIATE = "immediate"  # Within 15 minutes
    URGENT = "urgent"       # Within 2 hours
    ROUTINE = "routine"     # Within 24 hours
    SCHEDULED = "scheduled" # At next appointment

@dataclass
class ClinicalResult:
    """Enhanced clinical result data"""
    result_id: str
    patient_id: str
    provider_id: str
    result_type: ResultType
    test_name: str
    test_name_ar: Optional[str] = None
    result_value: Optional[str] = None
    reference_range: Optional[str] = None
    severity: ResultSeverity = ResultSeverity.NORMAL
    urgency: NotificationUrgency = NotificationUrgency.ROUTINE
    abnormal_flags: List[str] = None
    interpretation: Optional[str] = None
    interpretation_ar: Optional[str] = None
    provider_notes: Optional[str] = None
    provider_notes_ar: Optional[str] = None
    follow_up_required: bool = False
    follow_up_timeframe: Optional[str] = None
    result_date: datetime = None
    reviewed_by_provider: bool = False
    patient_notified: bool = False

@dataclass
class ProviderNotificationData:
    """Provider notification information"""
    provider_id: str
    name: str
    name_ar: Optional[str] = None
    phone_number: str
    email: Optional[str] = None
    department: Optional[str] = None
    preferred_language: Language = Language.ENGLISH
    notification_preferences: List[CommunicationChannel] = None
    escalation_contact: Optional[str] = None

@dataclass
class ReferralData:
    """Referral information"""
    referral_id: str
    referring_provider_id: str
    specialist_provider_id: str
    specialist_name: str
    specialist_name_ar: Optional[str] = None
    specialty: str
    specialty_ar: Optional[str] = None
    urgency: NotificationUrgency = NotificationUrgency.ROUTINE
    reason: str
    reason_ar: Optional[str] = None
    appointment_required: bool = True
    contact_info: Optional[str] = None

@dataclass
class ClinicalWorkflowConfig:
    """Configuration for clinical results workflow"""
    critical_notification_minutes: int = 15  # Notify critical results within 15 minutes
    urgent_notification_hours: int = 2  # Notify urgent results within 2 hours
    routine_notification_hours: int = 24  # Notify routine results within 24 hours
    provider_escalation_minutes: int = 30  # Escalate to supervisor if no provider response
    max_notification_attempts: int = 5
    patient_education_delay_hours: int = 2  # Send education materials 2 hours after notification

class ClinicalResultsWorkflow:
    """
    Clinical Results Communication Workflow Implementation
    
    Manages communication of all clinical results with appropriate urgency and follow-up
    """
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
        self.config = ClinicalWorkflowConfig()
        self.active_workflows: Dict[str, Dict] = {}
        self.provider_notifications: Dict[str, List] = {}
        
    async def initiate_clinical_results_workflow(self, 
                                               patient_data: PatientCommunicationData,
                                               clinical_result: ClinicalResult,
                                               provider_data: ProviderNotificationData) -> Dict[str, Any]:
        """
        Initiate clinical results workflow based on result severity and type
        
        Args:
            patient_data: Patient communication information
            clinical_result: Clinical result details
            provider_data: Provider notification information
            
        Returns:
            Workflow initiation result with notification plan
        """
        try:
            workflow_id = f"clinical_{clinical_result.result_id}"
            
            # Determine notification timeline based on severity
            notification_schedule = self._calculate_notification_schedule(clinical_result)
            
            # Store workflow state
            workflow_state = {
                "workflow_id": workflow_id,
                "patient_data": patient_data,
                "clinical_result": clinical_result,
                "provider_data": provider_data,
                "notification_schedule": notification_schedule,
                "status": "initiated",
                "notifications_sent": [],
                "escalations": [],
                "created_at": datetime.now()
            }
            
            self.active_workflows[workflow_id] = workflow_state
            
            # Immediate actions based on severity
            immediate_actions = []
            
            # Critical/Panic results require immediate provider notification
            if clinical_result.severity in [ResultSeverity.CRITICAL, ResultSeverity.PANIC_VALUE]:
                provider_notification = await self.send_critical_result_alert(
                    provider_data, patient_data, clinical_result, workflow_id
                )
                immediate_actions.append(provider_notification)
                
                # Also send immediate patient notification for critical results
                patient_notification = await self.send_critical_patient_alert(
                    patient_data, clinical_result, provider_data, workflow_id
                )
                immediate_actions.append(patient_notification)
                
            elif clinical_result.severity == ResultSeverity.ABNORMAL:
                # Abnormal results notify provider first
                provider_notification = await self.notify_provider_of_result(
                    provider_data, patient_data, clinical_result, workflow_id
                )
                immediate_actions.append(provider_notification)
                
            else:
                # Normal/slightly abnormal results go directly to patient
                patient_notification = await self.send_routine_result_notification(
                    patient_data, clinical_result, provider_data, workflow_id
                )
                immediate_actions.append(patient_notification)
            
            # Schedule follow-up actions
            scheduled_tasks = await self._schedule_workflow_tasks(
                workflow_id, notification_schedule
            )
            
            logger.info(f"Clinical results workflow initiated for result {clinical_result.result_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "initiated",
                "severity": clinical_result.severity.value,
                "urgency": clinical_result.urgency.value,
                "immediate_actions": immediate_actions,
                "scheduled_tasks": scheduled_tasks,
                "notification_schedule": {k: v.isoformat() if isinstance(v, datetime) else v for k, v in notification_schedule.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate clinical results workflow: {e}")
            raise

    def _calculate_notification_schedule(self, clinical_result: ClinicalResult) -> Dict[str, Any]:
        """Calculate notification timeline based on result severity and type"""
        now = datetime.now()
        schedule = {}
        
        if clinical_result.severity in [ResultSeverity.CRITICAL, ResultSeverity.PANIC_VALUE]:
            schedule["provider_notification"] = now
            schedule["patient_notification"] = now
            schedule["escalation_check"] = now + timedelta(minutes=self.config.provider_escalation_minutes)
            schedule["follow_up_reminder"] = now + timedelta(hours=2)
            
        elif clinical_result.severity == ResultSeverity.ABNORMAL:
            schedule["provider_notification"] = now
            schedule["patient_notification"] = now + timedelta(hours=2)  # After provider review
            schedule["follow_up_reminder"] = now + timedelta(days=1)
            
        else:  # Normal or slightly abnormal
            schedule["patient_notification"] = now + timedelta(hours=1)
            schedule["education_materials"] = now + timedelta(hours=self.config.patient_education_delay_hours)
        
        return schedule

    async def send_critical_result_alert(self, 
                                       provider_data: ProviderNotificationData,
                                       patient_data: PatientCommunicationData,
                                       clinical_result: ClinicalResult,
                                       workflow_id: str) -> Dict[str, Any]:
        """Send critical result alert to provider"""
        try:
            template = self.communication_service.message_templates["critical_result_alert"]
            
            # Use provider phone as contact for critical alerts
            variables = {
                "provider_name": provider_data.name,
                "patient_name": patient_data.patient_id,
                "provider_phone": provider_data.phone_number
            }
            
            # Critical alerts always use voice first, then SMS
            priority_channels = [CommunicationChannel.VOICE, CommunicationChannel.SMS]
            channel = priority_channels[0] if provider_data.notification_preferences is None else provider_data.notification_preferences[0]
            
            subject, content = self.communication_service.render_message_template(
                template, provider_data.preferred_language, variables
            )
            
            # Add specific result details for provider
            test_name = clinical_result.test_name_ar if provider_data.preferred_language == Language.ARABIC else clinical_result.test_name
            if provider_data.preferred_language == Language.ARABIC:
                content += f"\n\nالفحص: {test_name}"
                if clinical_result.result_value:
                    content += f"\nالنتيجة: {clinical_result.result_value}"
                if clinical_result.interpretation_ar:
                    content += f"\nالتفسير: {clinical_result.interpretation_ar}"
            else:
                content += f"\n\nTest: {test_name}"
                if clinical_result.result_value:
                    content += f"\nResult: {clinical_result.result_value}"
                if clinical_result.interpretation:
                    content += f"\nInterpretation: {clinical_result.interpretation}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=provider_data.provider_id,
                channel=channel,
                language=provider_data.preferred_language,
                priority=MessagePriority.CRITICAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "result_id": clinical_result.result_id,
                    "severity": clinical_result.severity.value,
                    "recipient_type": "provider"
                }
            )
            
            # Create provider communication data
            provider_comm_data = PatientCommunicationData(
                patient_id=provider_data.provider_id,
                phone_number=provider_data.phone_number,
                email=provider_data.email,
                preferred_language=provider_data.preferred_language,
                preferred_channels=provider_data.notification_preferences or [CommunicationChannel.VOICE, CommunicationChannel.SMS]
            )
            
            result = await self.communication_service.send_message(provider_comm_data, message)
            
            # Store notification in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["notifications_sent"].append({
                    "type": "critical_provider_alert",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send critical result alert to provider: {e}")
            raise

    async def send_critical_patient_alert(self, 
                                        patient_data: PatientCommunicationData,
                                        clinical_result: ClinicalResult,
                                        provider_data: ProviderNotificationData,
                                        workflow_id: str) -> Dict[str, Any]:
        """Send critical result alert to patient"""
        try:
            template = self.communication_service.message_templates["critical_result_alert"]
            
            variables = {
                "patient_name": patient_data.patient_id,
                "provider_name": provider_data.name_ar if patient_data.preferred_language == Language.ARABIC else provider_data.name,
                "provider_phone": provider_data.phone_number
            }
            
            # Critical patient alerts prefer voice, then SMS
            channel = self.communication_service.select_communication_channel(
                patient_data, MessagePriority.CRITICAL, [CommunicationChannel.VOICE, CommunicationChannel.SMS]
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=MessagePriority.CRITICAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "result_id": clinical_result.result_id,
                    "severity": clinical_result.severity.value,
                    "recipient_type": "patient"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Mark patient as notified
            clinical_result.patient_notified = True
            
            # Store notification in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["notifications_sent"].append({
                    "type": "critical_patient_alert",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send critical result alert to patient: {e}")
            raise

    async def notify_provider_of_result(self, 
                                      provider_data: ProviderNotificationData,
                                      patient_data: PatientCommunicationData,
                                      clinical_result: ClinicalResult,
                                      workflow_id: str) -> Dict[str, Any]:
        """Notify provider of abnormal result for review"""
        try:
            if provider_data.preferred_language == Language.ARABIC:
                subject = "نتيجة مختبر تحتاج مراجعة - برينسيت للرعاية الصحية"
                content = f"دكتور {provider_data.name}، نتيجة {clinical_result.test_name_ar or clinical_result.test_name} للمريض {patient_data.patient_id} تحتاج مراجعتك."
            else:
                subject = "Lab Result Requires Review - BrainSAIT Healthcare"
                content = f"Dr. {provider_data.name}, {clinical_result.test_name} result for patient {patient_data.patient_id} requires your review."
            
            # Add result details
            if clinical_result.result_value:
                if provider_data.preferred_language == Language.ARABIC:
                    content += f"\n\nالنتيجة: {clinical_result.result_value}"
                    if clinical_result.reference_range:
                        content += f"\nالمدى الطبيعي: {clinical_result.reference_range}"
                else:
                    content += f"\n\nResult: {clinical_result.result_value}"
                    if clinical_result.reference_range:
                        content += f"\nReference Range: {clinical_result.reference_range}"
            
            # Add abnormal flags if present
            if clinical_result.abnormal_flags:
                flags_text = ", ".join(clinical_result.abnormal_flags)
                if provider_data.preferred_language == Language.ARABIC:
                    content += f"\nمؤشرات غير طبيعية: {flags_text}"
                else:
                    content += f"\nAbnormal Flags: {flags_text}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=provider_data.provider_id,
                channel=provider_data.notification_preferences[0] if provider_data.notification_preferences else CommunicationChannel.SMS,
                language=provider_data.preferred_language,
                priority=MessagePriority.HIGH,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "result_id": clinical_result.result_id,
                    "severity": clinical_result.severity.value,
                    "recipient_type": "provider",
                    "action_required": "review"
                }
            )
            
            # Create provider communication data
            provider_comm_data = PatientCommunicationData(
                patient_id=provider_data.provider_id,
                phone_number=provider_data.phone_number,
                email=provider_data.email,
                preferred_language=provider_data.preferred_language,
                preferred_channels=provider_data.notification_preferences or [CommunicationChannel.SMS]
            )
            
            result = await self.communication_service.send_message(provider_comm_data, message)
            
            # Store notification in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["notifications_sent"].append({
                    "type": "provider_review_notification",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to notify provider of result: {e}")
            raise

    async def send_routine_result_notification(self, 
                                             patient_data: PatientCommunicationData,
                                             clinical_result: ClinicalResult,
                                             provider_data: ProviderNotificationData,
                                             workflow_id: str) -> Dict[str, Any]:
        """Send routine result notification to patient"""
        try:
            # Use lab results available template
            template = self.communication_service.message_templates["lab_results_available"]
            
            # Generate patient portal link
            portal_link = f"https://brainsait.com/portal/results/{patient_data.patient_id}/{clinical_result.result_id}"
            test_date = clinical_result.result_date.strftime("%Y-%m-%d") if clinical_result.result_date else datetime.now().strftime("%Y-%m-%d")
            
            variables = {
                "patient_name": patient_data.patient_id,
                "test_date": test_date,
                "portal_link": portal_link
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add test-specific information
            test_name = clinical_result.test_name_ar if patient_data.preferred_language == Language.ARABIC else clinical_result.test_name
            if patient_data.preferred_language == Language.ARABIC:
                content += f"\n\nالفحص: {test_name}"
                if clinical_result.severity == ResultSeverity.NORMAL:
                    content += "\nالنتيجة: طبيعية"
                elif clinical_result.severity == ResultSeverity.SLIGHTLY_ABNORMAL:
                    content += "\nالنتيجة: انحراف طفيف عن الطبيعي"
            else:
                content += f"\n\nTest: {test_name}"
                if clinical_result.severity == ResultSeverity.NORMAL:
                    content += "\nResult: Normal"
                elif clinical_result.severity == ResultSeverity.SLIGHTLY_ABNORMAL:
                    content += "\nResult: Slightly abnormal"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "result_id": clinical_result.result_id,
                    "portal_link": portal_link
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Mark patient as notified
            clinical_result.patient_notified = True
            
            # Store notification in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["notifications_sent"].append({
                    "type": "routine_patient_notification",
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send routine result notification: {e}")
            raise

    async def send_imaging_result_notification(self, 
                                             patient_data: PatientCommunicationData,
                                             clinical_result: ClinicalResult,
                                             provider_data: ProviderNotificationData,
                                             workflow_id: str) -> Dict[str, Any]:
        """Send imaging result notification"""
        try:
            template = self.communication_service.message_templates["imaging_results"]
            
            scan_date = clinical_result.result_date.strftime("%Y-%m-%d") if clinical_result.result_date else datetime.now().strftime("%Y-%m-%d")
            
            variables = {
                "patient_name": patient_data.patient_id,
                "imaging_type": clinical_result.test_name_ar if patient_data.preferred_language == Language.ARABIC else clinical_result.test_name,
                "scan_date": scan_date,
                "provider_name": provider_data.name_ar if patient_data.preferred_language == Language.ARABIC else provider_data.name,
                "clinic_phone": provider_data.phone_number
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add follow-up information if required
            if clinical_result.follow_up_required:
                if patient_data.preferred_language == Language.ARABIC:
                    content += f"\n\nمطلوب متابعة خلال: {clinical_result.follow_up_timeframe or 'حسب توجيهات الطبيب'}"
                else:
                    content += f"\n\nFollow-up required within: {clinical_result.follow_up_timeframe or 'as directed by physician'}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "result_id": clinical_result.result_id,
                    "result_type": "imaging"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Mark patient as notified
            clinical_result.patient_notified = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send imaging result notification: {e}")
            raise

    async def send_referral_notification(self, 
                                       patient_data: PatientCommunicationData,
                                       referral_data: ReferralData,
                                       workflow_id: str) -> Dict[str, Any]:
        """Send specialist referral notification"""
        try:
            if patient_data.preferred_language == Language.ARABIC:
                subject = "إحالة لطبيب متخصص - برينسيت للرعاية الصحية"
                content = f"عزيزي {patient_data.patient_id}، تم إحالتك لطبيب متخصص في {referral_data.specialty_ar or referral_data.specialty}."
                content += f"\n\nاسم الطبيب: {referral_data.specialist_name_ar or referral_data.specialist_name}"
                content += f"\nالسبب: {referral_data.reason_ar or referral_data.reason}"
            else:
                subject = "Specialist Referral - BrainSAIT Healthcare"
                content = f"Dear {patient_data.patient_id}, you have been referred to a {referral_data.specialty} specialist."
                content += f"\n\nSpecialist: {referral_data.specialist_name}"
                content += f"\nReason: {referral_data.reason}"
            
            if referral_data.contact_info:
                if patient_data.preferred_language == Language.ARABIC:
                    content += f"\n\nللحجز اتصل على: {referral_data.contact_info}"
                else:
                    content += f"\n\nTo schedule, call: {referral_data.contact_info}"
            
            if referral_data.urgency == NotificationUrgency.URGENT:
                if patient_data.preferred_language == Language.ARABIC:
                    content += "\n\n⚠️ هذه إحالة عاجلة - يرجى الحجز في أقرب وقت ممكن"
                else:
                    content += "\n\n⚠️ This is an urgent referral - please schedule as soon as possible"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.CLINICAL_RESULTS,
                patient_id=patient_data.patient_id,
                channel=CommunicationChannel.SMS,  # Referrals typically via SMS or email
                language=patient_data.preferred_language,
                priority=MessagePriority.HIGH if referral_data.urgency == NotificationUrgency.URGENT else MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "referral_id": referral_data.referral_id,
                    "specialist_id": referral_data.specialist_provider_id,
                    "urgency": referral_data.urgency.value
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send referral notification: {e}")
            raise

    async def escalate_critical_result(self, 
                                     workflow_id: str,
                                     escalation_contact: str,
                                     reason: str = "no_provider_response") -> Dict[str, Any]:
        """Escalate critical result when provider doesn't respond"""
        try:
            if workflow_id not in self.active_workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.active_workflows[workflow_id]
            clinical_result = workflow["clinical_result"]
            patient_data = workflow["patient_data"]
            
            if patient_data.preferred_language == Language.ARABIC:
                subject = "تصعيد نتيجة حرجة - برينسيت للرعاية الصحية"
                content = f"تنبيه: نتيجة حرجة للمريض {patient_data.patient_id} تحتاج انتباه فوري."
                content += f"\nالفحص: {clinical_result.test_name}"
                content += f"\nالسبب: {reason}"
            else:
                subject = "Critical Result Escalation - BrainSAIT Healthcare"
                content = f"ALERT: Critical result for patient {patient_data.patient_id} requires immediate attention."
                content += f"\nTest: {clinical_result.test_name}"
                content += f"\nReason: {reason}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.EMERGENCY,
                patient_id=f"escalation_{workflow_id}",
                channel=CommunicationChannel.VOICE,  # Escalations prefer voice
                language=Language.ENGLISH,  # Escalations typically in English
                priority=MessagePriority.CRITICAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "escalation_reason": reason,
                    "original_result_id": clinical_result.result_id
                }
            )
            
            # Create escalation contact data
            escalation_comm_data = PatientCommunicationData(
                patient_id=f"escalation_{workflow_id}",
                phone_number=escalation_contact,
                preferred_language=Language.ENGLISH,
                preferred_channels=[CommunicationChannel.VOICE, CommunicationChannel.SMS]
            )
            
            result = await self.communication_service.send_message(escalation_comm_data, message)
            
            # Store escalation in workflow
            workflow["escalations"].append({
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "escalation_contact": escalation_contact,
                "result": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to escalate critical result: {e}")
            raise

    async def mark_provider_reviewed(self, 
                                   workflow_id: str,
                                   provider_notes: Optional[str] = None) -> Dict[str, Any]:
        """Mark result as reviewed by provider and trigger patient notification"""
        try:
            if workflow_id not in self.active_workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.active_workflows[workflow_id]
            clinical_result = workflow["clinical_result"]
            patient_data = workflow["patient_data"]
            provider_data = workflow["provider_data"]
            
            # Mark as reviewed
            clinical_result.reviewed_by_provider = True
            if provider_notes:
                clinical_result.provider_notes = provider_notes
            
            # Send patient notification now that provider has reviewed
            if not clinical_result.patient_notified:
                if clinical_result.result_type == ResultType.IMAGING:
                    patient_notification = await self.send_imaging_result_notification(
                        patient_data, clinical_result, provider_data, workflow_id
                    )
                else:
                    patient_notification = await self.send_routine_result_notification(
                        patient_data, clinical_result, provider_data, workflow_id
                    )
                
                return {
                    "status": "reviewed_and_notified",
                    "provider_notes": provider_notes,
                    "patient_notification": patient_notification
                }
            
            return {
                "status": "reviewed",
                "provider_notes": provider_notes,
                "patient_already_notified": True
            }
            
        except Exception as e:
            logger.error(f"Failed to mark provider reviewed: {e}")
            raise

    async def _schedule_workflow_tasks(self, 
                                     workflow_id: str,
                                     schedule: Dict[str, Any]) -> List[str]:
        """Schedule workflow tasks based on notification timeline"""
        # In a production system, this would integrate with a task scheduler like Celery
        scheduled_tasks = []
        
        now = datetime.now()
        
        for task_name, scheduled_time in schedule.items():
            if isinstance(scheduled_time, datetime) and scheduled_time > now:
                task_id = f"{workflow_id}_{task_name}_{scheduled_time.isoformat()}"
                scheduled_tasks.append(task_id)
                logger.info(f"Scheduled clinical task {task_name} for {scheduled_time}")
        
        return scheduled_tasks

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a clinical results workflow"""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found"}
        
        workflow = self.active_workflows[workflow_id]
        clinical_result = workflow["clinical_result"]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "result_id": clinical_result.result_id,
            "result_type": clinical_result.result_type.value,
            "severity": clinical_result.severity.value,
            "urgency": clinical_result.urgency.value,
            "provider_reviewed": clinical_result.reviewed_by_provider,
            "patient_notified": clinical_result.patient_notified,
            "notifications_sent": len(workflow["notifications_sent"]),
            "escalations": len(workflow["escalations"]),
            "created_at": workflow["created_at"].isoformat()
        }

    async def get_pending_critical_results(self) -> List[Dict[str, Any]]:
        """Get all pending critical results that need attention"""
        pending_critical = []
        
        for workflow_id, workflow in self.active_workflows.items():
            clinical_result = workflow["clinical_result"]
            
            if (clinical_result.severity in [ResultSeverity.CRITICAL, ResultSeverity.PANIC_VALUE] and
                not clinical_result.reviewed_by_provider):
                
                pending_critical.append({
                    "workflow_id": workflow_id,
                    "result_id": clinical_result.result_id,
                    "patient_id": clinical_result.patient_id,
                    "test_name": clinical_result.test_name,
                    "severity": clinical_result.severity.value,
                    "result_date": clinical_result.result_date.isoformat() if clinical_result.result_date else None,
                    "time_since_result": (datetime.now() - (clinical_result.result_date or datetime.now())).total_seconds() / 60,
                    "provider_notified": len([n for n in workflow["notifications_sent"] if "provider" in n["type"]]) > 0
                })
        
        return pending_critical