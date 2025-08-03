# Medical Coding Training & Certification Service
# Implements comprehensive training platform for 25,000+ professionals
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)

class ProgramType(str, Enum):
    FOUNDATION = "foundation"
    ADVANCED = "advanced"
    SPECIALIZATION = "specialization"
    CORPORATE = "corporate"

class CertificationType(str, Enum):
    CPC = "CPC"  # Certified Professional Coder
    NPHIES = "NPHIES"  # NPHIES Compliance Specialist
    RCMP = "RCMP"  # Revenue Cycle Management Professional
    HITS = "HITS"  # Healthcare IT Integration Specialist
    CCS = "CCS"  # Certified Coding Specialist

class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"

class ModuleStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TrainingProgram(BaseModel):
    program_code: str
    title: str
    title_ar: str
    description: str
    description_ar: str
    program_type: ProgramType
    duration_hours: int
    certification_type: CertificationType
    language: str = "bilingual"  # arabic, english, bilingual
    price_sar: float
    prerequisites: List[str] = []
    learning_outcomes: List[str] = []

class TrainingModule(BaseModel):
    program_id: str
    module_code: str
    title: str
    title_ar: str
    content_type: str  # video, document, quiz, lab, simulation
    duration_minutes: int
    sequence_order: int
    content_url: Optional[str] = None
    assessment_required: bool = False
    passing_score: Optional[float] = None

class StudentEnrollment(BaseModel):
    student_id: str
    program_id: str
    enrollment_date: date
    expected_completion: date
    progress_percentage: float = 0.0
    status: EnrollmentStatus
    payment_status: str = "pending"
    employer_sponsored: bool = False

class TrainingAssessment(BaseModel):
    enrollment_id: str
    assessment_type: str  # quiz, exam, practical, certification
    max_score: float
    passing_score: float
    attempts_allowed: int = 3
    time_limit_minutes: Optional[int] = None

