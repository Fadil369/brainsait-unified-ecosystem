"""
BrainSAIT Healthcare Platform - NPHIES Compliance and Arabic Message Templates
Comprehensive NPHIES-compliant communication templates with full Arabic/English support

This module provides:
1. NPHIES-compliant message templates and validation
2. Enhanced Arabic message templates with proper RTL formatting
3. Healthcare communication compliance checking
4. Saudi healthcare regulation adherence
5. Patient privacy and data protection (PDPL) compliance
6. Medical terminology translations (Arabic/English)
7. Integration with Saudi healthcare standards
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from arabic_reshaper import reshape
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class NPHIESMessageType(str, Enum):
    """NPHIES-specific message types"""
    CLAIM_SUBMISSION = "claim_submission"
    CLAIM_STATUS = "claim_status"
    ELIGIBILITY_CHECK = "eligibility_check"
    PRIOR_AUTHORIZATION = "prior_authorization"
    PAYMENT_NOTICE = "payment_notice"
    PROVIDER_NOTIFICATION = "provider_notification"
    PATIENT_NOTIFICATION = "patient_notification"

class ComplianceLevel(str, Enum):
    """Healthcare compliance levels"""
    NPHIES_REQUIRED = "nphies_required"
    PDPL_REQUIRED = "pdpl_required"
    MOH_REQUIRED = "moh_required"
    SFDA_REQUIRED = "sfda_required"
    STANDARD = "standard"

class MedicalTerminologyType(str, Enum):
    """Medical terminology types for translation"""
    DIAGNOSIS = "diagnosis"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    BODY_SYSTEM = "body_system"
    SPECIALTY = "specialty"
    GENERAL_MEDICAL = "general_medical"

@dataclass
class NPHIESComplianceRule:
    """NPHIES compliance rule definition"""
    rule_id: str
    rule_name: str
    rule_name_ar: str
    description: str
    description_ar: str
    compliance_level: ComplianceLevel
    required_fields: List[str]
    validation_pattern: Optional[str] = None
    error_message_en: str = ""
    error_message_ar: str = ""

@dataclass
class ArabicMessageTemplate:
    """Enhanced Arabic message template with NPHIES compliance"""
    template_id: str
    template_name: str
    template_name_ar: str
    category: str
    nphies_message_type: Optional[NPHIESMessageType] = None
    compliance_level: ComplianceLevel = ComplianceLevel.STANDARD
    subject_en: str = ""
    subject_ar: str = ""
    content_en: str = ""
    content_ar: str = ""
    variables: List[str] = field(default_factory=list)
    medical_terminology: Dict[str, Dict[str, str]] = field(default_factory=dict)
    formatting_rules: Dict[str, Any] = field(default_factory=dict)
    compliance_notes: str = ""
    compliance_notes_ar: str = ""
    last_updated: datetime = field(default_factory=datetime.now)

class MedicalTerminologyManager:
    """Manages medical terminology translations for Arabic/English"""
    
    def __init__(self):
        self.terminology_db = self._initialize_medical_terminology()
    
    def _initialize_medical_terminology(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Initialize comprehensive medical terminology database"""
        return {
            MedicalTerminologyType.DIAGNOSIS.value: {
                # Common diagnoses
                "diabetes_mellitus": {
                    "en": "Diabetes Mellitus",
                    "ar": "داء السكري",
                    "code": "E11"
                },
                "hypertension": {
                    "en": "Hypertension",
                    "ar": "ارتفاع ضغط الدم",
                    "code": "I10"
                },
                "asthma": {
                    "en": "Asthma",
                    "ar": "الربو",
                    "code": "J45"
                },
                "covid19": {
                    "en": "COVID-19",
                    "ar": "كوفيد-19",
                    "code": "U07.1"
                },
                "pneumonia": {
                    "en": "Pneumonia",
                    "ar": "التهاب الرئة",
                    "code": "J18"
                },
                "gastritis": {
                    "en": "Gastritis",
                    "ar": "التهاب المعدة",
                    "code": "K29"
                }
            },
            MedicalTerminologyType.PROCEDURE.value: {
                # Common procedures
                "blood_test": {
                    "en": "Blood Test",
                    "ar": "فحص الدم",
                    "code": "33747"
                },
                "x_ray": {
                    "en": "X-Ray",
                    "ar": "أشعة سينية",
                    "code": "70000"
                },
                "ct_scan": {
                    "en": "CT Scan",
                    "ar": "أشعة مقطعية",
                    "code": "74150"
                },
                "mri": {
                    "en": "MRI",
                    "ar": "رنين مغناطيسي",
                    "code": "72148"
                },
                "ecg": {
                    "en": "ECG/EKG",
                    "ar": "تخطيط القلب",
                    "code": "93000"
                },
                "consultation": {
                    "en": "Medical Consultation",
                    "ar": "استشارة طبية",
                    "code": "99213"
                }
            },
            MedicalTerminologyType.MEDICATION.value: {
                # Common medications
                "paracetamol": {
                    "en": "Paracetamol",
                    "ar": "باراسيتامول",
                    "code": "RxNorm:161"
                },
                "ibuprofen": {
                    "en": "Ibuprofen",
                    "ar": "إيبوبروفين",
                    "code": "RxNorm:5640"
                },
                "amoxicillin": {
                    "en": "Amoxicillin",
                    "ar": "أموكسيسيلين",
                    "code": "RxNorm:723"
                },
                "metformin": {
                    "en": "Metformin",
                    "ar": "ميتفورمين",
                    "code": "RxNorm:6809"
                },
                "insulin": {
                    "en": "Insulin",
                    "ar": "الأنسولين",
                    "code": "RxNorm:5856"
                }
            },
            MedicalTerminologyType.SPECIALTY.value: {
                # Medical specialties
                "cardiology": {
                    "en": "Cardiology",
                    "ar": "أمراض القلب",
                    "code": "SPEC001"
                },
                "dermatology": {
                    "en": "Dermatology",
                    "ar": "الأمراض الجلدية",
                    "code": "SPEC002"
                },
                "neurology": {
                    "en": "Neurology",
                    "ar": "طب الأعصاب",
                    "code": "SPEC003"
                },
                "orthopedics": {
                    "en": "Orthopedics",
                    "ar": "جراحة العظام",
                    "code": "SPEC004"
                },
                "pediatrics": {
                    "en": "Pediatrics",
                    "ar": "طب الأطفال",
                    "code": "SPEC005"
                },
                "gynecology": {
                    "en": "Gynecology",
                    "ar": "أمراض النساء",
                    "code": "SPEC006"
                },
                "psychiatry": {
                    "en": "Psychiatry",
                    "ar": "الطب النفسي",
                    "code": "SPEC007"
                },
                "emergency_medicine": {
                    "en": "Emergency Medicine",
                    "ar": "طب الطوارئ",
                    "code": "SPEC008"
                }
            },
            MedicalTerminologyType.GENERAL_MEDICAL.value: {
                # General medical terms
                "appointment": {
                    "en": "Appointment",
                    "ar": "موعد",
                    "code": "GEN001"
                },
                "prescription": {
                    "en": "Prescription",
                    "ar": "وصفة طبية",
                    "code": "GEN002"
                },
                "medical_record": {
                    "en": "Medical Record",
                    "ar": "السجل الطبي",
                    "code": "GEN003"
                },
                "insurance": {
                    "en": "Insurance",
                    "ar": "التأمين",
                    "code": "GEN004"
                },
                "patient": {
                    "en": "Patient",
                    "ar": "مريض",
                    "code": "GEN005"
                },
                "doctor": {
                    "en": "Doctor",
                    "ar": "طبيب",
                    "code": "GEN006"
                },
                "nurse": {
                    "en": "Nurse",
                    "ar": "ممرض/ممرضة",
                    "code": "GEN007"
                },
                "hospital": {
                    "en": "Hospital",
                    "ar": "مستشفى",
                    "code": "GEN008"
                },
                "clinic": {
                    "en": "Clinic",
                    "ar": "عيادة",
                    "code": "GEN009"
                },
                "pharmacy": {
                    "en": "Pharmacy",
                    "ar": "صيدلية",
                    "code": "GEN010"
                }
            }
        }
    
    def get_translation(self, 
                       term_key: str, 
                       terminology_type: MedicalTerminologyType, 
                       language: str = "ar") -> str:
        """Get medical terminology translation"""
        try:
            term_data = self.terminology_db.get(terminology_type.value, {}).get(term_key, {})
            return term_data.get(language, term_key)
        except Exception as e:
            logger.warning(f"Translation not found for {term_key}: {e}")
            return term_key
    
    def get_medical_code(self, 
                        term_key: str, 
                        terminology_type: MedicalTerminologyType) -> Optional[str]:
        """Get medical terminology code"""
        try:
            term_data = self.terminology_db.get(terminology_type.value, {}).get(term_key, {})
            return term_data.get("code")
        except Exception as e:
            logger.warning(f"Medical code not found for {term_key}: {e}")
            return None

