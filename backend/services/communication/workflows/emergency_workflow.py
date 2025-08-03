"""
BrainSAIT Healthcare Platform - Emergency Communication Protocols
Comprehensive emergency communication system with automated escalation and crisis management

This workflow handles:
1. Medical emergencies with immediate provider and emergency contact notifications
2. Facility emergencies (evacuation, system failures, security incidents)
3. Critical patient alerts (code blue, rapid response, patient missing)
4. Mass notification events (disease outbreaks, natural disasters)
5. Provider emergency notifications (on-call alerts, urgent consultations)
6. Automated escalation chains with multiple contact attempts
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum

from ..patient_communication_service import (
    PatientCommunicationService, PatientCommunicationData,
    CommunicationMessage, MessagePriority, WorkflowType, Language, CommunicationChannel
)

logger = logging.getLogger(__name__)

class EmergencyType(str, Enum):
    """Types of emergency situations"""
    MEDICAL_EMERGENCY = "medical_emergency"
    CODE_BLUE = "code_blue"
    RAPID_RESPONSE = "rapid_response"
    MISSING_PATIENT = "missing_patient"
    FACILITY_EMERGENCY = "facility_emergency"
    FIRE_EMERGENCY = "fire_emergency"
    SECURITY_INCIDENT = "security_incident"
    SYSTEM_FAILURE = "system_failure"
    MASS_CASUALTY = "mass_casualty"
    INFECTIOUS_OUTBREAK = "infectious_outbreak"
    NATURAL_DISASTER = "natural_disaster"
    PROVIDER_EMERGENCY = "provider_emergency"

class EmergencyLevel(str, Enum):
    """Emergency severity levels"""
    LEVEL_1 = "level_1"  # Critical - Life threatening
    LEVEL_2 = "level_2"  # Urgent - Serious condition
    LEVEL_3 = "level_3"  # Moderate - Needs attention
    LEVEL_4 = "level_4"  # Low - Non-urgent

class NotificationTier(str, Enum):
    """Emergency notification tiers"""
    IMMEDIATE = "immediate"      # 0-5 minutes
    PRIMARY = "primary"          # 5-15 minutes
    SECONDARY = "secondary"      # 15-30 minutes
    ADMINISTRATIVE = "administrative"  # 30+ minutes

class ContactRole(str, Enum):
    """Emergency contact roles"""
    EMERGENCY_CONTACT = "emergency_contact"
    PRIMARY_PHYSICIAN = "primary_physician"
    ON_CALL_PHYSICIAN = "on_call_physician"
    NURSE_SUPERVISOR = "nurse_supervisor"
    SECURITY = "security"
    ADMINISTRATION = "administration"
    EMERGENCY_COORDINATOR = "emergency_coordinator"

@dataclass
class EmergencyContact:
    """Emergency contact information"""
    contact_id: str
    name: str
    name_ar: Optional[str] = None
    role: ContactRole = ContactRole.EMERGENCY_CONTACT
    phone_number: str
    backup_phone: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Language = Language.ENGLISH
    notification_preferences: List[CommunicationChannel] = field(default_factory=lambda: [CommunicationChannel.VOICE, CommunicationChannel.SMS])
    availability_schedule: Optional[Dict[str, Any]] = None
    priority_order: int = 1

@dataclass
class EmergencyEvent:
    """Emergency event data"""
    event_id: str
    emergency_type: EmergencyType
    emergency_level: EmergencyLevel
    patient_id: Optional[str] = None
    location: str = ""
    location_ar: Optional[str] = None
    description: str = ""
    description_ar: Optional[str] = None
    initiated_by: str = ""
    initiated_at: datetime = field(default_factory=datetime.now)
    estimated_duration: Optional[int] = None  # minutes
    affected_areas: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    contact_emergency_services: bool = False
    evacuation_required: bool = False
    external_agencies_notified: bool = False

@dataclass
class EscalationRule:
    """Escalation rule configuration"""
    tier: NotificationTier
    delay_minutes: int
    max_attempts: int
    required_acknowledgment: bool
    escalate_if_no_response: bool
    escalation_delay_minutes: int
    contact_roles: List[ContactRole]

@dataclass
class EmergencyWorkflowConfig:
    """Configuration for emergency workflows"""
    max_notification_attempts: int = 10
    voice_call_timeout_seconds: int = 30
    sms_backup_delay_seconds: int = 60
    acknowledgment_required: bool = True
    acknowledgment_timeout_minutes: int = 5
    auto_escalation_enabled: bool = True
    emergency_services_integration: bool = True

class EmergencyWorkflow:
    """
    Emergency Communication Workflow Implementation
    
    Manages critical emergency notifications with automated escalation
    """
    
    def __init__(self, communication_service: PatientCommunicationService):
        self.communication_service = communication_service
        self.config = EmergencyWorkflowConfig()
        self.active_emergencies: Dict[str, Dict] = {}
        self.escalation_rules = self._initialize_escalation_rules()
        self.emergency_contacts: Dict[str, List[EmergencyContact]] = {}
        
    def _initialize_escalation_rules(self) -> Dict[EmergencyType, List[EscalationRule]]:
        """Initialize escalation rules for different emergency types"""
        rules = {}
        
        # Medical Emergency Escalation
        rules[EmergencyType.MEDICAL_EMERGENCY] = [
            EscalationRule(
                tier=NotificationTier.IMMEDIATE,
                delay_minutes=0,
                max_attempts=3,
                required_acknowledgment=True,
                escalate_if_no_response=True,
                escalation_delay_minutes=2,
                contact_roles=[ContactRole.PRIMARY_PHYSICIAN, ContactRole.ON_CALL_PHYSICIAN]
            ),
            EscalationRule(
                tier=NotificationTier.PRIMARY,
                delay_minutes=5,
                max_attempts=2,
                required_acknowledgment=True,
                escalate_if_no_response=True,
                escalation_delay_minutes=10,
                contact_roles=[ContactRole.NURSE_SUPERVISOR, ContactRole.EMERGENCY_COORDINATOR]
            ),
            EscalationRule(
                tier=NotificationTier.SECONDARY,
                delay_minutes=15,
                max_attempts=1,
                required_acknowledgment=False,
                escalate_if_no_response=False,
                escalation_delay_minutes=0,
                contact_roles=[ContactRole.ADMINISTRATION]
            )
        ]
        
        # Code Blue Escalation
        rules[EmergencyType.CODE_BLUE] = [
            EscalationRule(
                tier=NotificationTier.IMMEDIATE,
                delay_minutes=0,
                max_attempts=5,
                required_acknowledgment=True,
                escalate_if_no_response=True,
                escalation_delay_minutes=1,
                contact_roles=[ContactRole.ON_CALL_PHYSICIAN, ContactRole.NURSE_SUPERVISOR, ContactRole.EMERGENCY_COORDINATOR]
            )
        ]
        
        # Facility Emergency Escalation
        rules[EmergencyType.FACILITY_EMERGENCY] = [
            EscalationRule(
                tier=NotificationTier.IMMEDIATE,
                delay_minutes=0,
                max_attempts=3,
                required_acknowledgment=True,
                escalate_if_no_response=True,
                escalation_delay_minutes=5,
                contact_roles=[ContactRole.SECURITY, ContactRole.EMERGENCY_COORDINATOR]
            ),
            EscalationRule(
                tier=NotificationTier.PRIMARY,
                delay_minutes=5,
                max_attempts=2,
                required_acknowledgment=True,
                escalate_if_no_response=False,
                escalation_delay_minutes=0,
                contact_roles=[ContactRole.ADMINISTRATION]
            )
        ]
        
        return rules

    async def initiate_emergency_workflow(self, 
                                        emergency_event: EmergencyEvent,
                                        emergency_contacts: List[EmergencyContact],
                                        patient_data: Optional[PatientCommunicationData] = None) -> Dict[str, Any]:
        """
        Initiate emergency workflow with immediate notifications and escalation
        
        Args:
            emergency_event: Emergency event details
            emergency_contacts: List of emergency contacts to notify
            patient_data: Patient data if emergency is patient-specific
            
        Returns:
            Emergency workflow initiation result
        """
        try:
            workflow_id = f"emergency_{emergency_event.event_id}"
            
            # Store emergency contacts for this workflow
            self.emergency_contacts[workflow_id] = emergency_contacts
            
            # Create workflow state
            workflow_state = {
                "workflow_id": workflow_id,
                "emergency_event": emergency_event,
                "patient_data": patient_data,
                "emergency_contacts": emergency_contacts,
                "status": "active",
                "notifications_sent": [],
                "acknowledgments_received": [],
                "escalations": [],
                "resolution_time": None,
                "created_at": datetime.now()
            }
            
            self.active_emergencies[workflow_id] = workflow_state
            
            # Get escalation rules for this emergency type
            escalation_rules = self.escalation_rules.get(
                emergency_event.emergency_type, 
                self.escalation_rules[EmergencyType.MEDICAL_EMERGENCY]  # Default
            )
            
            # Start immediate notifications
            immediate_notifications = await self._execute_notification_tier(
                workflow_id, emergency_event, NotificationTier.IMMEDIATE, escalation_rules
            )
            
            # Schedule escalation tiers
            scheduled_escalations = await self._schedule_escalation_tiers(
                workflow_id, escalation_rules
            )
            
            # Handle special emergency types
            special_actions = await self._handle_special_emergency_actions(
                emergency_event, workflow_id
            )
            
            logger.critical(f"Emergency workflow initiated: {emergency_event.emergency_type.value} - {emergency_event.event_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "initiated",
                "emergency_type": emergency_event.emergency_type.value,
                "emergency_level": emergency_event.emergency_level.value,
                "immediate_notifications": immediate_notifications,
                "scheduled_escalations": scheduled_escalations,
                "special_actions": special_actions
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate emergency workflow: {e}")
            raise

    async def _execute_notification_tier(self, 
                                       workflow_id: str,
                                       emergency_event: EmergencyEvent,
                                       tier: NotificationTier,
                                       escalation_rules: List[EscalationRule]) -> List[Dict[str, Any]]:
        """Execute notifications for a specific tier"""
        try:
            # Get the rule for this tier
            tier_rule = next((rule for rule in escalation_rules if rule.tier == tier), None)
            if not tier_rule:
                return []
            
            # Get contacts for required roles
            contacts_to_notify = []
            for contact in self.emergency_contacts[workflow_id]:
                if contact.role in tier_rule.contact_roles:
                    contacts_to_notify.append(contact)
            
            # Sort by priority order
            contacts_to_notify.sort(key=lambda x: x.priority_order)
            
            # Send notifications
            notification_results = []
            for contact in contacts_to_notify:
                notification_result = await self.send_emergency_notification(
                    contact, emergency_event, workflow_id, tier
                )
                notification_results.append(notification_result)
                
                # Small delay between notifications to avoid overwhelming systems
                await asyncio.sleep(0.5)
            
            return notification_results
            
        except Exception as e:
            logger.error(f"Failed to execute notification tier {tier.value}: {e}")
            raise

    async def send_emergency_notification(self, 
                                        contact: EmergencyContact,
                                        emergency_event: EmergencyEvent,
                                        workflow_id: str,
                                        tier: NotificationTier) -> Dict[str, Any]:
        """Send emergency notification to a specific contact"""
        try:
            # Determine notification channels based on emergency level
            if emergency_event.emergency_level == EmergencyLevel.LEVEL_1:
                # Critical emergencies prefer voice calls
                preferred_channels = [CommunicationChannel.VOICE, CommunicationChannel.SMS]
            else:
                # Use contact preferences
                preferred_channels = contact.notification_preferences
            
            # Create emergency message content
            if contact.preferred_language == Language.ARABIC:
                subject = f"تنبيه طوارئ - {emergency_event.emergency_type.value} - برينسيت للرعاية الصحية"
                content = self._create_arabic_emergency_content(emergency_event, contact)
            else:
                subject = f"EMERGENCY ALERT - {emergency_event.emergency_type.value} - BrainSAIT Healthcare"
                content = self._create_english_emergency_content(emergency_event, contact)
            
            # Try multiple channels if needed
            notification_results = []
            for channel in preferred_channels[:2]:  # Try first 2 preferred channels
                message = CommunicationMessage(
                    workflow_type=WorkflowType.EMERGENCY,
                    patient_id=contact.contact_id,
                    channel=channel,
                    language=contact.preferred_language,
                    priority=MessagePriority.CRITICAL,
                    subject=subject,
                    message_content=content,
                    metadata={
                        "workflow_id": workflow_id,
                        "emergency_type": emergency_event.emergency_type.value,
                        "emergency_level": emergency_event.emergency_level.value,
                        "contact_role": contact.role.value,
                        "tier": tier.value,
                        "requires_acknowledgment": True
                    }
                )
                
                # Create contact communication data
                contact_comm_data = PatientCommunicationData(
                    patient_id=contact.contact_id,
                    phone_number=contact.phone_number,
                    email=contact.email,
                    preferred_language=contact.preferred_language,
                    preferred_channels=contact.notification_preferences
                )
                
                result = await self.communication_service.send_message(contact_comm_data, message)
                notification_results.append(result)
                
                # If voice call, wait a moment then send SMS backup
                if channel == CommunicationChannel.VOICE:
                    await asyncio.sleep(self.config.sms_backup_delay_seconds)
                    if len(preferred_channels) > 1 and preferred_channels[1] == CommunicationChannel.SMS:
                        sms_message = CommunicationMessage(
                            workflow_type=WorkflowType.EMERGENCY,
                            patient_id=contact.contact_id,
                            channel=CommunicationChannel.SMS,
                            language=contact.preferred_language,
                            priority=MessagePriority.CRITICAL,
                            subject=subject,
                            message_content=content,
                            metadata={
                                "workflow_id": workflow_id,
                                "backup_for": "voice_call",
                                "emergency_type": emergency_event.emergency_type.value
                            }
                        )
                        
                        sms_result = await self.communication_service.send_message(contact_comm_data, sms_message)
                        notification_results.append(sms_result)
                
                # Break if successful
                if result["status"] == "sent":
                    break
            
            # Store notification in workflow
            if workflow_id in self.active_emergencies:
                self.active_emergencies[workflow_id]["notifications_sent"].append({
                    "contact_id": contact.contact_id,
                    "contact_role": contact.role.value,
                    "tier": tier.value,
                    "timestamp": datetime.now().isoformat(),
                    "results": notification_results
                })
            
            return {
                "contact_id": contact.contact_id,
                "contact_role": contact.role.value,
                "notification_results": notification_results,
                "success": any(r["status"] == "sent" for r in notification_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to send emergency notification to {contact.contact_id}: {e}")
            raise

    def _create_english_emergency_content(self, emergency_event: EmergencyEvent, contact: EmergencyContact) -> str:
        """Create emergency notification content in English"""
        content = f"EMERGENCY ALERT\n\n"
        content += f"Type: {emergency_event.emergency_type.value.replace('_', ' ').title()}\n"
        content += f"Level: {emergency_event.emergency_level.value.replace('_', ' ').title()}\n"
        content += f"Location: {emergency_event.location}\n"
        content += f"Time: {emergency_event.initiated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if emergency_event.patient_id:
            content += f"Patient ID: {emergency_event.patient_id}\n"
        
        content += f"\nDescription: {emergency_event.description}\n"
        
        if emergency_event.required_actions:
            content += "\nRequired Actions:\n"
            for action in emergency_event.required_actions:
                content += f"• {action}\n"
        
        if emergency_event.contact_emergency_services:
            content += "\n⚠️ EMERGENCY SERVICES HAVE BEEN CONTACTED\n"
        
        if emergency_event.evacuation_required:
            content += "\n🚨 EVACUATION REQUIRED - FOLLOW EVACUATION PROCEDURES\n"
        
        content += "\nPlease acknowledge receipt of this alert immediately."
        content += "\nFor urgent response, call: +966112345678"
        
        return content

    def _create_arabic_emergency_content(self, emergency_event: EmergencyEvent, contact: EmergencyContact) -> str:
        """Create emergency notification content in Arabic"""
        content = f"تنبيه طوارئ\n\n"
        
        # Emergency type translations
        emergency_type_ar = {
            "medical_emergency": "طوارئ طبية",
            "code_blue": "كود أزرق",
            "rapid_response": "استجابة سريعة",
            "missing_patient": "مريض مفقود",
            "facility_emergency": "طوارئ المنشأة",
            "fire_emergency": "طوارئ حريق",
            "security_incident": "حادث أمني",
            "system_failure": "عطل في النظام",
            "mass_casualty": "إصابات جماعية",
            "infectious_outbreak": "تفشي عدوى",
            "natural_disaster": "كارثة طبيعية"
        }
        
        content += f"النوع: {emergency_type_ar.get(emergency_event.emergency_type.value, emergency_event.emergency_type.value)}\n"
        content += f"المستوى: {emergency_event.emergency_level.value}\n"
        content += f"الموقع: {emergency_event.location_ar or emergency_event.location}\n"
        content += f"الوقت: {emergency_event.initiated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if emergency_event.patient_id:
            content += f"رقم المريض: {emergency_event.patient_id}\n"
        
        content += f"\nالوصف: {emergency_event.description_ar or emergency_event.description}\n"
        
        if emergency_event.required_actions:
            content += "\nالإجراءات المطلوبة:\n"
            for action in emergency_event.required_actions:
                content += f"• {action}\n"
        
        if emergency_event.contact_emergency_services:
            content += "\n⚠️ تم الاتصال بخدمات الطوارئ\n"
        
        if emergency_event.evacuation_required:
            content += "\n🚨 مطلوب إخلاء - اتبع إجراءات الإخلاء\n"
        
        content += "\nيرجى تأكيد استلام هذا التنبيه فوراً."
        content += "\nللاستجابة العاجلة، اتصل على: +966112345678"
        
        return content

    async def _handle_special_emergency_actions(self, 
                                              emergency_event: EmergencyEvent,
                                              workflow_id: str) -> List[str]:
        """Handle special actions for specific emergency types"""
        special_actions = []
        
        try:
            # Code Blue - Mass notification
            if emergency_event.emergency_type == EmergencyType.CODE_BLUE:
                # Send facility-wide alert
                facility_alert = await self.send_facility_wide_alert(
                    emergency_event, workflow_id
                )
                special_actions.append("facility_wide_alert_sent")
            
            # Missing Patient - Security and administration alerts
            elif emergency_event.emergency_type == EmergencyType.MISSING_PATIENT:
                # Notify security immediately
                security_alert = await self.notify_security_team(
                    emergency_event, workflow_id
                )
                special_actions.append("security_team_notified")
            
            # Fire Emergency - Evacuation procedures
            elif emergency_event.emergency_type == EmergencyType.FIRE_EMERGENCY:
                # Trigger evacuation notifications
                evacuation_alert = await self.trigger_evacuation_notifications(
                    emergency_event, workflow_id
                )
                special_actions.append("evacuation_notifications_sent")
            
            # Infectious Outbreak - CDC and health department notifications
            elif emergency_event.emergency_type == EmergencyType.INFECTIOUS_OUTBREAK:
                # Notify health authorities
                health_dept_notification = await self.notify_health_authorities(
                    emergency_event, workflow_id
                )
                special_actions.append("health_authorities_notified")
            
            # System Failure - IT and operations teams
            elif emergency_event.emergency_type == EmergencyType.SYSTEM_FAILURE:
                # Notify IT emergency response
                it_notification = await self.notify_it_emergency_team(
                    emergency_event, workflow_id
                )
                special_actions.append("it_emergency_team_notified")
            
        except Exception as e:
            logger.error(f"Failed to handle special emergency actions: {e}")
            special_actions.append(f"error: {str(e)}")
        
        return special_actions

    async def send_facility_wide_alert(self, 
                                     emergency_event: EmergencyEvent,
                                     workflow_id: str) -> Dict[str, Any]:
        """Send facility-wide emergency alert"""
        try:
            # This would integrate with facility PA system, digital displays, etc.
            logger.critical(f"FACILITY-WIDE ALERT: {emergency_event.emergency_type.value} at {emergency_event.location}")
            
            # Simulate sending to facility communication systems
            return {
                "status": "sent",
                "systems": ["PA_system", "digital_displays", "mobile_app_push"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send facility-wide alert: {e}")
            raise

    async def notify_security_team(self, 
                                 emergency_event: EmergencyEvent,
                                 workflow_id: str) -> Dict[str, Any]:
        """Notify security team for specific emergencies"""
        try:
            # This would notify security personnel
            logger.critical(f"SECURITY ALERT: {emergency_event.emergency_type.value}")
            
            return {
                "status": "notified",
                "security_personnel": ["chief_security", "duty_officer"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to notify security team: {e}")
            raise

    async def trigger_evacuation_notifications(self, 
                                             emergency_event: EmergencyEvent,
                                             workflow_id: str) -> Dict[str, Any]:
        """Trigger evacuation notifications and procedures"""
        try:
            # This would trigger building evacuation systems
            logger.critical(f"EVACUATION TRIGGERED: {emergency_event.location}")
            
            return {
                "status": "triggered",
                "systems": ["fire_alarm", "PA_announcement", "emergency_lighting"],
                "affected_areas": emergency_event.affected_areas,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger evacuation notifications: {e}")
            raise

    async def notify_health_authorities(self, 
                                      emergency_event: EmergencyEvent,
                                      workflow_id: str) -> Dict[str, Any]:
        """Notify health authorities for infectious disease outbreaks"""
        try:
            # This would notify MOH, CDC equivalent, etc.
            logger.critical(f"HEALTH AUTHORITIES NOTIFIED: {emergency_event.emergency_type.value}")
            
            return {
                "status": "notified",
                "authorities": ["ministry_of_health", "cdc_saudi", "who_representative"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to notify health authorities: {e}")
            raise

    async def notify_it_emergency_team(self, 
                                     emergency_event: EmergencyEvent,
                                     workflow_id: str) -> Dict[str, Any]:
        """Notify IT emergency response team"""
        try:
            # This would notify IT emergency response team
            logger.critical(f"IT EMERGENCY: {emergency_event.description}")
            
            return {
                "status": "notified",
                "teams": ["it_emergency_response", "systems_admin", "network_team"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to notify IT emergency team: {e}")
            raise

    async def receive_acknowledgment(self, 
                                   workflow_id: str,
                                   contact_id: str,
                                   acknowledgment_message: Optional[str] = None) -> Dict[str, Any]:
        """Record acknowledgment from emergency contact"""
        try:
            if workflow_id not in self.active_emergencies:
                raise ValueError(f"Emergency workflow {workflow_id} not found")
            
            workflow = self.active_emergencies[workflow_id]
            
            acknowledgment = {
                "contact_id": contact_id,
                "timestamp": datetime.now().isoformat(),
                "message": acknowledgment_message,
                "response_time_seconds": (datetime.now() - datetime.fromisoformat(workflow["created_at"].isoformat())).total_seconds()
            }
            
            workflow["acknowledgments_received"].append(acknowledgment)
            
            logger.info(f"Emergency acknowledgment received from {contact_id} for {workflow_id}")
            
            return {
                "status": "acknowledged",
                "contact_id": contact_id,
                "response_time": acknowledgment["response_time_seconds"]
            }
            
        except Exception as e:
            logger.error(f"Failed to record acknowledgment: {e}")
            raise

    async def escalate_emergency(self, 
                               workflow_id: str,
                               reason: str = "no_acknowledgment") -> Dict[str, Any]:
        """Escalate emergency to next tier"""
        try:
            if workflow_id not in self.active_emergencies:
                raise ValueError(f"Emergency workflow {workflow_id} not found")
            
            workflow = self.active_emergencies[workflow_id]
            emergency_event = workflow["emergency_event"]
            
            # Determine next escalation tier
            escalation_rules = self.escalation_rules.get(
                emergency_event.emergency_type,
                self.escalation_rules[EmergencyType.MEDICAL_EMERGENCY]
            )
            
            # Find next tier to escalate to
            current_escalations = len(workflow["escalations"])
            if current_escalations < len(escalation_rules):
                next_rule = escalation_rules[current_escalations]
                
                # Execute escalation
                escalation_result = await self._execute_notification_tier(
                    workflow_id, emergency_event, next_rule.tier, escalation_rules
                )
                
                # Record escalation
                escalation = {
                    "tier": next_rule.tier.value,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "result": escalation_result
                }
                
                workflow["escalations"].append(escalation)
                
                logger.warning(f"Emergency escalated to {next_rule.tier.value} for {workflow_id}")
                
                return {
                    "status": "escalated",
                    "new_tier": next_rule.tier.value,
                    "reason": reason,
                    "escalation_result": escalation_result
                }
            else:
                logger.critical(f"Maximum escalation reached for emergency {workflow_id}")
                return {
                    "status": "max_escalation_reached",
                    "final_tier": escalation_rules[-1].tier.value
                }
            
        except Exception as e:
            logger.error(f"Failed to escalate emergency: {e}")
            raise

    async def resolve_emergency(self, 
                              workflow_id: str,
                              resolution_notes: str,
                              resolved_by: str) -> Dict[str, Any]:
        """Mark emergency as resolved"""
        try:
            if workflow_id not in self.active_emergencies:
                raise ValueError(f"Emergency workflow {workflow_id} not found")
            
            workflow = self.active_emergencies[workflow_id]
            workflow["status"] = "resolved"
            workflow["resolution_time"] = datetime.now()
            workflow["resolution_notes"] = resolution_notes
            workflow["resolved_by"] = resolved_by
            
            # Calculate total response time
            total_response_time = (datetime.now() - workflow["created_at"]).total_seconds()
            
            # Send resolution notifications to key contacts
            resolution_notifications = await self.send_resolution_notifications(
                workflow_id, resolution_notes, total_response_time
            )
            
            logger.info(f"Emergency {workflow_id} resolved by {resolved_by}")
            
            return {
                "status": "resolved",
                "workflow_id": workflow_id,
                "resolution_time": workflow["resolution_time"].isoformat(),
                "total_response_time_seconds": total_response_time,
                "resolved_by": resolved_by,
                "resolution_notifications": resolution_notifications
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve emergency: {e}")
            raise

    async def send_resolution_notifications(self, 
                                          workflow_id: str,
                                          resolution_notes: str,
                                          total_response_time: float) -> List[Dict[str, Any]]:
        """Send notifications when emergency is resolved"""
        try:
            workflow = self.active_emergencies[workflow_id]
            emergency_event = workflow["emergency_event"]
            
            # Notify all contacts who were notified during the emergency
            notified_contacts = set()
            for notification in workflow["notifications_sent"]:
                notified_contacts.add(notification["contact_id"])
            
            resolution_notifications = []
            for contact_id in notified_contacts:
                # Find contact details
                contact = next((c for c in workflow["emergency_contacts"] if c.contact_id == contact_id), None)
                if contact:
                    notification_result = await self.send_resolution_notification(
                        contact, emergency_event, resolution_notes, total_response_time, workflow_id
                    )
                    resolution_notifications.append(notification_result)
            
            return resolution_notifications
            
        except Exception as e:
            logger.error(f"Failed to send resolution notifications: {e}")
            return []

    async def send_resolution_notification(self, 
                                         contact: EmergencyContact,
                                         emergency_event: EmergencyEvent,
                                         resolution_notes: str,
                                         response_time: float,
                                         workflow_id: str) -> Dict[str, Any]:
        """Send resolution notification to a specific contact"""
        try:
            if contact.preferred_language == Language.ARABIC:
                subject = f"حُل الطارئ - {emergency_event.emergency_type.value} - برينسيت للرعاية الصحية"
                content = f"تم حل الطارئ: {emergency_event.emergency_type.value}\n"
                content += f"الموقع: {emergency_event.location_ar or emergency_event.location}\n"
                content += f"وقت الاستجابة: {int(response_time/60)} دقيقة\n"
                content += f"ملاحظات الحل: {resolution_notes}\n"
                content += "شكراً لاستجابتكم السريعة."
            else:
                subject = f"Emergency Resolved - {emergency_event.emergency_type.value} - BrainSAIT Healthcare"
                content = f"Emergency resolved: {emergency_event.emergency_type.value}\n"
                content += f"Location: {emergency_event.location}\n"
                content += f"Response time: {int(response_time/60)} minutes\n"
                content += f"Resolution notes: {resolution_notes}\n"
                content += "Thank you for your prompt response."
            
            message = CommunicationMessage(
                workflow_type=WorkflowType.EMERGENCY,
                patient_id=contact.contact_id,
                channel=CommunicationChannel.SMS,  # Resolution notifications typically via SMS
                language=contact.preferred_language,
                priority=MessagePriority.NORMAL,
                subject=subject,
                message_content=content,
                metadata={
                    "workflow_id": workflow_id,
                    "event_type": "emergency_resolution",
                    "response_time": response_time
                }
            )
            
            # Create contact communication data
            contact_comm_data = PatientCommunicationData(
                patient_id=contact.contact_id,
                phone_number=contact.phone_number,
                email=contact.email,
                preferred_language=contact.preferred_language,
                preferred_channels=[CommunicationChannel.SMS]
            )
            
            result = await self.communication_service.send_message(contact_comm_data, message)
            return result
            
        except Exception as e:
            logger.error(f"Failed to send resolution notification: {e}")
            raise

    async def _schedule_escalation_tiers(self, 
                                       workflow_id: str,
                                       escalation_rules: List[EscalationRule]) -> List[str]:
        """Schedule automatic escalation tiers"""
        # In a production system, this would integrate with a task scheduler
        scheduled_escalations = []
        
        for i, rule in enumerate(escalation_rules[1:], 1):  # Skip immediate tier
            if rule.escalate_if_no_response:
                escalation_time = datetime.now() + timedelta(minutes=rule.delay_minutes)
                task_id = f"{workflow_id}_escalation_{rule.tier.value}_{escalation_time.isoformat()}"
                scheduled_escalations.append(task_id)
                logger.info(f"Scheduled escalation to {rule.tier.value} at {escalation_time}")
        
        return scheduled_escalations

    async def get_emergency_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current emergency status"""
        if workflow_id not in self.active_emergencies:
            return {"status": "not_found"}
        
        workflow = self.active_emergencies[workflow_id]
        emergency_event = workflow["emergency_event"]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "emergency_type": emergency_event.emergency_type.value,
            "emergency_level": emergency_event.emergency_level.value,
            "location": emergency_event.location,
            "created_at": workflow["created_at"].isoformat(),
            "notifications_sent": len(workflow["notifications_sent"]),
            "acknowledgments_received": len(workflow["acknowledgments_received"]),
            "escalations": len(workflow["escalations"]),
            "resolution_time": workflow.get("resolution_time").isoformat() if workflow.get("resolution_time") else None
        }

    async def get_active_emergencies(self) -> List[Dict[str, Any]]:
        """Get all active emergency workflows"""
        active_emergencies = []
        
        for workflow_id, workflow in self.active_emergencies.items():
            if workflow["status"] == "active":
                emergency_event = workflow["emergency_event"]
                active_emergencies.append({
                    "workflow_id": workflow_id,
                    "emergency_type": emergency_event.emergency_type.value,
                    "emergency_level": emergency_event.emergency_level.value,
                    "location": emergency_event.location,
                    "patient_id": emergency_event.patient_id,
                    "created_at": workflow["created_at"].isoformat(),
                    "time_elapsed_minutes": (datetime.now() - workflow["created_at"]).total_seconds() / 60,
                    "acknowledgments_received": len(workflow["acknowledgments_received"])
                })
        
        return active_emergencies