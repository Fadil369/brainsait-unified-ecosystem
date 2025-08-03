"""
BrainSAIT Healthcare Platform - Visit Communication Workflow
Real-time communication during patient visit including check-in, wait time updates, and provider notifications

This workflow handles:
1. Patient arrival and check-in confirmation
2. Real-time wait time updates and delays
3. Provider and staff alerts for patient readiness
4. Room assignment notifications
5. Visit status updates and delays
6. Emergency notifications during visit
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from ..patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData, AppointmentData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)

logger = logging.getLogger(__name__)

class VisitStatus(str, Enum):
    """Visit status types"""
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class ProviderType(str, Enum):
    """Provider notification types"""
    PRIMARY_PROVIDER = "primary_provider"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"

@dataclass
class VisitData:
    """Visit-specific data"""
    visit_id: str
    appointment_id: str
    patient_id: str
    provider_id: str
    check_in_time: Optional[datetime] = None
    room_number: Optional[str] = None
    estimated_wait_time: int = 15  # minutes
    actual_wait_time: Optional[int] = None
    visit_status: VisitStatus = VisitStatus.SCHEDULED
    vitals_completed: bool = False
    provider_notified: bool = False
    special_instructions: Optional[str] = None

@dataclass
class ProviderData:
    """Provider communication data"""
    provider_id: str
    name: str
    name_ar: Optional[str] = None
    phone_number: str
    email: Optional[str] = None
    provider_type: ProviderType = ProviderType.PRIMARY_PROVIDER
    preferred_language: Language = Language.ENGLISH
    notification_preferences: List[CommunicationChannel] = None

    def __post_init__(self):
        if self.notification_preferences is None:
            self.notification_preferences = [CommunicationChannel.SMS, CommunicationChannel.PUSH_NOTIFICATION]

@dataclass
class VisitWorkflowConfig:
    """Configuration for visit workflow"""
    wait_time_update_threshold: int = 10  # Update if wait time changes by 10+ minutes
    provider_notification_delay: int = 5  # Notify provider 5 minutes before patient ready
    max_wait_time_acceptable: int = 60  # Escalate if wait time exceeds 60 minutes
    vitals_timeout_minutes: int = 30  # Timeout for vitals completion
    room_assignment_timeout: int = 15  # Timeout for room assignment

class VisitWorkflow:
    """
    Visit Communication Workflow Implementation
    
    Manages real-time communication during patient visits
    """
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
        self.config = VisitWorkflowConfig()
        self.active_visits: Dict[str, VisitData] = {}
        self.visit_workflows: Dict[str, Dict] = {}
        
    async def initiate_visit_workflow(self, 
                                    patient_data: PatientCommunicationData,
                                    appointment_data: AppointmentData,
                                    provider_data: ProviderData) -> Dict[str, Any]:
        """
        Initiate visit workflow when patient arrives
        
        Args:
            patient_data: Patient communication information
            appointment_data: Appointment details
            provider_data: Provider notification information
            
        Returns:
            Workflow initiation result
        """
        try:
            visit_id = f"visit_{appointment_data.appointment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create visit data
            visit_data = VisitData(
                visit_id=visit_id,
                appointment_id=appointment_data.appointment_id,
                patient_id=patient_data.patient_id,
                provider_id=provider_data.provider_id,
                check_in_time=datetime.now(),
                visit_status=VisitStatus.CHECKED_IN
            )
            
            # Store visit data
            self.active_visits[visit_id] = visit_data
            
            # Create workflow state
            workflow_state = {
                "visit_id": visit_id,
                "patient_data": patient_data,
                "appointment_data": appointment_data,
                "provider_data": provider_data,
                "visit_data": visit_data,
                "status": "active",
                "events": [],
                "created_at": datetime.now()
            }
            
            self.visit_workflows[visit_id] = workflow_state
            
            # Send check-in confirmation to patient
            check_in_result = await self.send_check_in_confirmation(
                patient_data, appointment_data, visit_data
            )
            
            # Notify provider of patient arrival
            provider_notification_result = await self.notify_provider_patient_arrival(
                provider_data, patient_data, appointment_data, visit_data
            )
            
            # Log event
            await self._log_visit_event(visit_id, "workflow_initiated", {
                "check_in_result": check_in_result,
                "provider_notification": provider_notification_result
            })
            
            logger.info(f"Visit workflow initiated for visit {visit_id}")
            
            return {
                "visit_id": visit_id,
                "status": "initiated",
                "check_in_confirmation": check_in_result,
                "provider_notification": provider_notification_result
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate visit workflow: {e}")
            raise

    async def send_check_in_confirmation(self, 
                                       patient_data: PatientCommunicationData,
                                       appointment_data: AppointmentData,
                                       visit_data: VisitData) -> Dict[str, Any]:
        """Send check-in confirmation to patient"""
        try:
            template = self.communication_service.message_templates["check_in_notification"]
            
            variables = {
                "patient_name": patient_data.patient_id,
                "provider_name": appointment_data.provider_name_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.provider_name,
                "wait_time": str(visit_data.estimated_wait_time)
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "visit_id": visit_data.visit_id,
                    "template_id": template.template_id,
                    "event_type": "check_in_confirmation"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update visit status
            if result["status"] == "sent":
                visit_data.visit_status = VisitStatus.WAITING
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send check-in confirmation: {e}")
            raise

    async def notify_provider_patient_arrival(self, 
                                            provider_data: ProviderData,
                                            patient_data: PatientCommunicationData,
                                            appointment_data: AppointmentData,
                                            visit_data: VisitData) -> Dict[str, Any]:
        """Notify provider of patient arrival"""
        try:
            # Create provider notification message
            if provider_data.preferred_language == Language.ARABIC:
                subject = "وصول مريض - برينسيت للرعاية الصحية"
                content = f"دكتور {provider_data.name}، المريض {patient_data.patient_id} وصل لموعده في {visit_data.check_in_time.strftime('%H:%M')}. سيتم إشعارك عند جاهزيته."
            else:
                subject = "Patient Arrival - BrainSAIT Healthcare"
                content = f"Dr. {provider_data.name}, patient {patient_data.patient_id} has arrived for their {visit_data.check_in_time.strftime('%H:%M')} appointment. You will be notified when they are ready."
            
            # Select channel based on provider preferences
            channel = provider_data.notification_preferences[0] if provider_data.notification_preferences else CommunicationChannel.SMS
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.VISIT,
                patient_id=provider_data.provider_id,  # Using provider_id as patient_id for provider notifications
                channel=channel,
                language=provider_data.preferred_language,
                priority=MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "visit_id": visit_data.visit_id,
                    "event_type": "provider_arrival_notification",
                    "patient_id": patient_data.patient_id
                }
            )
            
            # Create temporary patient data for provider notification
            provider_comm_data = PatientCommunicationData(
                patient_id=provider_data.provider_id,
                phone_number=provider_data.phone_number,
                email=provider_data.email,
                preferred_language=provider_data.preferred_language,
                preferred_channels=provider_data.notification_preferences
            )
            
            result = await self.communication_service.send_message(provider_comm_data, message)
            
            if result["status"] == "sent":
                visit_data.provider_notified = True
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to notify provider of patient arrival: {e}")
            raise

    async def update_wait_time(self, 
                             visit_id: str,
                             new_wait_time: int,
                             delay_reason: Optional[str] = None) -> Dict[str, Any]:
        """Update patient wait time and send notification if significant change"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            visit_data = self.active_visits[visit_id]
            workflow = self.visit_workflows[visit_id]
            patient_data = workflow["patient_data"]
            
            old_wait_time = visit_data.estimated_wait_time
            wait_time_change = abs(new_wait_time - old_wait_time)
            
            # Update wait time
            visit_data.estimated_wait_time = new_wait_time
            
            # Send update if change is significant
            if wait_time_change >= self.config.wait_time_update_threshold:
                update_result = await self.send_wait_time_update(
                    patient_data, visit_data, old_wait_time, delay_reason
                )
                
                # Log event
                await self._log_visit_event(visit_id, "wait_time_updated", {
                    "old_wait_time": old_wait_time,
                    "new_wait_time": new_wait_time,
                    "change": wait_time_change,
                    "delay_reason": delay_reason,
                    "update_sent": update_result["status"] == "sent"
                })
                
                return {
                    "status": "updated",
                    "old_wait_time": old_wait_time,
                    "new_wait_time": new_wait_time,
                    "notification_sent": True,
                    "notification_result": update_result
                }
            else:
                await self._log_visit_event(visit_id, "wait_time_updated", {
                    "old_wait_time": old_wait_time,
                    "new_wait_time": new_wait_time,
                    "change": wait_time_change,
                    "notification_sent": False,
                    "reason": "Change below threshold"
                })
                
                return {
                    "status": "updated",
                    "old_wait_time": old_wait_time,
                    "new_wait_time": new_wait_time,
                    "notification_sent": False,
                    "reason": "Change below notification threshold"
                }
            
        except Exception as e:
            logger.error(f"Failed to update wait time for visit {visit_id}: {e}")
            raise

    async def send_wait_time_update(self, 
                                  patient_data: PatientCommunicationData,
                                  visit_data: VisitData,
                                  old_wait_time: int,
                                  delay_reason: Optional[str] = None) -> Dict[str, Any]:
        """Send wait time update to patient"""
        try:
            template = self.communication_service.message_templates["wait_time_update"]
            
            delay_minutes = visit_data.estimated_wait_time - old_wait_time
            
            variables = {
                "patient_name": patient_data.patient_id,
                "delay_minutes": str(abs(delay_minutes)),
                "new_wait_time": str(visit_data.estimated_wait_time)
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add delay reason if provided
            if delay_reason:
                if patient_data.preferred_language == Language.ARABIC:
                    content += f" السبب: {delay_reason}"
                else:
                    content += f" Reason: {delay_reason}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "visit_id": visit_data.visit_id,
                    "template_id": template.template_id,
                    "event_type": "wait_time_update",
                    "delay_minutes": delay_minutes,
                    "delay_reason": delay_reason
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send wait time update: {e}")
            raise

    async def assign_room(self, 
                        visit_id: str,
                        room_number: str) -> Dict[str, Any]:
        """Assign room to patient and notify relevant parties"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            visit_data = self.active_visits[visit_id]
            workflow = self.visit_workflows[visit_id]
            patient_data = workflow["patient_data"]
            
            # Update room assignment
            visit_data.room_number = room_number
            
            # Send room assignment notification to patient
            patient_notification = await self.send_room_assignment_notification(
                patient_data, visit_data
            )
            
            # Log event
            await self._log_visit_event(visit_id, "room_assigned", {
                "room_number": room_number,
                "notification_result": patient_notification
            })
            
            return {
                "status": "assigned",
                "room_number": room_number,
                "patient_notification": patient_notification
            }
            
        except Exception as e:
            logger.error(f"Failed to assign room for visit {visit_id}: {e}")
            raise

    async def send_room_assignment_notification(self, 
                                              patient_data: PatientCommunicationData,
                                              visit_data: VisitData) -> Dict[str, Any]:
        """Send room assignment notification to patient"""
        try:
            if patient_data.preferred_language == Language.ARABIC:
                subject = "تخصيص غرفة - برينسيت للرعاية الصحية"
                content = f"مرحباً {patient_data.patient_id}، تم تخصيص الغرفة رقم {visit_data.room_number} لك. يرجى التوجه إلى الغرفة."
            else:
                subject = "Room Assignment - BrainSAIT Healthcare"
                content = f"Hello {patient_data.patient_id}, you have been assigned to Room {visit_data.room_number}. Please proceed to your room."
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.VISIT,
                patient_id=patient_data.patient_id,
                channel=CommunicationChannel.SMS,  # Default to SMS for room notifications
                language=patient_data.preferred_language,
                priority=MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "visit_id": visit_data.visit_id,
                    "event_type": "room_assignment",
                    "room_number": visit_data.room_number
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send room assignment notification: {e}")
            raise

    async def complete_vitals(self, 
                            visit_id: str,
                            vitals_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark vitals as completed and notify provider"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            visit_data = self.active_visits[visit_id]
            workflow = self.visit_workflows[visit_id]
            provider_data = workflow["provider_data"]
            
            # Update vitals status
            visit_data.vitals_completed = True
            
            # Notify provider that patient is ready
            provider_notification = await self.notify_provider_patient_ready(
                provider_data, workflow["patient_data"], visit_data
            )
            
            # Log event
            await self._log_visit_event(visit_id, "vitals_completed", {
                "vitals_data": vitals_data,
                "provider_notification": provider_notification
            })
            
            return {
                "status": "completed",
                "vitals_data": vitals_data,
                "provider_notification": provider_notification
            }
            
        except Exception as e:
            logger.error(f"Failed to complete vitals for visit {visit_id}: {e}")
            raise

    async def notify_provider_patient_ready(self, 
                                          provider_data: ProviderData,
                                          patient_data: PatientCommunicationData,
                                          visit_data: VisitData) -> Dict[str, Any]:
        """Notify provider that patient is ready"""
        try:
            template = self.communication_service.message_templates["provider_alert"]
            
            variables = {
                "provider_name": provider_data.name,
                "patient_name": patient_data.patient_id,
                "patient_id": patient_data.patient_id,
                "room_number": visit_data.room_number or "TBD"
            }
            
            subject, content = self.communication_service.render_message_template(
                template, provider_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.VISIT,
                patient_id=provider_data.provider_id,
                channel=provider_data.notification_preferences[0],
                language=provider_data.preferred_language,
                priority=MessagePriority.HIGH,
                subject=subject,
                message_content=content,
                metadata={
                    "visit_id": visit_data.visit_id,
                    "template_id": template.template_id,
                    "event_type": "patient_ready_notification"
                }
            )
            
            # Create provider communication data
            provider_comm_data = PatientCommunicationData(
                patient_id=provider_data.provider_id,
                phone_number=provider_data.phone_number,
                email=provider_data.email,
                preferred_language=provider_data.preferred_language,
                preferred_channels=provider_data.notification_preferences
            )
            
            result = await self.communication_service.send_message(provider_comm_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to notify provider that patient is ready: {e}")
            raise

    async def start_visit(self, visit_id: str) -> Dict[str, Any]:
        """Mark visit as started when provider begins seeing patient"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            visit_data = self.active_visits[visit_id]
            visit_data.visit_status = VisitStatus.IN_PROGRESS
            
            # Calculate actual wait time
            if visit_data.check_in_time:
                visit_data.actual_wait_time = int((datetime.now() - visit_data.check_in_time).total_seconds() / 60)
            
            # Log event
            await self._log_visit_event(visit_id, "visit_started", {
                "actual_wait_time": visit_data.actual_wait_time
            })
            
            return {
                "status": "started",
                "visit_id": visit_id,
                "actual_wait_time": visit_data.actual_wait_time
            }
            
        except Exception as e:
            logger.error(f"Failed to start visit {visit_id}: {e}")
            raise

    async def complete_visit(self, visit_id: str) -> Dict[str, Any]:
        """Mark visit as completed"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            visit_data = self.active_visits[visit_id]
            visit_data.visit_status = VisitStatus.COMPLETED
            
            # Log event
            await self._log_visit_event(visit_id, "visit_completed", {
                "completion_time": datetime.now().isoformat()
            })
            
            # Visit workflow will transition to post-visit workflow
            return {
                "status": "completed",
                "visit_id": visit_id,
                "ready_for_post_visit": True
            }
            
        except Exception as e:
            logger.error(f"Failed to complete visit {visit_id}: {e}")
            raise

    async def handle_visit_emergency(self, 
                                   visit_id: str,
                                   emergency_type: str,
                                   emergency_details: str) -> Dict[str, Any]:
        """Handle emergency situation during visit"""
        try:
            if visit_id not in self.active_visits:
                raise ValueError(f"Visit {visit_id} not found")
            
            workflow = self.visit_workflows[visit_id]
            patient_data = workflow["patient_data"]
            provider_data = workflow["provider_data"]
            
            # Send emergency notifications
            notifications = []
            
            # Notify emergency contacts if available
            if patient_data.emergency_contact:
                emergency_notification = await self.send_emergency_notification(
                    patient_data.emergency_contact, patient_data, emergency_details
                )
                notifications.append(emergency_notification)
            
            # Log emergency event
            await self._log_visit_event(visit_id, "emergency_occurred", {
                "emergency_type": emergency_type,
                "emergency_details": emergency_details,
                "notifications_sent": len(notifications)
            })
            
            return {
                "status": "emergency_handled",
                "emergency_type": emergency_type,
                "notifications_sent": notifications
            }
            
        except Exception as e:
            logger.error(f"Failed to handle visit emergency for {visit_id}: {e}")
            raise

    async def send_emergency_notification(self, 
                                        emergency_contact: str,
                                        patient_data: PatientCommunicationData,
                                        emergency_details: str) -> Dict[str, Any]:
        """Send emergency notification to emergency contact"""
        try:
            if patient_data.preferred_language == Language.ARABIC:
                subject = "إشعار طوارئ - برينسيت للرعاية الصحية"
                content = f"هذا إشعار عاجل بخصوص {patient_data.patient_id}. يرجى الاتصال بالمستشفى فوراً. تفاصيل: {emergency_details}"
            else:
                subject = "Emergency Notification - BrainSAIT Healthcare"
                content = f"This is an urgent notification regarding {patient_data.patient_id}. Please contact the hospital immediately. Details: {emergency_details}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.EMERGENCY,
                patient_id=f"emergency_{patient_data.patient_id}",
                channel=CommunicationChannel.VOICE,  # Emergency notifications prefer voice
                language=patient_data.preferred_language,
                priority=MessagePriority.CRITICAL,
                subject=subject,
                message_content=content,
                metadata={
                    "emergency_contact": emergency_contact,
                    "patient_id": patient_data.patient_id,
                    "event_type": "emergency_notification"
                }
            )
            
            # Create emergency contact data
            emergency_comm_data = PatientCommunicationData(
                patient_id=f"emergency_{patient_data.patient_id}",
                phone_number=emergency_contact,
                preferred_language=patient_data.preferred_language,
                preferred_channels=[CommunicationChannel.VOICE, CommunicationChannel.SMS]
            )
            
            result = await self.communication_service.send_message(emergency_comm_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send emergency notification: {e}")
            raise

    async def _log_visit_event(self, 
                             visit_id: str,
                             event_type: str,
                             event_data: Dict[str, Any]):
        """Log visit event for audit and tracking"""
        if visit_id in self.visit_workflows:
            event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": event_data
            }
            self.visit_workflows[visit_id]["events"].append(event)
            
            # Also log to main logging system
            logger.info(f"VISIT_EVENT: {visit_id} - {event_type} - {event_data}")

    async def get_visit_status(self, visit_id: str) -> Dict[str, Any]:
        """Get current visit status and workflow information"""
        try:
            if visit_id not in self.active_visits:
                return {"status": "not_found"}
            
            visit_data = self.active_visits[visit_id]
            workflow = self.visit_workflows[visit_id]
            
            return {
                "visit_id": visit_id,
                "visit_status": visit_data.visit_status.value,
                "check_in_time": visit_data.check_in_time.isoformat() if visit_data.check_in_time else None,
                "room_number": visit_data.room_number,
                "estimated_wait_time": visit_data.estimated_wait_time,
                "actual_wait_time": visit_data.actual_wait_time,
                "vitals_completed": visit_data.vitals_completed,
                "provider_notified": visit_data.provider_notified,
                "events_count": len(workflow["events"]),
                "last_event": workflow["events"][-1] if workflow["events"] else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get visit status for {visit_id}: {e}")
            raise

    async def get_active_visits(self) -> List[Dict[str, Any]]:
        """Get all active visits"""
        active_visits = []
        
        for visit_id, visit_data in self.active_visits.items():
            if visit_data.visit_status not in [VisitStatus.COMPLETED, VisitStatus.CANCELLED]:
                active_visits.append({
                    "visit_id": visit_id,
                    "patient_id": visit_data.patient_id,
                    "provider_id": visit_data.provider_id,
                    "status": visit_data.visit_status.value,
                    "check_in_time": visit_data.check_in_time.isoformat() if visit_data.check_in_time else None,
                    "estimated_wait_time": visit_data.estimated_wait_time
                })
        
        return active_visits