class NPHIESComplianceValidator:
    """Validates messages for NPHIES compliance"""
    
    def __init__(self):
        self.compliance_rules = self._initialize_compliance_rules()
        self.terminology_manager = MedicalTerminologyManager()
    
    def _initialize_compliance_rules(self) -> Dict[str, NPHIESComplianceRule]:
        """Initialize NPHIES compliance rules"""
        rules = {}
        
        # Patient identification compliance
        rules["patient_id_validation"] = NPHIESComplianceRule(
            rule_id="patient_id_validation",
            rule_name="Patient ID Validation",
            rule_name_ar="التحقق من هوية المريض",
            description="Patient must be identified with valid NPHIES ID or National ID",
            description_ar="يجب تحديد هوية المريض برقم NPHIES صالح أو رقم هوية وطني",
            compliance_level=ComplianceLevel.NPHIES_REQUIRED,
            required_fields=["patient_nphies_id", "national_id"],
            validation_pattern=r"^(NPH\d{10}|\d{10})$",
            error_message_en="Invalid patient identification. NPHIES ID or National ID required.",
            error_message_ar="هوية المريض غير صالحة. مطلوب رقم NPHIES أو رقم الهوية الوطنية."
        )
        
        # Provider identification compliance
        rules["provider_id_validation"] = NPHIESComplianceRule(
            rule_id="provider_id_validation",
            rule_name="Provider ID Validation",
            rule_name_ar="التحقق من هوية مقدم الخدمة",
            description="Provider must have valid NPHIES provider ID",
            description_ar="يجب أن يكون لمقدم الخدمة رقم NPHIES صالح",
            compliance_level=ComplianceLevel.NPHIES_REQUIRED,
            required_fields=["provider_nphies_id"],
            validation_pattern=r"^PRV\d{8}$",
            error_message_en="Invalid provider ID. Valid NPHIES provider ID required.",
            error_message_ar="رقم مقدم الخدمة غير صالح. مطلوب رقم NPHIES صالح لمقدم الخدمة."
        )
        
        # PHI protection compliance
        rules["phi_protection"] = NPHIESComplianceRule(
            rule_id="phi_protection",
            rule_name="PHI Protection",
            rule_name_ar="حماية المعلومات الصحية الشخصية",
            description="Messages must not contain unencrypted PHI",
            description_ar="يجب ألا تحتوي الرسائل على معلومات صحية شخصية غير مشفرة",
            compliance_level=ComplianceLevel.PDPL_REQUIRED,
            required_fields=[],
            error_message_en="Message contains unencrypted PHI. Review and encrypt sensitive data.",
            error_message_ar="الرسالة تحتوي على معلومات صحية شخصية غير مشفرة. يرجى المراجعة وتشفير البيانات الحساسة."
        )
        
        # Arabic language compliance
        rules["arabic_language_support"] = NPHIESComplianceRule(
            rule_id="arabic_language_support",
            rule_name="Arabic Language Support",
            rule_name_ar="دعم اللغة العربية",
            description="Healthcare communications must support Arabic language",
            description_ar="يجب أن تدعم الاتصالات الصحية اللغة العربية",
            compliance_level=ComplianceLevel.MOH_REQUIRED,
            required_fields=["arabic_content"],
            error_message_en="Arabic language support required for Saudi healthcare communications.",
            error_message_ar="دعم اللغة العربية مطلوب للاتصالات الصحية السعودية."
        )
        
        return rules
    
    def validate_message_compliance(self, 
                                  message_data: Dict[str, Any],
                                  template: ArabicMessageTemplate) -> Dict[str, Any]:
        """Validate message for NPHIES and regulatory compliance"""
        try:
            validation_result = {
                "compliant": True,
                "compliance_level": template.compliance_level.value,
                "violations": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check NPHIES-specific compliance
            if template.nphies_message_type:
                nphies_validation = self._validate_nphies_specific(message_data, template)
                validation_result["violations"].extend(nphies_validation.get("violations", []))
                validation_result["warnings"].extend(nphies_validation.get("warnings", []))
            
            # Check patient identification
            patient_validation = self._validate_patient_identification(message_data)
            if not patient_validation["valid"]:
                validation_result["violations"].append(patient_validation["error"])
                validation_result["compliant"] = False
            
            # Check PHI protection
            phi_validation = self._validate_phi_protection(message_data)
            if not phi_validation["valid"]:
                validation_result["violations"].append(phi_validation["error"])
                validation_result["compliant"] = False
            
            # Check Arabic language support
            arabic_validation = self._validate_arabic_support(template)
            if not arabic_validation["valid"]:
                validation_result["warnings"].append(arabic_validation["warning"])
            
            # Check medical terminology compliance
            terminology_validation = self._validate_medical_terminology(message_data, template)
            validation_result["recommendations"].extend(terminology_validation.get("recommendations", []))
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Message compliance validation failed: {e}")
            return {
                "compliant": False,
                "compliance_level": "unknown",
                "violations": [f"Compliance validation error: {str(e)}"],
                "warnings": [],
                "recommendations": []
            }
    
    def _validate_nphies_specific(self, 
                                message_data: Dict[str, Any],
                                template: ArabicMessageTemplate) -> Dict[str, Any]:
        """Validate NPHIES-specific requirements"""
        violations = []
        warnings = []
        
        # Check claim-related messages
        if template.nphies_message_type == NPHIESMessageType.CLAIM_SUBMISSION:
            if not message_data.get("claim_id"):
                violations.append("NPHIES claim ID required for claim submission messages")
            
            if not message_data.get("provider_nphies_id"):
                violations.append("Provider NPHIES ID required for claim messages")
        
        # Check eligibility messages
        elif template.nphies_message_type == NPHIESMessageType.ELIGIBILITY_CHECK:
            if not message_data.get("insurance_id"):
                warnings.append("Insurance ID recommended for eligibility check messages")
        
        # Check payment notices
        elif template.nphies_message_type == NPHIESMessageType.PAYMENT_NOTICE:
            if not message_data.get("payment_amount"):
                violations.append("Payment amount required for payment notice messages")
        
        return {
            "violations": violations,
            "warnings": warnings
        }
    
    def _validate_patient_identification(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate patient identification compliance"""
        patient_id = message_data.get("patient_id", "")
        nphies_id = message_data.get("patient_nphies_id", "")
        national_id = message_data.get("national_id", "")
        
        # Check if at least one valid ID is present
        valid_nphies = re.match(r"^NPH\d{10}$", nphies_id) if nphies_id else False
        valid_national = re.match(r"^\d{10}$", national_id) if national_id else False
        valid_patient = bool(patient_id)
        
        if not (valid_nphies or valid_national or valid_patient):
            return {
                "valid": False,
                "error": "Patient identification required: NPHIES ID, National ID, or Patient ID"
            }
        
        return {"valid": True}
    
    def _validate_phi_protection(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PHI protection compliance"""
        # Check for common PHI patterns in message content
        content = str(message_data.get("message_content", ""))
        
        # Patterns that might indicate unencrypted PHI
        phi_patterns = [
            r'\b\d{10}\b',  # National ID pattern
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN-like pattern
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card pattern
            r'\b[A-Z]{2}\d{8}\b',  # ID card pattern
        ]
        
        for pattern in phi_patterns:
            if re.search(pattern, content):
                return {
                    "valid": False,
                    "error": "Potential unencrypted PHI detected in message content"
                }
        
        return {"valid": True}
    
    def _validate_arabic_support(self, template: ArabicMessageTemplate) -> Dict[str, Any]:
        """Validate Arabic language support"""
        if not template.content_ar or not template.subject_ar:
            return {
                "valid": False,
                "warning": "Arabic language content missing. MOH requires Arabic support for healthcare communications."
            }
        
        return {"valid": True}
    
    def _validate_medical_terminology(self, 
                                   message_data: Dict[str, Any],
                                   template: ArabicMessageTemplate) -> Dict[str, Any]:
        """Validate medical terminology usage"""
        recommendations = []
        
        # Check if medical terms have proper translations
        content = str(message_data.get("message_content", ""))
        
        # Look for common medical terms that should be translated
        medical_terms = ["doctor", "patient", "appointment", "prescription", "diagnosis"]
        
        for term in medical_terms:
            if term.lower() in content.lower():
                arabic_translation = self.terminology_manager.get_translation(
                    term, MedicalTerminologyType.GENERAL_MEDICAL, "ar"
                )
                if arabic_translation != term:
                    recommendations.append(f"Consider using Arabic translation for '{term}': '{arabic_translation}'")
        
        return {"recommendations": recommendations}

class ArabicMessageTemplateManager:
    """Manages Arabic message templates with NPHIES compliance"""
    
    def __init__(self):
        self.templates = self._initialize_arabic_templates()
        self.compliance_validator = NPHIESComplianceValidator()
        self.terminology_manager = MedicalTerminologyManager()
    
    def _initialize_arabic_templates(self) -> Dict[str, ArabicMessageTemplate]:
        """Initialize comprehensive Arabic message templates"""
        templates = {}
        
        # NPHIES Claim Submission Notification
        templates["nphies_claim_submitted"] = ArabicMessageTemplate(
            template_id="nphies_claim_submitted",
            template_name="NPHIES Claim Submission Notification",
            template_name_ar="إشعار تقديم مطالبة NPHIES",
            category="nphies_claims",
            nphies_message_type=NPHIESMessageType.CLAIM_SUBMISSION,
            compliance_level=ComplianceLevel.NPHIES_REQUIRED,
            subject_en="Claim Submitted to NPHIES - BrainSAIT Healthcare",
            subject_ar="تم تقديم المطالبة إلى NPHIES - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, your insurance claim (ID: {claim_id}) has been submitted to NPHIES for processing. Claim amount: {amount} SAR. You will be notified of the approval status within 72 hours.",
            content_ar="عزيزي {patient_name}، تم تقديم مطالبتك التأمينية (رقم: {claim_id}) إلى NPHIES للمعالجة. مبلغ المطالبة: {amount} ريال سعودي. سيتم إشعارك بحالة الموافقة خلال 72 ساعة.",
            variables=["patient_name", "claim_id", "amount"],
            compliance_notes="NPHIES claim submission requires secure transmission and patient notification",
            compliance_notes_ar="تقديم مطالبة NPHIES يتطلب نقل آمن وإشعار المريض"
        )
        
        # NPHIES Eligibility Check Result
        templates["nphies_eligibility_result"] = ArabicMessageTemplate(
            template_id="nphies_eligibility_result",
            template_name="NPHIES Eligibility Check Result",
            template_name_ar="نتيجة فحص الأهلية NPHIES",
            category="nphies_eligibility",
            nphies_message_type=NPHIESMessageType.ELIGIBILITY_CHECK,
            compliance_level=ComplianceLevel.NPHIES_REQUIRED,
            subject_en="Insurance Eligibility Confirmed - BrainSAIT Healthcare",
            subject_ar="تأكيد أهلية التأمين - برينسيت للرعاية الصحية",
            content_en="Hello {patient_name}, your insurance eligibility has been verified through NPHIES. Coverage: {coverage_details}. Co-payment: {copay_amount} SAR. Valid until: {expiry_date}.",
            content_ar="مرحباً {patient_name}، تم التحقق من أهلية تأمينك من خلال NPHIES. التغطية: {coverage_details}. الدفع المشارك: {copay_amount} ريال سعودي. صالح حتى: {expiry_date}.",
            variables=["patient_name", "coverage_details", "copay_amount", "expiry_date"],
            medical_terminology={
                "insurance": {"en": "Insurance", "ar": "التأمين"},
                "coverage": {"en": "Coverage", "ar": "التغطية"},
                "copay": {"en": "Co-payment", "ar": "الدفع المشارك"}
            }
        )
        
        # Enhanced Appointment Confirmation with Medical Context
        templates["medical_appointment_confirmation"] = ArabicMessageTemplate(
            template_id="medical_appointment_confirmation",
            template_name="Medical Appointment Confirmation",
            template_name_ar="تأكيد الموعد الطبي",
            category="appointments",
            compliance_level=ComplianceLevel.MOH_REQUIRED,
            subject_en="Medical Appointment Confirmed - {specialty} - BrainSAIT Healthcare",
            subject_ar="تأكيد الموعد الطبي - {specialty_ar} - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, your appointment with Dr. {doctor_name} ({specialty}) is confirmed for {appointment_date} at {appointment_time}. Location: {clinic_location}. Please bring your insurance card and valid ID. Fasting required: {fasting_required}.",
            content_ar="عزيزي {patient_name}، موعدك مع الدكتور {doctor_name} ({specialty_ar}) مؤكد في {appointment_date} الساعة {appointment_time}. الموقع: {clinic_location}. يرجى إحضار بطاقة التأمين والهوية الصالحة. الصيام مطلوب: {fasting_required}.",
            variables=["patient_name", "doctor_name", "specialty", "specialty_ar", "appointment_date", "appointment_time", "clinic_location", "fasting_required"],
            medical_terminology={
                "appointment": {"en": "Appointment", "ar": "موعد"},
                "doctor": {"en": "Doctor", "ar": "دكتور"},
                "clinic": {"en": "Clinic", "ar": "عيادة"},
                "insurance": {"en": "Insurance", "ar": "التأمين"},
                "fasting": {"en": "Fasting", "ar": "الصيام"}
            }
        )
        
        # Prescription Ready with Medication Details
        templates["prescription_ready_detailed"] = ArabicMessageTemplate(
            template_id="prescription_ready_detailed",
            template_name="Prescription Ready with Details",
            template_name_ar="الوصفة الطبية جاهزة مع التفاصيل",
            category="prescriptions",
            compliance_level=ComplianceLevel.SFDA_REQUIRED,
            subject_en="Prescription Ready for Pickup - BrainSAIT Healthcare",
            subject_ar="الوصفة الطبية جاهزة للاستلام - برينسيت للرعاية الصحية",
            content_en="Hello {patient_name}, your prescription is ready at {pharmacy_name}. Medications: {medication_list}. Total cost: {total_cost} SAR (Insurance covered: {insurance_covered} SAR). Please bring valid ID. Pharmacy hours: {pharmacy_hours}. For questions, call: {pharmacy_phone}.",
            content_ar="مرحباً {patient_name}، وصفتك الطبية جاهزة في {pharmacy_name}. الأدوية: {medication_list}. التكلفة الإجمالية: {total_cost} ريال سعودي (مغطى بالتأمين: {insurance_covered} ريال سعودي). يرجى إحضار هوية صالحة. ساعات الصيدلية: {pharmacy_hours}. للاستفسار، اتصل على: {pharmacy_phone}.",
            variables=["patient_name", "pharmacy_name", "medication_list", "total_cost", "insurance_covered", "pharmacy_hours", "pharmacy_phone"],
            medical_terminology={
                "prescription": {"en": "Prescription", "ar": "الوصفة الطبية"},
                "medication": {"en": "Medication", "ar": "دواء"},
                "pharmacy": {"en": "Pharmacy", "ar": "صيدلية"},
                "insurance": {"en": "Insurance", "ar": "التأمين"}
            },
            compliance_notes="SFDA requires detailed medication information and proper identification",
            compliance_notes_ar="الهيئة العامة للغذاء والدواء تتطلب معلومات مفصلة عن الدواء والتحقق من الهوية"
        )
        
        # Lab Results with Clinical Context
        templates["lab_results_clinical"] = ArabicMessageTemplate(
            template_id="lab_results_clinical",
            template_name="Lab Results with Clinical Context",
            template_name_ar="نتائج المختبر مع السياق السريري",
            category="clinical_results",
            compliance_level=ComplianceLevel.MOH_REQUIRED,
            subject_en="Lab Results Available - {test_name} - BrainSAIT Healthcare",
            subject_ar="نتائج المختبر متاحة - {test_name_ar} - برينسيت للرعاية الصحية",
            content_en="Dear {patient_name}, your {test_name} results are now available. Status: {result_status}. Please log into your patient portal to view detailed results: {portal_link}. Follow-up required: {followup_required}. If you have questions, contact Dr. {doctor_name} at {doctor_phone}.",
            content_ar="عزيزي {patient_name}، نتائج {test_name_ar} متاحة الآن. الحالة: {result_status_ar}. يرجى تسجيل الدخول لبوابة المريض لعرض النتائج التفصيلية: {portal_link}. متابعة مطلوبة: {followup_required_ar}. في حالة وجود أسئلة، اتصل بالدكتور {doctor_name} على {doctor_phone}.",
            variables=["patient_name", "test_name", "test_name_ar", "result_status", "result_status_ar", "portal_link", "followup_required", "followup_required_ar", "doctor_name", "doctor_phone"],
            medical_terminology={
                "lab_results": {"en": "Lab Results", "ar": "نتائج المختبر"},
                "test": {"en": "Test", "ar": "فحص"},
                "normal": {"en": "Normal", "ar": "طبيعي"},
                "abnormal": {"en": "Abnormal", "ar": "غير طبيعي"},
                "followup": {"en": "Follow-up", "ar": "متابعة"}
            }
        )
        
        # Emergency Alert with Severity
        templates["emergency_alert_medical"] = ArabicMessageTemplate(
            template_id="emergency_alert_medical",
            template_name="Medical Emergency Alert",
            template_name_ar="تنبيه طوارئ طبي",
            category="emergency",
            compliance_level=ComplianceLevel.MOH_REQUIRED,
            subject_en="URGENT: Medical Emergency Alert - BrainSAIT Healthcare",
            subject_ar="عاجل: تنبيه طوارئ طبي - برينسيت للرعاية الصحية",
            content_en="EMERGENCY ALERT: {patient_name}, you have a critical medical alert. Alert type: {alert_type}. Please contact your physician immediately at {doctor_phone} or proceed to the nearest emergency room. If this is life-threatening, call 997 (Saudi Red Crescent) immediately.",
            content_ar="تنبيه طوارئ: {patient_name}، لديك تنبيه طبي حرج. نوع التنبيه: {alert_type_ar}. يرجى الاتصال بطبيبك فوراً على {doctor_phone} أو التوجه لأقرب غرفة طوارئ. إذا كان هذا يهدد الحياة، اتصل على 997 (الهلال الأحمر السعودي) فوراً.",
            variables=["patient_name", "alert_type", "alert_type_ar", "doctor_phone"],
            medical_terminology={
                "emergency": {"en": "Emergency", "ar": "طوارئ"},
                "critical": {"en": "Critical", "ar": "حرج"},
                "physician": {"en": "Physician", "ar": "طبيب"},
                "hospital": {"en": "Hospital", "ar": "مستشفى"}
            },
            formatting_rules={
                "priority": "critical",
                "channels": ["voice", "sms"],
                "max_retries": 5
            }
        )
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[ArabicMessageTemplate]:
        """Get message template by ID"""
        return self.templates.get(template_id)
    
    def render_template(self, 
                       template_id: str, 
                       variables: Dict[str, Any],
                       language: str = "ar",
                       validate_compliance: bool = True) -> Dict[str, Any]:
        """Render message template with variables and compliance validation"""
        try:
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Select language-specific content
            if language == "ar":
                subject_template = template.subject_ar
                content_template = template.content_ar
            else:
                subject_template = template.subject_en
                content_template = template.content_en
            
            # Replace variables
            subject = self._replace_variables(subject_template, variables, template)
            content = self._replace_variables(content_template, variables, template)
            
            # Apply Arabic formatting if needed
            if language == "ar":
                subject = self._format_arabic_text(subject)
                content = self._format_arabic_text(content)
            
            # Prepare message data for validation
            message_data = {
                "template_id": template_id,
                "subject": subject,
                "message_content": content,
                "language": language,
                **variables
            }
            
            # Validate compliance if requested
            compliance_result = None
            if validate_compliance:
                compliance_result = self.compliance_validator.validate_message_compliance(
                    message_data, template
                )
            
            return {
                "success": True,
                "subject": subject,
                "content": content,
                "template": template,
                "compliance": compliance_result,
                "medical_terminology": template.medical_terminology,
                "formatting_rules": template.formatting_rules
            }
            
        except Exception as e:
            logger.error(f"Failed to render template {template_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "subject": "",
                "content": "",
                "compliance": None
            }
    
    def _replace_variables(self, 
                          template_text: str, 
                          variables: Dict[str, Any],
                          template: ArabicMessageTemplate) -> str:
        """Replace variables in template text with enhanced medical terminology"""
        text = template_text
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            
            # Apply medical terminology translation if applicable
            if var_name in template.medical_terminology:
                term_data = template.medical_terminology[var_name]
                if isinstance(var_value, str) and var_value.lower() in term_data:
                    var_value = term_data[var_value.lower()]
            
            # Handle medical term translations
            if var_name.endswith("_ar") and var_name[:-3] in variables:
                # This is an Arabic version of a term
                base_term = variables[var_name[:-3]]
                arabic_translation = self.terminology_manager.get_translation(
                    base_term.lower().replace(" ", "_"),
                    MedicalTerminologyType.GENERAL_MEDICAL,
                    "ar"
                )
                if arabic_translation != base_term:
                    var_value = arabic_translation
            
            text = text.replace(placeholder, str(var_value))
        
        return text
    
    def _format_arabic_text(self, text: str) -> str:
        """Format Arabic text for proper RTL display"""
        try:
            # Reshape Arabic text for proper character joining
            reshaped_text = reshape(text)
            # Apply bidirectional algorithm for proper RTL display
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logger.warning(f"Arabic text formatting failed: {e}")
            return text
    
    def get_templates_by_category(self, category: str) -> List[ArabicMessageTemplate]:
        """Get all templates in a specific category"""
        return [template for template in self.templates.values() if template.category == category]
    
    def get_nphies_templates(self) -> List[ArabicMessageTemplate]:
        """Get all NPHIES-specific templates"""
        return [template for template in self.templates.values() if template.nphies_message_type is not None]
    
    def validate_template_compliance(self, template_id: str) -> Dict[str, Any]:
        """Validate template compliance without rendering"""
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template {template_id} not found"}
        
        # Basic template validation
        validation_result = {
            "template_id": template_id,
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check Arabic content
        if not template.content_ar or not template.subject_ar:
            validation_result["issues"].append("Missing Arabic content - MOH requires Arabic support")
            validation_result["compliant"] = False
        
        # Check NPHIES compliance
        if template.compliance_level == ComplianceLevel.NPHIES_REQUIRED:
            if not template.nphies_message_type:
                validation_result["issues"].append("NPHIES message type not specified for NPHIES-required template")
                validation_result["compliant"] = False
        
        # Check medical terminology
        if template.medical_terminology:
            for term, translations in template.medical_terminology.items():
                if "ar" not in translations:
                    validation_result["recommendations"].append(f"Arabic translation missing for medical term: {term}")
        
        return validation_result