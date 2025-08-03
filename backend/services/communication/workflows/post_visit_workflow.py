"""
BrainSAIT Healthcare Platform - Post-Visit Communication Workflow
Comprehensive post-visit communication including visit summaries, prescriptions, follow-ups, and care plans

This workflow handles:
1. Visit summary delivery and patient portal access
2. Prescription notifications and pharmacy coordination
3. Follow-up appointment scheduling and reminders
4. Care plan delivery and patient education
5. Satisfaction surveys and feedback collection
6. Insurance claims and billing notifications
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

class FollowUpType(str, Enum):
    """Follow-up appointment types"""
    ROUTINE_CHECKUP = "routine_checkup"
    TREATMENT_MONITORING = "treatment_monitoring"
    TEST_RESULTS_REVIEW = "test_results_review"
    MEDICATION_ADJUSTMENT = "medication_adjustment"
    SURGICAL_FOLLOWUP = "surgical_followup"
    CHRONIC_CARE = "chronic_care"

class PrescriptionStatus(str, Enum):
    """Prescription status types"""
    PRESCRIBED = "prescribed"
    SENT_TO_PHARMACY = "sent_to_pharmacy"
    READY_FOR_PICKUP = "ready_for_pickup"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"

@dataclass
class PostVisitData:
    """Post-visit specific data"""
    visit_id: str
    appointment_id: str
    patient_id: str
    provider_id: str
    visit_completed_time: datetime
    diagnosis_codes: List[str] = None
    prescribed_medications: List[Dict[str, Any]] = None
    follow_up_required: bool = False
    follow_up_type: Optional[FollowUpType] = None
    follow_up_timeframe: Optional[str] = None  # "1 week", "2 months", etc.
    care_instructions: Optional[str] = None
    care_instructions_ar: Optional[str] = None
    referrals: List[Dict[str, Any]] = None
    discharge_summary: Optional[str] = None

@dataclass
class PrescriptionData:
    """Prescription information"""
    prescription_id: str
    medication_name: str
    medication_name_ar: Optional[str] = None
    dosage: str
    frequency: str
    duration: str
    instructions: str
    instructions_ar: Optional[str] = None
    pharmacy_name: Optional[str] = None
    pharmacy_phone: Optional[str] = None
    status: PrescriptionStatus = PrescriptionStatus.PRESCRIBED
    refills_remaining: int = 0

@dataclass
class FollowUpData:
    """Follow-up appointment information"""
    follow_up_id: str
    follow_up_type: FollowUpType
    provider_id: str
    provider_name: str
    timeframe: str
    priority: MessagePriority = MessagePriority.NORMAL
    instructions: Optional[str] = None
    instructions_ar: Optional[str] = None
    booking_link: Optional[str] = None

@dataclass
class PostVisitWorkflowConfig:
    """Configuration for post-visit workflow"""
    summary_delay_hours: int = 1  # Send summary 1 hour after visit
    prescription_notification_delay: int = 30  # Notify 30 minutes after prescription
    follow_up_reminder_days: int = 7  # Send follow-up reminder after 7 days
    satisfaction_survey_delay_hours: int = 24  # Send survey 24 hours after visit
    care_plan_delivery_delay: int = 2  # Send care plan 2 hours after visit
    max_follow_up_reminders: int = 3

class PostVisitWorkflow:
    """
    Post-Visit Communication Workflow Implementation
    
    Manages all communication after patient visit completion
    """
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
        self.config = PostVisitWorkflowConfig()
        self.active_workflows: Dict[str, Dict] = {}
        
    async def initiate_post_visit_workflow(self, 
                                         patient_data: PatientCommunicationData,
                                         appointment_data: AppointmentData,
                                         post_visit_data: PostVisitData) -> Dict[str, Any]:
        """
        Initiate the complete post-visit workflow
        
        Args:
            patient_data: Patient communication information
            appointment_data: Original appointment details
            post_visit_data: Post-visit specific information
            
        Returns:
            Workflow initiation result with scheduled tasks
        """
        try:
            workflow_id = f"post_visit_{post_visit_data.visit_id}"
            
            # Calculate workflow schedule
            now = datetime.now()
            visit_time = post_visit_data.visit_completed_time
            
            schedule = {
                "visit_summary": visit_time + timedelta(hours=self.config.summary_delay_hours),
                "care_plan": visit_time + timedelta(hours=self.config.care_plan_delivery_delay),
                "satisfaction_survey": visit_time + timedelta(hours=self.config.satisfaction_survey_delay_hours)
            }
            
            # Add follow-up reminders if needed
            if post_visit_data.follow_up_required:
                schedule["follow_up_reminder"] = visit_time + timedelta(days=self.config.follow_up_reminder_days)
            
            # Store workflow state
            workflow_state = {
                "workflow_id": workflow_id,
                "patient_data": patient_data,
                "appointment_data": appointment_data,
                "post_visit_data": post_visit_data,
                "schedule": schedule,
                "status": "initiated",
                "completed_tasks": [],
                "failed_tasks": [],
                "created_at": now,
                "prescriptions": [],
                "follow_ups": []
            }
            
            self.active_workflows[workflow_id] = workflow_state
            
            # Send immediate visit summary
            summary_result = await self.send_visit_summary(
                patient_data, appointment_data, post_visit_data, workflow_id
            )
            
            # Process prescriptions if any
            prescription_results = []
            if post_visit_data.prescribed_medications:
                for medication in post_visit_data.prescribed_medications:
                    prescription_result = await self.process_prescription(
                        patient_data, medication, workflow_id
                    )
                    prescription_results.append(prescription_result)
            
            # Schedule future tasks
            scheduled_tasks = await self._schedule_workflow_tasks(
                workflow_id, patient_data, schedule
            )
            
            logger.info(f"Post-visit workflow initiated for visit {post_visit_data.visit_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "initiated",
                "visit_summary": summary_result,
                "prescriptions": prescription_results,
                "scheduled_tasks": scheduled_tasks,
                "schedule": {k: v.isoformat() for k, v in schedule.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate post-visit workflow: {e}")
            raise

    async def send_visit_summary(self, 
                               patient_data: PatientCommunicationData,
                               appointment_data: AppointmentData,
                               post_visit_data: PostVisitData,
                               workflow_id: str) -> Dict[str, Any]:
        """Send visit summary to patient"""
        try:
            template = self.communication_service.message_templates["visit_summary"]
            
            # Generate patient portal link (would integrate with actual portal)
            portal_link = f"https://brainsait.com/portal/visit/{post_visit_data.visit_id}"
            
            variables = {
                "patient_name": patient_data.patient_id,
                "provider_name": appointment_data.provider_name_ar if patient_data.preferred_language == Language.ARABIC else appointment_data.provider_name,
                "portal_link": portal_link
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add care instructions if available
            if post_visit_data.care_instructions:
                care_instructions = post_visit_data.care_instructions_ar if patient_data.preferred_language == Language.ARABIC else post_visit_data.care_instructions
                if patient_data.preferred_language == Language.ARABIC:
                    content += f"\n\nتعليمات العناية: {care_instructions}"
                else:
                    content += f"\n\nCare Instructions: {care_instructions}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "visit_id": post_visit_data.visit_id,
                    "portal_link": portal_link
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("visit_summary")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("visit_summary")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send visit summary: {e}")
            raise

    async def process_prescription(self, 
                                 patient_data: PatientCommunicationData,
                                 medication_data: Dict[str, Any],
                                 workflow_id: str) -> Dict[str, Any]:
        """Process and notify about prescription"""
        try:
            # Create prescription data object
            prescription = PrescriptionData(
                prescription_id=medication_data.get("prescription_id", f"rx_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                medication_name=medication_data.get("medication_name", ""),
                medication_name_ar=medication_data.get("medication_name_ar"),
                dosage=medication_data.get("dosage", ""),
                frequency=medication_data.get("frequency", ""),
                duration=medication_data.get("duration", ""),
                instructions=medication_data.get("instructions", ""),
                instructions_ar=medication_data.get("instructions_ar"),
                pharmacy_name=medication_data.get("pharmacy_name"),
                pharmacy_phone=medication_data.get("pharmacy_phone")
            )
            
            # Store prescription in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["prescriptions"].append(prescription)
            
            # Send prescription notification
            notification_result = await self.send_prescription_notification(
                patient_data, prescription, workflow_id
            )
            
            return {
                "prescription_id": prescription.prescription_id,
                "medication_name": prescription.medication_name,
                "notification_result": notification_result
            }
            
        except Exception as e:
            logger.error(f"Failed to process prescription: {e}")
            raise

    async def send_prescription_notification(self, 
                                           patient_data: PatientCommunicationData,
                                           prescription: PrescriptionData,
                                           workflow_id: str) -> Dict[str, Any]:
        """Send prescription notification to patient"""
        try:
            # Use prescription ready template initially
            template = self.communication_service.message_templates["prescription_ready"]
            
            # Default pharmacy info if not provided
            pharmacy_name = prescription.pharmacy_name or "الصيدلية المحددة" if patient_data.preferred_language == Language.ARABIC else "Designated Pharmacy"
            pharmacy_hours = "08:00 - 22:00" if prescription.pharmacy_phone else "24/7"
            
            variables = {
                "patient_name": patient_data.patient_id,
                "pharmacy_name": pharmacy_name,
                "prescription_id": prescription.prescription_id,
                "pharmacy_hours": pharmacy_hours
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add medication details
            medication_name = prescription.medication_name_ar if patient_data.preferred_language == Language.ARABIC else prescription.medication_name
            if patient_data.preferred_language == Language.ARABIC:
                content += f"\n\nالدواء: {medication_name}\nالجرعة: {prescription.dosage}\nالتكرار: {prescription.frequency}"
                if prescription.instructions_ar:
                    content += f"\nتعليمات: {prescription.instructions_ar}"
            else:
                content += f"\n\nMedication: {medication_name}\nDosage: {prescription.dosage}\nFrequency: {prescription.frequency}"
                if prescription.instructions:
                    content += f"\nInstructions: {prescription.instructions}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "prescription_id": prescription.prescription_id,
                    "medication_name": prescription.medication_name
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send prescription notification: {e}")
            raise

    async def schedule_follow_up_reminder(self, 
                                        patient_data: PatientCommunicationData,
                                        follow_up_data: FollowUpData,
                                        workflow_id: str) -> Dict[str, Any]:
        """Schedule and send follow-up appointment reminder"""
        try:
            template = self.communication_service.message_templates["follow_up_reminder"]
            
            # Generate booking link (would integrate with actual booking system)
            booking_link = follow_up_data.booking_link or f"https://brainsait.com/booking/{patient_data.patient_id}"
            clinic_phone = "+966112345678"  # Would get from clinic settings
            
            variables = {
                "patient_name": patient_data.patient_id,
                "provider_name": follow_up_data.provider_name,
                "clinic_phone": clinic_phone,
                "booking_link": booking_link
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            # Add specific follow-up instructions if available
            if follow_up_data.instructions:
                instructions = follow_up_data.instructions_ar if patient_data.preferred_language == Language.ARABIC else follow_up_data.instructions
                if patient_data.preferred_language == Language.ARABIC:
                    content += f"\n\nتعليمات المتابعة: {instructions}"
                else:
                    content += f"\n\nFollow-up Instructions: {instructions}"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "template_id": template.template_id,
                    "follow_up_id": follow_up_data.follow_up_id,
                    "follow_up_type": follow_up_data.follow_up_type.value
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Store follow-up in workflow
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["follow_ups"].append(follow_up_data)
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("follow_up_reminder")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("follow_up_reminder")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send follow-up reminder: {e}")
            raise

    async def send_satisfaction_survey(self, 
                                     patient_data: PatientCommunicationData,
                                     appointment_data: AppointmentData,
                                     workflow_id: str) -> Dict[str, Any]:
        """Send patient satisfaction survey"""
        try:
            # Generate survey link (would integrate with actual survey system)
            survey_link = f"https://brainsait.com/survey/{patient_data.patient_id}/{appointment_data.appointment_id}"
            
            if patient_data.preferred_language == Language.ARABIC:
                subject = "استبيان رضا المريض - برينسيت للرعاية الصحية"
                content = f"عزيزي {patient_data.patient_id}، نأمل أن تكون راضياً عن زيارتك الأخيرة. يرجى قضاء دقيقتين لتقييم خدماتنا: {survey_link}"
            else:
                subject = "Patient Satisfaction Survey - BrainSAIT Healthcare"
                content = f"Dear {patient_data.patient_id}, we hope you were satisfied with your recent visit. Please take 2 minutes to rate our services: {survey_link}"
            
            channel = self.communication_service.select_communication_channel(
                patient_data, MessagePriority.LOW, [CommunicationChannel.SMS, CommunicationChannel.EMAIL]
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=MessagePriority.LOW,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "survey_link": survey_link,
                    "event_type": "satisfaction_survey"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("satisfaction_survey")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("satisfaction_survey")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send satisfaction survey: {e}")
            raise

    async def send_care_plan(self, 
                           patient_data: PatientCommunicationData,
                           care_plan_data: Dict[str, Any],
                           workflow_id: str) -> Dict[str, Any]:
        """Send detailed care plan to patient"""
        try:
            # Generate care plan document link (would integrate with document system)
            care_plan_link = f"https://brainsait.com/care-plan/{patient_data.patient_id}/{care_plan_data.get('plan_id')}"
            
            if patient_data.preferred_language == Language.ARABIC:
                subject = "خطة الرعاية الخاصة بك - برينسيت للرعاية الصحية"
                content = f"عزيزي {patient_data.patient_id}، خطة الرعاية الشخصية الخاصة بك جاهزة الآن. يمكنك الوصول إليها هنا: {care_plan_link}"
            else:
                subject = "Your Care Plan - BrainSAIT Healthcare"
                content = f"Dear {patient_data.patient_id}, your personalized care plan is now ready. You can access it here: {care_plan_link}"
            
            # Add key care points if available
            if care_plan_data.get("key_points"):
                if patient_data.preferred_language == Language.ARABIC:
                    content += "\n\nنقاط مهمة:\n"
                else:
                    content += "\n\nKey Points:\n"
                
                for point in care_plan_data["key_points"]:
                    content += f"• {point}\n"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=CommunicationChannel.EMAIL,  # Care plans typically sent via email
                language=patient_data.preferred_language,
                priority=MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "care_plan_link": care_plan_link,
                    "event_type": "care_plan_delivery"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            
            # Update workflow state
            if workflow_id in self.active_workflows:
                if result["status"] == "sent":
                    self.active_workflows[workflow_id]["completed_tasks"].append("care_plan")
                else:
                    self.active_workflows[workflow_id]["failed_tasks"].append("care_plan")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send care plan: {e}")
            raise

    async def send_billing_notification(self, 
                                      patient_data: PatientCommunicationData,
                                      billing_data: Dict[str, Any],
                                      workflow_id: str) -> Dict[str, Any]:
        """Send billing and insurance information"""
        try:
            # Generate billing statement link
            billing_link = f"https://brainsait.com/billing/{patient_data.patient_id}/{billing_data.get('statement_id')}"
            
            if patient_data.preferred_language == Language.ARABIC:
                subject = "بيان الفواتير والتأمين - برينسيت للرعاية الصحية"
                content = f"عزيزي {patient_data.patient_id}، بيان الفواتير والتأمين الخاص بزيارتك متاح الآن: {billing_link}"
            else:
                subject = "Billing and Insurance Statement - BrainSAIT Healthcare"
                content = f"Dear {patient_data.patient_id}, your billing and insurance statement for your recent visit is now available: {billing_link}"
            
            # Add billing summary if available
            if billing_data.get("total_amount"):
                if patient_data.preferred_language == Language.ARABIC:
                    content += f"\n\nإجمالي المبلغ: {billing_data['total_amount']} ريال سعودي"
                    if billing_data.get("insurance_covered"):
                        content += f"\nمغطى بالتأمين: {billing_data['insurance_covered']} ريال سعودي"
                    if billing_data.get("patient_responsibility"):
                        content += f"\nمسؤولية المريض: {billing_data['patient_responsibility']} ريال سعودي"
                else:
                    content += f"\n\nTotal Amount: {billing_data['total_amount']} SAR"
                    if billing_data.get("insurance_covered"):
                        content += f"\nInsurance Covered: {billing_data['insurance_covered']} SAR"
                    if billing_data.get("patient_responsibility"):
                        content += f"\nPatient Responsibility: {billing_data['patient_responsibility']} SAR"
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=CommunicationChannel.EMAIL,  # Billing typically sent via email
                language=patient_data.preferred_language,
                priority=MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "billing_link": billing_link,
                    "event_type": "billing_notification"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send billing notification: {e}")
            raise

    async def update_prescription_status(self, 
                                       workflow_id: str,
                                       prescription_id: str,
                                       new_status: PrescriptionStatus,
                                       notification_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update prescription status and notify patient if needed"""
        try:
            if workflow_id not in self.active_workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.active_workflows[workflow_id]
            
            # Find and update prescription
            prescription_updated = False
            for prescription in workflow["prescriptions"]:
                if prescription.prescription_id == prescription_id:
                    prescription.status = new_status
                    prescription_updated = True
                    break
            
            if not prescription_updated:
                raise ValueError(f"Prescription {prescription_id} not found in workflow")
            
            # Send notification based on status
            if new_status == PrescriptionStatus.READY_FOR_PICKUP and notification_data:
                pickup_notification = await self.send_prescription_pickup_notification(
                    workflow["patient_data"], prescription, notification_data
                )
                return {
                    "status": "updated",
                    "prescription_id": prescription_id,
                    "new_status": new_status.value,
                    "notification_sent": pickup_notification
                }
            
            return {
                "status": "updated",
                "prescription_id": prescription_id,
                "new_status": new_status.value,
                "notification_sent": False
            }
            
        except Exception as e:
            logger.error(f"Failed to update prescription status: {e}")
            raise

    async def send_prescription_pickup_notification(self, 
                                                  patient_data: PatientCommunicationData,
                                                  prescription: PrescriptionData,
                                                  notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send prescription ready for pickup notification"""
        try:
            template = self.communication_service.message_templates["prescription_ready"]
            
            variables = {
                "patient_name": patient_data.patient_id,
                "pharmacy_name": notification_data.get("pharmacy_name", prescription.pharmacy_name),
                "prescription_id": prescription.prescription_id,
                "pharmacy_hours": notification_data.get("pharmacy_hours", "08:00 - 22:00")
            }
            
            channel = self.communication_service.select_communication_channel(
                patient_data, template.priority, template.channels
            )
            
            subject, content = self.communication_service.render_message_template(
                template, patient_data.preferred_language, variables
            )
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.POST_VISIT,
                patient_id=patient_data.patient_id,
                channel=channel,
                language=patient_data.preferred_language,
                priority=template.priority,
                subject=subject,
                message_content=content,
                metadata={
                    "prescription_id": prescription.prescription_id,
                    "event_type": "prescription_pickup_notification"
                }
            )
            
            result = await self.communication_service.send_message(patient_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send prescription pickup notification: {e}")
            raise

    async def _schedule_workflow_tasks(self, 
                                     workflow_id: str,
                                     patient_data: PatientCommunicationData,
                                     schedule: Dict[str, datetime]) -> List[str]:
        """Schedule future workflow tasks (placeholder for task scheduler integration)"""
        # In a production system, this would integrate with a task scheduler like Celery
        scheduled_tasks = []
        
        now = datetime.now()
        
        for task_name, scheduled_time in schedule.items():
            if scheduled_time > now:
                # Schedule task (would use actual task scheduler)
                task_id = f"{workflow_id}_{task_name}_{scheduled_time.isoformat()}"
                scheduled_tasks.append(task_id)
                logger.info(f"Scheduled post-visit task {task_name} for {scheduled_time}")
        
        return scheduled_tasks

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a post-visit workflow"""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found"}
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "visit_id": workflow["post_visit_data"].visit_id,
            "created_at": workflow["created_at"].isoformat(),
            "completed_tasks": workflow["completed_tasks"],
            "failed_tasks": workflow["failed_tasks"],
            "prescriptions_count": len(workflow["prescriptions"]),
            "follow_ups_count": len(workflow["follow_ups"])
        }

    async def complete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Mark post-visit workflow as completed"""
        try:
            if workflow_id not in self.active_workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now()
            
            logger.info(f"Post-visit workflow {workflow_id} completed")
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "completed_tasks": workflow["completed_tasks"],
                "failed_tasks": workflow["failed_tasks"]
            }
            
        except Exception as e:
            logger.error(f"Failed to complete workflow {workflow_id}: {e}")
            raise