class TrainingService:
    """
    Comprehensive training platform service implementing BOT training objectives
    Target: 25,000+ certified professionals with 85%+ pass rate
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    async def create_training_program(self, program: TrainingProgram) -> str:
        """Create new training program with modules"""
        program_id = str(uuid.uuid4())
        
        # Insert program
        query = """
            INSERT INTO training_programs (
                id, program_code, title, title_ar, description, description_ar,
                program_type, duration_hours, certification_type, language, 
                price_sar, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (
                program_id, program.program_code, program.title, program.title_ar,
                program.description, program.description_ar, program.program_type.value,
                program.duration_hours, program.certification_type.value,
                program.language, program.price_sar, "active", datetime.now()
            ))
        
        # Create default modules based on program type
        await self._create_default_modules(program_id, program)
        
        logger.info(f"Created training program {program.program_code}")
        return program_id
    
    async def enroll_student(self, enrollment: StudentEnrollment) -> str:
        """Enroll student in training program"""
        enrollment_id = str(uuid.uuid4())
        
        # Validate prerequisites
        program = await self.get_program(enrollment.program_id)
        if not await self._check_prerequisites(enrollment.student_id, program):
            raise ValueError("Student does not meet prerequisites")
        
        # Create enrollment
        query = """
            INSERT INTO student_enrollments (
                id, student_id, program_id, enrollment_date, start_date,
                expected_completion, progress_percentage, status,
                payment_status, employer_sponsored, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (
                enrollment_id, enrollment.student_id, enrollment.program_id,
                enrollment.enrollment_date, datetime.now().date(),
                enrollment.expected_completion, 0.0, enrollment.status.value,
                enrollment.payment_status, enrollment.employer_sponsored,
                datetime.now()
            ))
        
        # Initialize progress tracking for all modules
        await self._initialize_progress_tracking(enrollment_id, enrollment.program_id)
        
        # Send welcome materials (Arabic/English based on preference)
        await self._send_enrollment_confirmation(enrollment_id)
        
        logger.info(f"Enrolled student {enrollment.student_id} in program {enrollment.program_id}")
        return enrollment_id
    
    async def update_progress(self, enrollment_id: str, module_id: str, 
                           time_spent: int, completed: bool = False) -> bool:
        """Update student progress for a module"""
        
        # Update module progress
        query = """
            UPDATE training_progress 
            SET time_spent_minutes = time_spent_minutes + %s,
                completed_at = CASE WHEN %s THEN %s ELSE completed_at END,
                status = CASE WHEN %s THEN 'completed' ELSE 'in_progress' END
            WHERE enrollment_id = %s AND module_id = %s
        """
        
        completion_time = datetime.now() if completed else None
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (
                time_spent, completed, completion_time, 
                completed, enrollment_id, module_id
            ))
        
        # Recalculate overall progress
        await self._update_enrollment_progress(enrollment_id)
        
        # Check for program completion
        if completed:
            await self._check_program_completion(enrollment_id)
        
        return True
    
    async def submit_assessment(self, enrollment_id: str, assessment_id: str,
                              answers: Dict[str, Any]) -> Dict[str, Any]:
        """Submit assessment and calculate score"""
        
        # Get assessment details
        assessment = await self._get_assessment(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        # Check attempt limits
        attempts = await self._get_assessment_attempts(enrollment_id, assessment_id)
        if attempts >= assessment["attempts_allowed"]:
            raise ValueError("Maximum attempts exceeded")
        
        # Calculate score
        score = await self._calculate_assessment_score(assessment_id, answers)
        passed = score >= assessment["passing_score"]
        
        # Record attempt
        attempt_id = await self._record_assessment_attempt(
            enrollment_id, assessment_id, score, passed, answers
        )
        
        # Update progress if passed
        if passed and assessment["assessment_type"] == "certification":
            await self._award_certification(enrollment_id)
        
        return {
            "attempt_id": attempt_id,
            "score": score,
            "passing_score": assessment["passing_score"],
            "passed": passed,
            "attempts_remaining": max(0, assessment["attempts_allowed"] - attempts - 1),
            "certification_awarded": passed and assessment["assessment_type"] == "certification"
        }
    
    async def get_student_dashboard(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student dashboard"""
        
        # Get active enrollments
        enrollments = await self._get_student_enrollments(student_id)
        
        # Get progress summary
        progress_summary = []
        for enrollment in enrollments:
            progress = await self._get_enrollment_progress(enrollment["id"])
            progress_summary.append({
                "enrollment": enrollment,
                "progress": progress,
                "next_modules": await self._get_next_modules(enrollment["id"]),
                "recent_activity": await self._get_recent_activity(enrollment["id"])
            })
        
        # Get certifications
        certifications = await self._get_student_certifications(student_id)
        
        # Get performance analytics
        analytics = await self._calculate_student_analytics(student_id)
        
        return {
            "student_info": await self._get_student_info(student_id),
            "enrollments": progress_summary,
            "certifications": certifications,
            "analytics": analytics,
            "recommendations": await self._get_program_recommendations(student_id)
        }
    
    async def get_corporate_training_plan(self, organization_id: str, 
                                       staff_count: int, 
                                       specializations: List[str]) -> Dict[str, Any]:
        """Create customized corporate training plan"""
        
        # Assess current competencies
        competency_gap = await self._assess_competency_gap(organization_id, specializations)
        
        # Recommend programs
        recommended_programs = []
        for gap in competency_gap:
            programs = await self._find_programs_for_competency(gap["competency"])
            recommended_programs.extend(programs)
        
        # Calculate investment and timeline
        total_cost = sum(p["price_sar"] * staff_count for p in recommended_programs)
        total_duration = max(p["duration_hours"] for p in recommended_programs)
        
        # Create implementation timeline
        timeline = await self._create_corporate_timeline(recommended_programs, staff_count)
        
        return {
            "organization_id": organization_id,
            "staff_count": staff_count,
            "competency_gaps": competency_gap,
            "recommended_programs": recommended_programs,
            "investment": {
                "total_cost_sar": total_cost,
                "cost_per_employee": total_cost / staff_count,
                "roi_projection": await self._calculate_training_roi(organization_id, total_cost)
            },
            "timeline": timeline,
            "expected_outcomes": {
                "certification_rate": "85%+",
                "competency_improvement": "40%+",
                "operational_efficiency": "25%+",
                "revenue_impact": "15%+"
            }
        }
    
    async def _create_default_modules(self, program_id: str, program: TrainingProgram):
        """Create default modules based on program type and certification"""
        
        modules = []
        
        if program.certification_type == CertificationType.CPC:
            modules = [
                {
                    "module_code": "MCC-101-M1",
                    "title": "Healthcare Fundamentals",
                    "title_ar": "أساسيات الرعاية الصحية",
                    "content_type": "video",
                    "duration_minutes": 2400,  # 40 hours
                    "sequence_order": 1
                },
                {
                    "module_code": "MCC-101-M2", 
                    "title": "ICD-10-AM Implementation",
                    "title_ar": "تطبيق نظام ICD-10-AM",
                    "content_type": "interactive",
                    "duration_minutes": 7200,  # 120 hours
                    "sequence_order": 2
                },
                {
                    "module_code": "MCC-101-M3",
                    "title": "NPHIES Platform Integration",
                    "title_ar": "تكامل منصة نفيس",
                    "content_type": "lab",
                    "duration_minutes": 3600,  # 60 hours
                    "sequence_order": 3
                },
                {
                    "module_code": "MCC-101-M4",
                    "title": "Practical Coding Exercises",
                    "title_ar": "تمارين الترميز العملية",
                    "content_type": "simulation",
                    "duration_minutes": 4800,  # 80 hours
                    "sequence_order": 4
                }
            ]
        
        elif program.certification_type == CertificationType.NPHIES:
            modules = [
                {
                    "module_code": "NCC-201-M1",
                    "title": "NPHIES Platform Overview",
                    "title_ar": "نظرة عامة على منصة نفيس",
                    "content_type": "video",
                    "duration_minutes": 1800,  # 30 hours
                    "sequence_order": 1
                },
                {
                    "module_code": "NCC-201-M2",
                    "title": "Claims Submission Process",
                    "title_ar": "عملية تقديم المطالبات",
                    "content_type": "interactive",
                    "duration_minutes": 2400,  # 40 hours
                    "sequence_order": 2
                },
                {
                    "module_code": "NCC-201-M3",
                    "title": "Denial Management",
                    "title_ar": "إدارة رفض المطالبات",
                    "content_type": "case_study",
                    "duration_minutes": 1800,  # 30 hours
                    "sequence_order": 3
                },
                {
                    "module_code": "NCC-201-M4",
                    "title": "Compliance and Audit",
                    "title_ar": "الامتثال والمراجعة",
                    "content_type": "assessment",
                    "duration_minutes": 1800,  # 30 hours
                    "sequence_order": 4
                }
            ]
        
        # Insert modules
        for module_data in modules:
            module = TrainingModule(
                program_id=program_id,
                **module_data
            )
            await self._insert_module(module)
    
    async def _check_prerequisites(self, student_id: str, program: Dict[str, Any]) -> bool:
        """Check if student meets program prerequisites"""
        if not program.get("prerequisites"):
            return True
        
        # Check completed certifications
        student_certs = await self._get_student_certifications(student_id)
        completed_certs = [cert["certification_type"] for cert in student_certs]
        
        for prereq in program["prerequisites"]:
            if prereq not in completed_certs:
                return False
        
        return True
    
    async def _calculate_assessment_score(self, assessment_id: str, answers: Dict[str, Any]) -> float:
        """Calculate assessment score based on correct answers"""
        # Get correct answers
        correct_answers = await self._get_assessment_answers(assessment_id)
        
        total_questions = len(correct_answers)
        correct_count = 0
        
        for question_id, correct_answer in correct_answers.items():
            student_answer = answers.get(question_id)
            if self._answers_match(student_answer, correct_answer):
                correct_count += 1
        
        return (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    async def _award_certification(self, enrollment_id: str):
        """Award certification upon successful completion"""
        enrollment = await self._get_enrollment(enrollment_id)
        program = await self.get_program(enrollment["program_id"])
        
        certificate_number = f"BRAINSAIT-{program['certification_type']}-{datetime.now().strftime('%Y%m%d')}-{enrollment_id[:8]}"
        
        # Update enrollment with certification
        query = """
            UPDATE student_enrollments 
            SET certificate_number = %s, 
                certificate_issued_date = %s,
                status = 'completed',
                actual_completion = %s
            WHERE id = %s
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (
                certificate_number,
                datetime.now().date(),
                datetime.now().date(),
                enrollment_id
            ))
        
        # Generate digital certificate
        await self._generate_digital_certificate(enrollment_id, certificate_number)
        
        logger.info(f"Awarded {program['certification_type']} certification: {certificate_number}")
    
    async def _calculate_training_roi(self, organization_id: str, investment: float) -> Dict[str, Any]:
        """Calculate ROI projection for corporate training investment"""
        
        # Based on BOT.md projected improvements
        return {
            "salary_increase_avg": 45000,  # SAR per employee
            "efficiency_gain": 0.25,  # 25% productivity improvement
            "error_reduction": 0.70,  # 70% reduction in coding errors
            "revenue_cycle_improvement": 0.15,  # 15% faster collections
            "payback_period_months": 8,
            "three_year_roi": 3.2  # 320% ROI over 3 years
        }
    
    async def get_program(self, program_id: str) -> Optional[Dict[str, Any]]:
        """Get training program details"""
        query = "SELECT * FROM training_programs WHERE id = %s"
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (program_id,))
            return await cursor.fetchone()
    
    async def _insert_module(self, module: TrainingModule):
        """Insert training module"""
        query = """
            INSERT INTO training_modules (
                id, program_id, module_code, title, title_ar, content_type,
                duration_minutes, sequence_order, content_url, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (
                str(uuid.uuid4()), module.program_id, module.module_code,
                module.title, module.title_ar, module.content_type,
                module.duration_minutes, module.sequence_order,
                module.content_url, datetime.now()
            ))
    
    # Additional helper methods would be implemented here...
    async def _initialize_progress_tracking(self, enrollment_id: str, program_id: str):
        """Initialize progress tracking for all modules"""
        pass
        
    async def _update_enrollment_progress(self, enrollment_id: str):
        """Update overall enrollment progress percentage"""
        pass
        
    async def _check_program_completion(self, enrollment_id: str):
        """Check if program is completed and trigger certification"""
        pass