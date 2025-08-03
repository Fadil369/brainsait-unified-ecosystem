"""
BrainSAIT Healthcare Platform - Pre-Visit Communication Workflow
Comprehensive pre-visit communication including appointment confirmation, health screening, and insurance verification

This workflow handles:
1. Appointment confirmation (immediate and 24h before)
2. Pre-visit health screening reminders
3. Insurance verification notifications
4. Preparation instructions
5. Cancellation and rescheduling management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import logging
from dataclasses import dataclass

from ..patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData, AppointmentData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)

logger = logging.getLogger(__name__)

@dataclass
class PreVisitWorkflowConfig:
    """Configuration for pre-visit workflow"""
    confirmation_delay_hours: int = 1  # Send confirmation 1 hour after booking
    reminder_hours_before: int = 24  # Send reminder 24 hours before appointment
    screening_hours_before: int = 48  # Send screening 48 hours before
    insurance_check_hours_before: int = 72  # Check insurance 72 hours before
    max_reminder_attempts: int = 3
    escalation_hours: int = 6  # Escalate if no response in 6 hours

class PreVisitWorkflow:
    """
    Pre-Visit Communication Workflow Implementation
    
    Manages all communication from appointment booking through patient arrival
    """
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
        self.config = PreVisitWorkflowConfig()
        self.active_workflows: Dict[str, Dict] = {}
        
    async def initiate_pre_visit_workflow(self, 
                                        patient_data: PatientCommunicationData,
                                        appointment_data: AppointmentData) -> Dict[str, Any]:
        """
        Initiate the complete pre-visit workflow for a new appointment
        
        Args:
            patient_data: Patient communication information
            appointment_data: Appointment details
            
        Returns:
            Workflow initiation result with scheduled tasks
        """
        try:
            workflow_id = f"pre_visit_{appointment_data.appointment_id}"
            
            # Calculate workflow schedule
            now = datetime.now()
            appointment_time = appointment_data.appointment_datetime
            
            schedule = {
                "confirmation": now + timedelta(hours=self.config.confirmation_delay_hours),
                "insurance_check": appointment_time - timedelta(hours=self.config.insurance_check_hours_before),
                "screening_reminder": appointment_time - timedelta(hours=self.config.screening_hours_before),
                "final_reminder": appointment_time - timedelta(hours=self.config.reminder_hours_before),
                "preparation_instructions": appointment_time - timedelta(hours=12)
            }
            
            # Store workflow state
            self.active_workflows[workflow_id] = {
                "patient_data": patient_data,
                "appointment_data": appointment_data,
                "schedule": schedule,
                "status": "initiated",
                "completed_tasks": [],
                "failed_tasks": [],
                "created_at": now
            }
            
            # Schedule immediate confirmation
            confirmation_result = await self.send_appointment_confirmation(
                patient_data, appointment_data, workflow_id
            )
            
            # Schedule future tasks
            scheduled_tasks = await self._schedule_workflow_tasks(
                workflow_id, patient_data, appointment_data, schedule
            )
            
            logger.info(f"Pre-visit workflow initiated for appointment {appointment_data.appointment_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "initiated",
                "confirmation_result": confirmation_result,
                "scheduled_tasks": scheduled_tasks,
                "schedule": {k: v.isoformat() for k, v in schedule.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate pre-visit workflow: {e}")
            raise

    async def send_appointment_confirmation(self, 
                                          patient_data: PatientCommunicationData,
                                          appointment_data: AppointmentData,
                                          workflow_id: str) -> Dict[str, Any]:
        """Send appointment confirmation message"""
        try:
            template = self.communication_service.message_templates["appointment_confirmation"]
            
            # Prepare message variables
            variables = {
                "patient_name": patient_data.patient_id,  # Would get actual name from patient service
                "provider_name": appointment_data.provider_name_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.provider_name,
                "appointment_date": appointment_data.appointment_datetime.strftime("%Y-%m-%d"),
                "appointment_time": appointment_data.appointment_datetime.strftime("%H:%M"),
                "location": appointment_data.location_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.location
            }
            
            # Select channel
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            # Render message
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Create message
            message = CommunicationMessage(
                workflow_type=WorkflowType.PRE_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "appointment_id": appointment_data.appointment_id
                }
            )
            
            # Send message
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("confirmation")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("confirmation")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send appointment confirmation: {e}")
            raise

    async def send_insurance_verification_request(self, 
                                                patient_data: PatientCommunicationData,
                                                appointment_data: AppointmentData,
                                                workflow_id: str) -> Dict[str, Any]:
        """Send insurance verification request"""
        try:
            template = self.communication_service.message_templates["insurance_verification"]
            
            variables = {
                "patient_name": patient_data.patient_id,
                "appointment_date": appointment_data.appointment_datetime.strftime("%Y-%m-%d"),
                "clinic_phone": "+966112345678"  # Would get from clinic settings
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.PRE_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "appointment_id": appointment_data.appointment_id
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("insurance_verification")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("insurance_verification")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send insurance verification request: {e}")
            raise

    async def send_health_screening_reminder(self, 
                                           patient_data: PatientCommunicationData,
                                           appointment_data: AppointmentData,
                                           workflow_id: str) -> Dict[str, Any]:
        """Send pre-visit health screening reminder"""
        try:
            template = self.communication_service.message_templates["pre_visit_screening"]
            
            # Generate screening link (would integrate with actual screening system)
            screening_link = f"https://brainsait.com/screening/{appointment_data.appointment_id}"
            
            variables = {
                "patient_name": patient_data.patient_id,
                "screening_link": screening_link
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.PRE_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "appointment_id": appointment_data.appointment_id,
                    "screening_link": screening_link
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("health_screening")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("health_screening")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send health screening reminder: {e}")
            raise

    async def send_final_reminder(self, 
                                patient_data: PatientCommunicationData,
                                appointment_data: AppointmentData,
                                workflow_id: str) -> Dict[str, Any]:
        """Send final appointment reminder 24 hours before"""
        try:
            # Use the confirmation template for final reminder
            template = self.communication_service.message_templates["appointment_confirmation"]
            
            variables = {
                "patient_name": patient_data.patient_id,
                "provider_name": appointment_data.provider_name_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.provider_name,
                "appointment_date": appointment_data.appointment_datetime.strftime("%Y-%m-%d"),
                "appointment_time": appointment_data.appointment_datetime.strftime("%H:%M"),
                "location": appointment_data.location_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.location
            }
            
            # Modify content for reminder
            if patient_data.preferred_language == Language.ARABIC:
                reminder_content = f"تذكير: {template.content_ar}"
            else:
                reminder_content = f"REMINDER: {template.content_en}"
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, _ = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Use modified content for reminder
            _, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            content = reminder_content.format(**variables)
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.PRE_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=MessagePriority.HIGH,  # Higher priority for final reminder
                subject=f"REMINDER: {subject}",
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": f"{template.template_id}_reminder",
                    "appointment_id": appointment_data.appointment_id
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("final_reminder")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("final_reminder")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send final reminder: {e}")
            raise

    async def handle_appointment_cancellation(self, 
                                            appointment_id: str,
                                            reason: str = "patient_request") -> Dict[str, Any]:
        """Handle appointment cancellation and stop workflow"""
        try:
            workflow_id = f"pre_visit_{appointment_id}"
            
            if workflow_id not in self.active_workflows:
                return {"status": "workflow_not_found"}
            
            workflow = self.active_workflows[workflow_id]
            patient_data = workflow["patient_data"]
            appointment_data = workflow["appointment_data"]
            
            # Send cancellation confirmation
            cancellation_message = self._create_cancellation_message(
                patient_data, appointment_data, reason
            )
            
            result = await self.communication_service.send_message(
                patient_data, cancellation_message
            )
            
            # Mark workflow as cancelled
            workflow["status"] = "cancelled"
            workflow["cancellation_reason"] = reason
            workflow["cancelled_at"] = datetime.now()
            
            logger.info(f"Pre-visit workflow cancelled for appointment {appointment_id}")
            
            return {
                "status": "cancelled",
                "workflow_id": workflow_id,
                "cancellation_result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to handle appointment cancellation: {e}")
            raise

    async def handle_appointment_rescheduling(self, 
                                            old_appointment_id: str,
                                            new_appointment_data: AppointmentData) -> Dict[str, Any]:
        """Handle appointment rescheduling"""
        try:
            # Cancel old workflow
            cancellation_result = await self.handle_appointment_cancellation(
                old_appointment_id, "rescheduled"
            )
            
            # Get patient data from cancelled workflow
            old_workflow_id = f"pre_visit_{old_appointment_id}"
            if old_workflow_id in self.active_workflows:
                patient_data = self.active_workflows[old_workflow_id]["patient_data"]
                
                # Start new workflow for rescheduled appointment
                new_workflow_result = await self.initiate_pre_visit_workflow(
                    patient_data, new_appointment_data
                )
                
                return {
                    "status": "rescheduled",
                    "old_workflow": cancellation_result,
                    "new_workflow": new_workflow_result
                }
            
            return {"status": "failed", "error": "Original workflow not found"}
            
        except Exception as e:
            logger.error(f"Failed to handle appointment rescheduling: {e}")
            raise

    def _create_cancellation_message(self, 
                                   patient_data: PatientCommunicationData,
                                   appointment_data: AppointmentData,
                                   reason: str) -> CommunicationMessage:
        """Create cancellation confirmation message"""
        if patient_data.preferred_language == Language.ARABIC:
            subject = "إلغاء الموعد - برينسيت للرعاية الصحية"
            if reason == "rescheduled":
                content = f"عزيزي {patient_data.patient_id}، تم إعادة جدولة موعدك مع الدكتور {appointment_data.provider_name}. سيتم إرسال تفاصيل الموعد الجديد قريباً."
            else:
                content = f"عزيزي {patient_data.patient_id}، تم إلغاء موعدك المقرر في {appointment_data.appointment_datetime.strftime('%Y-%m-%d')} مع الدكتور {appointment_data.provider_name}. لحجز موعد جديد، يرجى الاتصال بنا."
        else:
            subject = "Appointment Cancellation - BrainSAIT Healthcare"
            if reason == "rescheduled":
                content = f"Dear {patient_data.patient_id}, your appointment with Dr. {appointment_data.provider_name} has been rescheduled. New appointment details will be sent shortly."
            else:
                content = f"Dear {patient_data.patient_id}, your appointment scheduled for {appointment_data.appointment_datetime.strftime('%Y-%m-%d')} with Dr. {appointment_data.provider_name} has been cancelled. Please contact us to schedule a new appointment."
        
        return CommunicationMessage(
            workflow_type=WorkflowType.PRE_VISIT,
            patient_id=patient_data.patient_id,
            channel=CommunicationChannel.SMS,  # Default to SMS for cancellations
            language=patient_data.preferred_language,
            priority=MessagePriority.HIGH,
            subject=subject,
            message_content=content,
            metadata={
                "reason": reason,
                "appointment_id": appointment_data.appointment_id
            }
        )

    async def _schedule_workflow_tasks(self, 
                                     workflow_id: str,
                                     patient_data: PatientCommunicationData,
                                     appointment_data: AppointmentData,
                                     schedule: Dict[str, datetime]) -> List[str]:
        """Schedule future workflow tasks (placeholder for task scheduler integration)"""
        # In a production system, this would integrate with a task scheduler like Celery
        scheduled_tasks = []
        
        now = datetime.now()
        
        for task_name, scheduled_time in schedule.items():
            if scheduled_time > now and task_name != "confirmation":
                # Schedule task (would use actual task scheduler)
                task_id = f"{workflow_id}_{task_name}_{scheduled_time.isoformat()}"
                scheduled_tasks.append(task_id)
                logger.info(f"Scheduled task {task_name} for {scheduled_time}")
        
        return scheduled_tasks

    async def get_workflow_status(self, appointment_id: str) -> Dict[str, Any]:
        """Get the status of a pre-visit workflow"""
        workflow_id = f"pre_visit_{appointment_id}"
        
        if workflow_id not in self.active_workflows:
            return {"status": "not_found"}
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "appointment_id": appointment_id,
            "created_at": workflow["created_at"].isoformat(),
            "completed_tasks": workflow["completed_tasks"],
            "failed_tasks": workflow["failed_tasks"],
            "next_scheduled_task": self._get_next_scheduled_task(workflow)
        }

    def _get_next_scheduled_task(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Get the next scheduled task for a workflow"""
        schedule = workflow["schedule"]
        completed = workflow["completed_tasks"]
        now = datetime.now()
        
        upcoming_tasks = []
        for task_name, scheduled_time in schedule.items():
            if task_name not in completed and scheduled_time > now:
                upcoming_tasks.append((task_name, scheduled_time))
        
        if upcoming_tasks:
            # Return the earliest upcoming task
            upcoming_tasks.sort(key=lambda x: x[1])
            return upcoming_tasks[0][0]
        
        return None