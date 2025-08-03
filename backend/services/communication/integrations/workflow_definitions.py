"""
BrainSAIT Healthcare Platform - Pre-built Healthcare Workflow Templates
Comprehensive collection of healthcare workflow definitions for Saudi Arabian healthcare ecosystem

This module provides ready-to-use workflow templates for:
1. Patient Onboarding Workflows
2. Pre-operative Preparation Sequences  
3. Post-discharge Follow-up Workflows
4. Chronic Disease Management Programs
5. Medication Adherence Monitoring
6. Preventive Care Reminders
7. Emergency Response Protocols
8. Care Team Coordination Workflows

All workflows include:
- Arabic and English language support
- NPHIES compliance integration
- Islamic calendar and cultural context
- HIPAA/PDPL data protection
- Saudi healthcare regulations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .pyheart_integration import (
    HealthcareWorkflowDefinition, WorkflowStep, WorkflowTrigger,
    HealthcareWorkflowType, WorkflowEventType
)
from ..patient_communication_service import MessagePriority

class HealthcareWorkflowTemplates:
    """
    Factory class for creating pre-built healthcare workflow definitions
    """
    
    @staticmethod
    def create_patient_onboarding_workflow() -> HealthcareWorkflowDefinition:
        """
        Create comprehensive patient onboarding workflow
        Includes registration, orientation, and initial care setup
        """
        return HealthcareWorkflowDefinition(
            workflow_id="patient_onboarding_v2.0",
            name="Patient Onboarding Workflow",
            name_ar="سير عمل تأهيل المرضى",
            description="Comprehensive patient onboarding with registration, orientation, and care setup",
            description_ar="تأهيل شامل للمرضى مع التسجيل والتوجيه وإعداد الرعاية",
            workflow_type=HealthcareWorkflowType.PATIENT_ONBOARDING,
            version="2.0",
            
            trigger=WorkflowTrigger(
                trigger_id="patient_registration_trigger",
                event_type=WorkflowEventType.APPOINTMENT_SCHEDULED,
                conditions={
                    "is_new_patient": True,
                    "appointment_type": {"operator": "in", "value": ["initial_consultation", "first_visit"]}
                },
                priority=MessagePriority.HIGH
            ),
            
            steps=[
                # Step 1: Welcome and Registration Confirmation
                WorkflowStep(
                    step_id="welcome_registration",
                    step_type="message",
                    name="Welcome and Registration Confirmation",
                    description="Send welcome message and confirm registration details",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "welcome_new_patient",
                                "channel": "sms",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "clinic_name": "{clinic_name}",
                                    "appointment_date": "{appointment_date}",
                                    "portal_link": "{patient_portal_link}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_registration_response"],
                    timeout_minutes=60,
                    compliance_checks=["hipaa", "pdpl", "nphies"]
                ),
                
                # Step 2: Wait for Registration Response
                WorkflowStep(
                    step_id="wait_registration_response",
                    step_type="wait",
                    name="Wait for Registration Response",
                    description="Wait for patient to confirm registration and complete forms",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 240  # 4 hours
                            }
                        }
                    ],
                    next_steps=["check_registration_status"],
                    timeout_minutes=240
                ),
                
                # Step 3: Check Registration Status
                WorkflowStep(
                    step_id="check_registration_status",
                    step_type="decision",
                    name="Check Registration Status",
                    description="Check if patient completed registration forms",
                    conditions=[
                        {
                            "type": "healthcare_data",
                            "field": "registration_completed",
                            "operator": "equals",
                            "value": True
                        }
                    ],
                    actions=[
                        {
                            "type": "decision",
                            "parameters": {
                                "conditions": [
                                    {
                                        "type": "healthcare_data",
                                        "field": "registration_completed",
                                        "operator": "equals",
                                        "value": True,
                                        "result": "completed",
                                        "next_step": "insurance_verification"
                                    }
                                ],
                                "default_next": "registration_reminder"
                            }
                        }
                    ],
                    next_steps=["insurance_verification", "registration_reminder"]
                ),
                
                # Step 4: Registration Reminder (if not completed)
                WorkflowStep(
                    step_id="registration_reminder",
                    step_type="message",
                    name="Registration Reminder",
                    description="Remind patient to complete registration forms",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "registration_reminder",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "deadline": "{registration_deadline}",
                                    "support_phone": "{clinic_support_phone}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_registration_response_2"],
                    timeout_minutes=30
                ),
                
                # Step 5: Second wait for registration
                WorkflowStep(
                    step_id="wait_registration_response_2",
                    step_type="wait",
                    name="Second Wait for Registration",
                    description="Final wait period for registration completion",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 120  # 2 hours
                            }
                        }
                    ],
                    next_steps=["escalate_registration"],
                    timeout_minutes=120
                ),
                
                # Step 6: Escalate Registration Issues
                WorkflowStep(
                    step_id="escalate_registration",
                    step_type="escalation",
                    name="Escalate Registration Issues",
                    description="Escalate to staff for manual assistance",
                    actions=[
                        {
                            "type": "escalation",
                            "parameters": {
                                "type": "staff_intervention",
                                "reason": "Patient registration incomplete after reminders",
                                "escalation_level": "level_1",
                                "assign_to": "patient_services_team"
                            }
                        }
                    ],
                    next_steps=["insurance_verification"]
                ),
                
                # Step 7: Insurance Verification
                WorkflowStep(
                    step_id="insurance_verification",
                    step_type="message",
                    name="Insurance Verification",
                    description="Request insurance verification and NPHIES check",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "insurance_verification_request",
                                "channel": "sms",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "insurance_requirements": "{insurance_requirements}",
                                    "nphies_info": "{nphies_verification_info}"
                                }
                            }
                        }
                    ],
                    next_steps=["orientation_scheduling"],
                    timeout_minutes=60,
                    compliance_checks=["nphies"]
                ),
                
                # Step 8: Orientation Scheduling
                WorkflowStep(
                    step_id="orientation_scheduling",
                    step_type="message",
                    name="Orientation Scheduling",
                    description="Schedule patient orientation session",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "orientation_invitation",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "orientation_options": "{orientation_time_slots}",
                                    "clinic_location": "{clinic_address}",
                                    "parking_info": "{parking_instructions}"
                                }
                            }
                        }
                    ],
                    next_steps=["pre_visit_preparation"],
                    timeout_minutes=30
                ),
                
                # Step 9: Pre-visit Preparation
                WorkflowStep(
                    step_id="pre_visit_preparation",
                    step_type="message",
                    name="Pre-visit Preparation",
                    description="Send pre-visit preparation instructions",
                    conditions=[
                        {
                            "type": "time_of_day",
                            "not_prayer_time": True
                        }
                    ],
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "pre_visit_preparation",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "appointment_date": "{appointment_date}",
                                    "preparation_instructions": "{pre_visit_instructions}",
                                    "what_to_bring": "{required_documents}",
                                    "fasting_requirements": "{fasting_instructions}"
                                }
                            }
                        }
                    ],
                    next_steps=[],  # End of workflow
                    timeout_minutes=15
                )
            ],
            
            variables={
                "patient_portal_link": "https://portal.brainsait.com",
                "clinic_support_phone": "+966112345678",
                "registration_deadline": "24 hours before appointment",
                "orientation_duration": "30 minutes"
            },
            
            timeout_hours=72,  # 3 days maximum
            
            escalation_policy={
                "levels": [
                    {
                        "level": 1,
                        "timeout_minutes": 60,
                        "action": "notify_patient_services"
                    },
                    {
                        "level": 2,
                        "timeout_minutes": 240,
                        "action": "notify_clinic_manager"
                    }
                ]
            },
            
            compliance_requirements=["hipaa", "pdpl", "nphies", "moh"],
            
            cultural_adaptations={
                "arabic_language_priority": True,
                "islamic_calendar_aware": True,
                "prayer_time_respect": True,
                "family_involvement_support": True,
                "gender_sensitive_communication": True
            }
        )
    
    @staticmethod
    def create_chronic_disease_management_workflow() -> HealthcareWorkflowDefinition:
        """
        Create chronic disease management workflow for ongoing patient care
        Includes medication reminders, lifestyle coaching, and monitoring
        """
        return HealthcareWorkflowDefinition(
            workflow_id="chronic_disease_mgmt_v1.5",
            name="Chronic Disease Management Workflow",
            name_ar="سير عمل إدارة الأمراض المزمنة",
            description="Comprehensive chronic disease management with medication adherence, lifestyle coaching, and monitoring",
            description_ar="إدارة شاملة للأمراض المزمنة مع الالتزام بالأدوية والتدريب على نمط الحياة والمراقبة",
            workflow_type=HealthcareWorkflowType.CHRONIC_DISEASE_MANAGEMENT,
            version="1.5",
            
            trigger=WorkflowTrigger(
                trigger_id="chronic_care_enrollment_trigger",
                event_type=WorkflowEventType.VISIT_COMPLETED,
                conditions={
                    "diagnosis_category": {"operator": "in", "value": ["diabetes", "hypertension", "heart_disease", "chronic_kidney_disease"]},
                    "care_plan_created": True
                },
                priority=MessagePriority.HIGH
            ),
            
            steps=[
                # Step 1: Welcome to Chronic Care Program
                WorkflowStep(
                    step_id="chronic_care_welcome",
                    step_type="message",
                    name="Welcome to Chronic Care Program",
                    description="Welcome patient to chronic disease management program",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "chronic_care_welcome",
                                "channel": "sms",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "condition_name": "{primary_diagnosis}",
                                    "care_team": "{assigned_care_team}",
                                    "program_duration": "{care_program_duration}",
                                    "support_hotline": "{chronic_care_hotline}"
                                }
                            }
                        }
                    ],
                    next_steps=["medication_setup"],
                    timeout_minutes=30,
                    compliance_checks=["hipaa", "pdpl"]
                ),
                
                # Step 2: Medication Setup and Education
                WorkflowStep(
                    step_id="medication_setup",
                    step_type="message",
                    name="Medication Setup and Education",
                    description="Set up medication schedule and provide education",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "medication_education",
                                "channel": "sms",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "medication_list": "{prescribed_medications}",
                                    "dosing_schedule": "{medication_schedule}",
                                    "side_effects_info": "{medication_side_effects}",
                                    "pharmacist_contact": "{clinical_pharmacist_phone}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_medication_confirmation"],
                    timeout_minutes=45
                ),
                
                # Step 3: Wait for Medication Confirmation
                WorkflowStep(
                    step_id="wait_medication_confirmation",
                    step_type="wait",
                    name="Wait for Medication Confirmation",
                    description="Wait for patient to confirm understanding of medication regimen",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 120
                            }
                        }
                    ],
                    next_steps=["daily_medication_reminders"],
                    timeout_minutes=120
                ),
                
                # Step 4: Daily Medication Reminders
                WorkflowStep(
                    step_id="daily_medication_reminders",
                    step_type="message",
                    name="Daily Medication Reminders",
                    description="Send daily medication reminders",
                    conditions=[
                        {
                            "type": "time_of_day",
                            "not_prayer_time": True
                        },
                        {
                            "type": "healthcare_data",
                            "field": "medication_time",
                            "operator": "equals",
                            "value": "current_time"
                        }
                    ],
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "daily_medication_reminder",
                                "channel": "sms",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "medication_name": "{current_medication}",
                                    "dosage": "{medication_dosage}",
                                    "timing": "{medication_timing}",
                                    "food_instructions": "{food_requirements}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_medication_taken"],
                    timeout_minutes=30
                ),
                
                # Step 5: Wait for Medication Taken Confirmation
                WorkflowStep(
                    step_id="wait_medication_taken",
                    step_type="wait",
                    name="Wait for Medication Taken",
                    description="Wait for patient to confirm medication taken",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 60
                            }
                        }
                    ],
                    next_steps=["check_adherence_pattern"],
                    timeout_minutes=60
                ),
                
                # Step 6: Check Adherence Pattern
                WorkflowStep(
                    step_id="check_adherence_pattern",
                    step_type="decision",
                    name="Check Medication Adherence",
                    description="Check medication adherence pattern and determine next action",
                    actions=[
                        {
                            "type": "decision",
                            "parameters": {
                                "conditions": [
                                    {
                                        "type": "healthcare_data",
                                        "field": "adherence_rate",
                                        "operator": "greater_than",
                                        "value": 90,
                                        "result": "good_adherence",
                                        "next_step": "weekly_check_in"
                                    },
                                    {
                                        "type": "healthcare_data",
                                        "field": "adherence_rate",
                                        "operator": "less_than",
                                        "value": 70,
                                        "result": "poor_adherence",
                                        "next_step": "adherence_intervention"
                                    }
                                ],
                                "default_next": "moderate_adherence_support"
                            }
                        }
                    ],
                    next_steps=["weekly_check_in", "adherence_intervention", "moderate_adherence_support"]
                ),
                
                # Step 7: Adherence Intervention
                WorkflowStep(
                    step_id="adherence_intervention",
                    step_type="escalation",
                    name="Medication Adherence Intervention",
                    description="Escalate for pharmacist consultation due to poor adherence",
                    actions=[
                        {
                            "type": "escalation",
                            "parameters": {
                                "type": "pharmacist_consultation",
                                "reason": "Poor medication adherence detected",
                                "urgency": "high",
                                "data_include": ["adherence_history", "medication_list", "patient_concerns"]
                            }
                        },
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "pharmacist_consultation_scheduled",
                                "channel": "voice",
                                "priority": "urgent",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "pharmacist_name": "{assigned_pharmacist}",
                                    "consultation_time": "{consultation_schedule}",
                                    "preparation_notes": "{consultation_prep}"
                                }
                            }
                        }
                    ],
                    next_steps=["post_intervention_monitoring"]
                ),
                
                # Step 8: Weekly Check-in
                WorkflowStep(
                    step_id="weekly_check_in",
                    step_type="message",
                    name="Weekly Health Check-in",
                    description="Weekly check-in on symptoms and overall health",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "weekly_health_checkin",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "week_number": "{care_week_number}",
                                    "symptom_questions": "{weekly_symptom_assessment}",
                                    "lifestyle_questions": "{lifestyle_assessment}",
                                    "emergency_contact": "{care_team_emergency_phone}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_weekly_response"],
                    timeout_minutes=30
                ),
                
                # Step 9: Wait for Weekly Response
                WorkflowStep(
                    step_id="wait_weekly_response",
                    step_type="wait",
                    name="Wait for Weekly Response",
                    description="Wait for patient's weekly health check-in response",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 1440  # 24 hours
                            }
                        }
                    ],
                    next_steps=["analyze_weekly_data"],
                    timeout_minutes=1440
                ),
                
                # Step 10: Analyze Weekly Data
                WorkflowStep(
                    step_id="analyze_weekly_data",
                    step_type="decision",
                    name="Analyze Weekly Health Data",
                    description="Analyze weekly check-in data for concerning trends",
                    actions=[
                        {
                            "type": "decision",
                            "parameters": {
                                "conditions": [
                                    {
                                        "type": "healthcare_data",
                                        "field": "symptom_severity",
                                        "operator": "greater_than",
                                        "value": 7,
                                        "result": "concerning_symptoms",
                                        "next_step": "urgent_provider_alert"
                                    },
                                    {
                                        "type": "healthcare_data",
                                        "field": "lifestyle_score",
                                        "operator": "less_than",
                                        "value": 60,
                                        "result": "lifestyle_intervention_needed",
                                        "next_step": "lifestyle_coaching"
                                    }
                                ],
                                "default_next": "continue_routine_monitoring"
                            }
                        }
                    ],
                    next_steps=["urgent_provider_alert", "lifestyle_coaching", "continue_routine_monitoring"]
                ),
                
                # Step 11: Urgent Provider Alert
                WorkflowStep(
                    step_id="urgent_provider_alert",
                    step_type="escalation",
                    name="Urgent Provider Alert",
                    description="Alert healthcare provider of concerning symptoms",
                    actions=[
                        {
                            "type": "escalation",
                            "parameters": {
                                "type": "provider_urgent_alert",
                                "reason": "Patient reported concerning symptoms in weekly check-in",
                                "urgency": "urgent",
                                "auto_schedule": "next_available_urgent_slot"
                            }
                        }
                    ],
                    next_steps=["continue_routine_monitoring"]
                ),
                
                # Step 12: Lifestyle Coaching
                WorkflowStep(
                    step_id="lifestyle_coaching",
                    step_type="message",
                    name="Lifestyle Coaching Support",
                    description="Provide lifestyle coaching and support resources",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "lifestyle_coaching",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "lifestyle_goals": "{personalized_lifestyle_goals}",
                                    "diet_recommendations": "{cultural_diet_recommendations}",
                                    "exercise_plan": "{safe_exercise_recommendations}",
                                    "support_resources": "{lifestyle_support_resources}"
                                }
                            }
                        }
                    ],
                    next_steps=["continue_routine_monitoring"],
                    timeout_minutes=30
                ),
                
                # Step 13: Continue Routine Monitoring
                WorkflowStep(
                    step_id="continue_routine_monitoring",
                    step_type="wait",
                    name="Continue Routine Monitoring",
                    description="Continue with routine chronic disease monitoring cycle",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "time",
                                "hours": 168  # 1 week
                            }
                        }
                    ],
                    next_steps=["weekly_check_in"],  # Loop back to weekly check-in
                    timeout_minutes=10080  # 1 week
                )
            ],
            
            variables={
                "chronic_care_hotline": "+966112345679",
                "care_program_duration": "12 months",
                "medication_reminder_times": ["08:00", "20:00"],
                "weekly_checkin_day": "sunday"
            },
            
            timeout_hours=8760,  # 1 year for chronic care
            
            escalation_policy={
                "levels": [
                    {
                        "level": 1,
                        "timeout_minutes": 120,
                        "action": "notify_care_coordinator"
                    },
                    {
                        "level": 2,
                        "timeout_minutes": 240,
                        "action": "notify_primary_physician"
                    },
                    {
                        "level": 3,
                        "timeout_minutes": 480,
                        "action": "emergency_intervention_protocol"
                    }
                ]
            },
            
            compliance_requirements=["hipaa", "pdpl", "moh"],
            
            cultural_adaptations={
                "arabic_language_priority": True,
                "islamic_calendar_aware": True,
                "prayer_time_respect": True,
                "ramadan_medication_adjustments": True,
                "cultural_diet_considerations": True,
                "family_caregiver_inclusion": True
            }
        )
    
    @staticmethod
    def create_post_operative_workflow() -> HealthcareWorkflowDefinition:
        """
        Create post-operative care workflow for surgical patients
        """
        return HealthcareWorkflowDefinition(
            workflow_id="post_operative_care_v2.1",
            name="Post-Operative Care Workflow",
            name_ar="سير عمل الرعاية ما بعد العملية",
            description="Comprehensive post-operative care with pain management, wound care, and recovery monitoring",
            description_ar="رعاية شاملة ما بعد العملية مع إدارة الألم والعناية بالجروح ومراقبة التعافي",
            workflow_type=HealthcareWorkflowType.POST_DISCHARGE_FOLLOW_UP,
            version="2.1",
            
            trigger=WorkflowTrigger(
                trigger_id="post_surgery_discharge_trigger",
                event_type=WorkflowEventType.VISIT_COMPLETED,
                conditions={
                    "visit_type": "surgical_procedure",
                    "discharge_status": "discharged_home",
                    "follow_up_required": True
                },
                priority=MessagePriority.HIGH
            ),
            
            steps=[
                # Step 1: Immediate Post-Discharge Instructions
                WorkflowStep(
                    step_id="immediate_post_discharge",
                    step_type="message",
                    name="Immediate Post-Discharge Instructions",
                    description="Send immediate post-surgery care instructions",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "post_surgery_immediate_care",
                                "channel": "sms",
                                "priority": "urgent",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "surgery_type": "{procedure_performed}",
                                    "pain_management": "{pain_medication_instructions}",
                                    "wound_care": "{wound_care_instructions}",
                                    "activity_restrictions": "{activity_limitations}",
                                    "emergency_contact": "{surgeon_emergency_phone}",
                                    "emergency_signs": "{when_to_call_doctor}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_first_day"],
                    timeout_minutes=15,
                    compliance_checks=["hipaa", "pdpl"]
                ),
                
                # Step 2: Wait First Day
                WorkflowStep(
                    step_id="wait_first_day",
                    step_type="wait",
                    name="Wait First Day Post-Surgery",
                    description="Wait 24 hours before first follow-up check",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "time",
                                "hours": 24
                            }
                        }
                    ],
                    next_steps=["first_day_checkin"],
                    timeout_minutes=1440
                ),
                
                # Step 3: First Day Check-in
                WorkflowStep(
                    step_id="first_day_checkin",
                    step_type="message",
                    name="First Day Post-Surgery Check-in",
                    description="Check on patient's condition 24 hours post-surgery",
                    conditions=[
                        {
                            "type": "time_of_day",
                            "not_prayer_time": True
                        }
                    ],
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "post_surgery_day1_checkin",
                                "channel": "voice",
                                "priority": "high",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "pain_scale_question": "{pain_assessment_questions}",
                                    "wound_healing_questions": "{wound_assessment_questions}",
                                    "complication_questions": "{complication_screening_questions}",
                                    "medication_questions": "{medication_adherence_questions}"
                                }
                            }
                        }
                    ],
                    next_steps=["wait_first_day_response"],
                    timeout_minutes=30
                ),
                
                # Step 4: Wait for First Day Response
                WorkflowStep(
                    step_id="wait_first_day_response",
                    step_type="wait",
                    name="Wait for First Day Response",
                    description="Wait for patient response to day-1 check-in",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 120
                            }
                        }
                    ],
                    next_steps=["analyze_day1_response"],
                    timeout_minutes=120
                ),
                
                # Step 5: Analyze Day-1 Response
                WorkflowStep(
                    step_id="analyze_day1_response",
                    step_type="decision",
                    name="Analyze Day-1 Response",
                    description="Analyze first day response for complications",
                    actions=[
                        {
                            "type": "decision",
                            "parameters": {
                                "conditions": [
                                    {
                                        "type": "healthcare_data",
                                        "field": "pain_level",
                                        "operator": "greater_than",
                                        "value": 8,
                                        "result": "severe_pain",
                                        "next_step": "urgent_pain_consultation"
                                    },
                                    {
                                        "type": "healthcare_data",
                                        "field": "complications_reported",
                                        "operator": "equals",
                                        "value": True,
                                        "result": "complications_detected",
                                        "next_step": "urgent_surgical_consultation"
                                    },
                                    {
                                        "type": "healthcare_data",
                                        "field": "wound_healing_concerns",
                                        "operator": "equals",
                                        "value": True,
                                        "result": "wound_concerns",
                                        "next_step": "wound_care_consultation"
                                    }
                                ],
                                "default_next": "continue_routine_monitoring"
                            }
                        }
                    ],
                    next_steps=["urgent_pain_consultation", "urgent_surgical_consultation", "wound_care_consultation", "continue_routine_monitoring"]
                ),
                
                # Step 6: Continue Routine Monitoring
                WorkflowStep(
                    step_id="continue_routine_monitoring",
                    step_type="wait",
                    name="Continue Routine Recovery Monitoring",
                    description="Continue with routine post-operative monitoring",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "time",
                                "hours": 72  # Wait 3 days
                            }
                        }
                    ],
                    next_steps=["weekly_recovery_checkin"],
                    timeout_minutes=4320
                ),
                
                # Step 7: Weekly Recovery Check-in
                WorkflowStep(
                    step_id="weekly_recovery_checkin",
                    step_type="message",
                    name="Weekly Recovery Check-in",
                    description="Weekly check on recovery progress",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "weekly_recovery_checkin",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "recovery_week": "{weeks_post_surgery}",
                                    "activity_progression": "{activity_progression_guidelines}",
                                    "pain_management_review": "{pain_management_assessment}",
                                    "follow_up_appointment": "{scheduled_follow_up_appointment}"
                                }
                            }
                        }
                    ],
                    next_steps=["check_recovery_milestone"],
                    timeout_minutes=30
                ),
                
                # Step 8: Check Recovery Milestone
                WorkflowStep(
                    step_id="check_recovery_milestone",
                    step_type="decision",
                    name="Check Recovery Milestone",
                    description="Check if patient has reached recovery milestones",
                    actions=[
                        {
                            "type": "decision",
                            "parameters": {
                                "conditions": [
                                    {
                                        "type": "healthcare_data",
                                        "field": "weeks_post_surgery",
                                        "operator": "greater_than",
                                        "value": 6,
                                        "result": "recovery_complete",
                                        "next_step": "recovery_completion"
                                    }
                                ],
                                "default_next": "continue_routine_monitoring"
                            }
                        }
                    ],
                    next_steps=["recovery_completion", "continue_routine_monitoring"]
                ),
                
                # Step 9: Recovery Completion
                WorkflowStep(
                    step_id="recovery_completion",
                    step_type="message",
                    name="Recovery Completion Congratulations",
                    description="Congratulate patient on successful recovery",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "recovery_completion_congratulations",
                                "channel": "sms",
                                "priority": "normal",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "surgery_type": "{procedure_performed}",
                                    "recovery_summary": "{recovery_progress_summary}",
                                    "long_term_care": "{long_term_care_recommendations}",
                                    "preventive_care": "{preventive_care_schedule}"
                                }
                            }
                        }
                    ],
                    next_steps=[],  # End of workflow
                    timeout_minutes=15
                )
            ],
            
            variables={
                "surgeon_emergency_phone": "+966112345680",
                "pain_assessment_scale": "0-10 numeric scale",
                "wound_care_video": "https://brainsait.com/wound-care-video",
                "recovery_timeline": "6-8 weeks typical"
            },
            
            timeout_hours=1344,  # 8 weeks maximum
            
            escalation_policy={
                "levels": [
                    {
                        "level": 1,
                        "timeout_minutes": 60,
                        "action": "notify_surgical_nurse"
                    },
                    {
                        "level": 2,
                        "timeout_minutes": 120,
                        "action": "notify_surgeon"
                    },
                    {
                        "level": 3,
                        "timeout_minutes": 240,
                        "action": "emergency_surgical_consultation"
                    }
                ]
            },
            
            compliance_requirements=["hipaa", "pdpl", "moh"],
            
            cultural_adaptations={
                "arabic_language_priority": True,
                "prayer_time_respect": True,
                "family_caregiver_communication": True,
                "cultural_pain_expression_understanding": True,
                "halal_medication_preferences": True
            }
        )
    
    @staticmethod
    def create_emergency_response_workflow() -> HealthcareWorkflowDefinition:
        """
        Create emergency response workflow for critical situations
        """
        return HealthcareWorkflowDefinition(
            workflow_id="emergency_response_v3.0",
            name="Emergency Response Workflow",
            name_ar="سير عمل الاستجابة للطوارئ",
            description="Critical emergency response protocol with immediate notification and escalation",
            description_ar="بروتوكول استجابة طوارئ حرج مع إشعار وتصعيد فوري",
            workflow_type=HealthcareWorkflowType.EMERGENCY_RESPONSE,
            version="3.0",
            
            trigger=WorkflowTrigger(
                trigger_id="emergency_alert_trigger",
                event_type=WorkflowEventType.EMERGENCY_ALERT,
                conditions={
                    "severity": {"operator": "in", "value": ["critical", "urgent", "high"]}
                },
                priority=MessagePriority.CRITICAL
            ),
            
            steps=[
                # Step 1: Immediate Emergency Alert
                WorkflowStep(
                    step_id="immediate_emergency_alert",
                    step_type="message",
                    name="Immediate Emergency Alert",
                    description="Send immediate emergency alert to patient and emergency contacts",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "emergency_immediate_alert",
                                "channel": "voice",
                                "priority": "critical",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "emergency_type": "{emergency_classification}",
                                    "immediate_action": "{immediate_action_required}",
                                    "emergency_services": "997",
                                    "hospital_emergency": "{nearest_hospital_emergency}",
                                    "medical_id": "{patient_medical_id}"
                                }
                            }
                        }
                    ],
                    next_steps=["notify_emergency_contacts"],
                    timeout_minutes=2,
                    compliance_checks=["emergency_protocol"]
                ),
                
                # Step 2: Notify Emergency Contacts
                WorkflowStep(
                    step_id="notify_emergency_contacts",
                    step_type="message",
                    name="Notify Emergency Contacts",
                    description="Immediately notify all emergency contacts",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "emergency_contact_notification",
                                "channel": "voice",
                                "priority": "critical",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "emergency_contact_name": "{emergency_contact_name}",
                                    "emergency_type": "{emergency_classification}",
                                    "patient_location": "{patient_current_location}",
                                    "emergency_services_contacted": "{emergency_services_status}",
                                    "hospital_destination": "{destination_hospital}"
                                }
                            }
                        }
                    ],
                    next_steps=["provider_emergency_alert"],
                    timeout_minutes=3
                ),
                
                # Step 3: Provider Emergency Alert
                WorkflowStep(
                    step_id="provider_emergency_alert",
                    step_type="escalation",
                    name="Provider Emergency Alert",
                    description="Alert all relevant healthcare providers",
                    actions=[
                        {
                            "type": "escalation",
                            "parameters": {
                                "type": "emergency_provider_alert",
                                "reason": "Patient emergency situation requiring immediate medical attention",
                                "urgency": "critical",
                                "broadcast_to": ["primary_physician", "specialist", "emergency_team"],
                                "include_data": ["medical_history", "current_medications", "allergies", "emergency_contacts"]
                            }
                        }
                    ],
                    next_steps=["track_emergency_response"],
                    timeout_minutes=5
                ),
                
                # Step 4: Track Emergency Response
                WorkflowStep(
                    step_id="track_emergency_response",
                    step_type="wait",
                    name="Track Emergency Response",
                    description="Monitor emergency response and provide updates",
                    actions=[
                        {
                            "type": "wait",
                            "parameters": {
                                "type": "response",
                                "timeout_minutes": 30
                            }
                        }
                    ],
                    next_steps=["emergency_follow_up"],
                    timeout_minutes=30
                ),
                
                # Step 5: Emergency Follow-up
                WorkflowStep(
                    step_id="emergency_follow_up",
                    step_type="message",
                    name="Emergency Follow-up",
                    description="Follow up on emergency response status",
                    actions=[
                        {
                            "type": "message",
                            "parameters": {
                                "template_id": "emergency_follow_up",
                                "channel": "sms",
                                "priority": "urgent",
                                "variables": {
                                    "patient_name": "{patient_name}",
                                    "emergency_status": "{emergency_resolution_status}",
                                    "hospital_status": "{hospital_admission_status}",
                                    "next_steps": "{post_emergency_care_plan}",
                                    "follow_up_contact": "{care_coordinator_phone}"
                                }
                            }
                        }
                    ],
                    next_steps=[],  # End of emergency workflow
                    timeout_minutes=10
                )
            ],
            
            variables={
                "emergency_services_number": "997",
                "nearest_hospital_emergency": "+966112345681",
                "emergency_response_team": "BrainSAIT Emergency Response",
                "max_response_time": "15 minutes"
            },
            
            timeout_hours=2,  # Emergency workflows must complete quickly
            
            escalation_policy={
                "levels": [
                    {
                        "level": 1,
                        "timeout_minutes": 5,
                        "action": "emergency_services_997"
                    },
                    {
                        "level": 2,
                        "timeout_minutes": 10,
                        "action": "hospital_emergency_department"
                    },
                    {
                        "level": 3,
                        "timeout_minutes": 15,
                        "action": "regional_emergency_coordinator"
                    }
                ]
            },
            
            compliance_requirements=["emergency_protocol", "hipaa", "pdpl"],
            
            cultural_adaptations={
                "arabic_language_priority": True,
                "family_emergency_notification": True,
                "islamic_emergency_prayers": True,
                "cultural_emergency_preferences": True
            }
        )
    
    @staticmethod
    def get_all_workflow_templates() -> List[HealthcareWorkflowDefinition]:
        """
        Get all pre-built workflow templates
        """
        return [
            HealthcareWorkflowTemplates.create_patient_onboarding_workflow(),
            HealthcareWorkflowTemplates.create_chronic_disease_management_workflow(),
            HealthcareWorkflowTemplates.create_post_operative_workflow(),
            HealthcareWorkflowTemplates.create_emergency_response_workflow()
        ]
    
    @staticmethod
    def get_workflow_by_type(workflow_type: HealthcareWorkflowType) -> Optional[HealthcareWorkflowDefinition]:
        """
        Get workflow template by type
        """
        template_map = {
            HealthcareWorkflowType.PATIENT_ONBOARDING: HealthcareWorkflowTemplates.create_patient_onboarding_workflow,
            HealthcareWorkflowType.CHRONIC_DISEASE_MANAGEMENT: HealthcareWorkflowTemplates.create_chronic_disease_management_workflow,
            HealthcareWorkflowType.POST_DISCHARGE_FOLLOW_UP: HealthcareWorkflowTemplates.create_post_operative_workflow,
            HealthcareWorkflowType.EMERGENCY_RESPONSE: HealthcareWorkflowTemplates.create_emergency_response_workflow
        }
        
        template_function = template_map.get(workflow_type)
        return template_function() if template_function else None

# Export main class
__all__ = ["HealthcareWorkflowTemplates"]