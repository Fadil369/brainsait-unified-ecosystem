# Build-Operate-Transfer (BOT) Lifecycle Management Service
# Implements the core BOT business model for healthcare organizations
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BOTPhase(str, Enum):
    PLANNING = "planning"
    BUILD = "build"
    OPERATE = "operate"
    TRANSFER = "transfer"
    COMPLETED = "completed"

class BOTProjectType(str, Enum):
    RCM_OPERATIONS = "rcm_operations"
    TRAINING_SETUP = "training_setup"
    FULL_PLATFORM = "full_platform"
    TECHNOLOGY_TRANSFER = "technology_transfer"

class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    BLOCKED = "blocked"

class BOTProject(BaseModel):
    project_code: str
    client_organization_id: str
    project_name: str
    project_type: BOTProjectType
    contract_value_sar: float
    build_start_date: date
    build_end_date: date
    operate_start_date: date
    operate_end_date: date
    transfer_start_date: date
    transfer_end_date: date
    current_phase: BOTPhase
    sla_metrics: Dict[str, Any]

class BOTMilestone(BaseModel):
    project_id: str
    phase: BOTPhase
    milestone_name: str
    description: str
    target_date: date
    completion_percentage: float = 0.0
    deliverables: List[str] = []
    status: MilestoneStatus

class KnowledgeTransfer(BaseModel):
    project_id: str
    transfer_type: str  # documentation, training, process, technology
    title: str
    description: str
    recipient_count: int = 0
    completion_status: str = "pending"
    transfer_date: Optional[date] = None
    feedback_score: Optional[float] = None

class BOTService:
    """
    Build-Operate-Transfer lifecycle management service
    Implements the comprehensive BOT model for healthcare transformation
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    async def create_bot_project(self, project: BOTProject) -> str:
        """Create new BOT project with predefined milestones"""
        # Insert project
        project_id = await self._insert_project(project)
        
        # Create phase-specific milestones
        await self._create_build_milestones(project_id, project)
        await self._create_operate_milestones(project_id, project)
        await self._create_transfer_milestones(project_id, project)
        
        logger.info(f"Created BOT project {project.project_code} with ID {project_id}")
        return project_id
    
    async def transition_phase(self, project_id: str, new_phase: BOTPhase) -> bool:
        """Transition project to next phase with validation"""
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Validate phase transition
        if not self._can_transition_to_phase(project["current_phase"], new_phase):
            raise ValueError(f"Cannot transition from {project['current_phase']} to {new_phase}")
        
        # Check phase completion requirements
        phase_complete = await self._validate_phase_completion(project_id, project["current_phase"])
        if not phase_complete:
            raise ValueError(f"Phase {project['current_phase']} requirements not met")
        
        # Update project phase
        await self._update_project_phase(project_id, new_phase)
        
        # Initialize new phase activities
        await self._initialize_phase_activities(project_id, new_phase)
        
        logger.info(f"Project {project_id} transitioned to {new_phase}")
        return True
    
    async def get_project_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""
        project = await self.get_project(project_id)
        milestones = await self.get_project_milestones(project_id)
        metrics = await self._calculate_project_metrics(project_id)
        transfers = await self.get_knowledge_transfers(project_id)
        
        return {
            "project": project,
            "milestones": milestones,
            "metrics": metrics,
            "knowledge_transfers": transfers,
            "phase_progress": await self._calculate_phase_progress(project_id),
            "sla_compliance": await self._check_sla_compliance(project_id),
            "next_deliverables": await self._get_upcoming_deliverables(project_id)
        }
    
    async def update_milestone_progress(self, milestone_id: str, percentage: float, status: MilestoneStatus) -> bool:
        """Update milestone completion progress"""
        query = """
            UPDATE bot_milestones 
            SET completion_percentage = %s, status = %s, updated_at = %s
            WHERE id = %s
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (percentage, status.value, datetime.now(), milestone_id))
            
        # Check if milestone completion triggers phase transition
        if percentage == 100.0 and status == MilestoneStatus.COMPLETED:
            await self._check_phase_completion_trigger(milestone_id)
            
        return True
    
    async def create_knowledge_transfer_plan(self, project_id: str) -> List[KnowledgeTransfer]:
        """Create comprehensive knowledge transfer plan for project"""
        project = await self.get_project(project_id)
        
        transfer_plan = []
        
        # Documentation transfers
        transfer_plan.extend([
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="documentation",
                title="Operations Procedures Manual",
                description="Complete documentation of all operational procedures"
            ),
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="documentation",
                title="System Architecture Documentation",
                description="Technical architecture and integration guides"
            ),
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="documentation",
                title="NPHIES Integration Guide",
                description="Saudi-specific NPHIES integration procedures"
            )
        ])
        
        # Training transfers
        transfer_plan.extend([
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="training",
                title="Medical Coding Specialist Training",
                description="Train internal staff to CPC/NPHIES certification levels"
            ),
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="training",
                title="Revenue Cycle Management Training",
                description="RCM operations and optimization training"
            ),
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="training",
                title="System Administration Training",
                description="Technical system management and troubleshooting"
            )
        ])
        
        # Process transfers
        transfer_plan.extend([
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="process",
                title="Quality Assurance Processes",
                description="QA procedures for 95%+ accuracy maintenance"
            ),
            KnowledgeTransfer(
                project_id=project_id,
                transfer_type="process",
                title="Performance Monitoring Systems",
                description="KPI tracking and performance optimization"
            )
        ])
        
        # Technology transfers
        if project["project_type"] == BOTProjectType.FULL_PLATFORM:
            transfer_plan.append(
                KnowledgeTransfer(
                    project_id=project_id,
                    transfer_type="technology",
                    title="Platform Technology Stack",
                    description="Complete technology platform with source code and licenses"
                )
            )
        
        # Save transfer plan
        for transfer in transfer_plan:
            await self._insert_knowledge_transfer(transfer)
            
        return transfer_plan
    
    async def _create_build_milestones(self, project_id: str, project: BOTProject):
        """Create BUILD phase milestones (Months 1-12)"""
        build_milestones = [
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.BUILD,
                milestone_name="NPHIES Integration Development",
                description="Complete NPHIES-compliant RCM platform development",
                target_date=project.build_start_date + timedelta(days=90),
                deliverables=["NPHIES API integration", "FHIR R4 compliance", "Security certification"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.BUILD,
                milestone_name="AI Claims Analysis Engine",
                description="Deploy AI-powered claims analysis with Arabic NLP",
                target_date=project.build_start_date + timedelta(days=120),
                deliverables=["Arabic NLP models", "Claims prediction engine", "Duplicate detection system"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.BUILD,
                milestone_name="Operations Centers Setup",
                description="Establish 24/7 operations centers",
                target_date=project.build_start_date + timedelta(days=180),
                deliverables=["Riyadh hub setup", "Staff recruitment", "Quality assurance systems"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.BUILD,
                milestone_name="Staff Training & Certification",
                description="Train 500+ medical coding specialists",
                target_date=project.build_start_date + timedelta(days=300),
                deliverables=["CPC certifications", "NPHIES training", "Quality standards"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.BUILD,
                milestone_name="System Integration Testing",
                description="Complete system integration and performance testing",
                target_date=project.build_end_date - timedelta(days=30),
                deliverables=["Performance benchmarks", "Security testing", "PDPL compliance"]
            )
        ]
        
        for milestone in build_milestones:
            await self._insert_milestone(milestone)
    
    async def _create_operate_milestones(self, project_id: str, project: BOTProject):
        """Create OPERATE phase milestones (Months 13-36)"""
        operate_milestones = [
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.OPERATE,
                milestone_name="Full RCM Operations Launch",
                description="Begin comprehensive RCM operations delivery",
                target_date=project.operate_start_date + timedelta(days=30),
                deliverables=["95% claim acceptance rate", "30-day collection cycle", "<2% denial rate"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.OPERATE,
                milestone_name="Training Program Delivery",
                description="Launch medical coding certification programs",
                target_date=project.operate_start_date + timedelta(days=90),
                deliverables=["1000+ students enrolled", "85% certification pass rate", "Corporate programs"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.OPERATE,
                milestone_name="Performance Optimization",
                description="Achieve target performance metrics",
                target_date=project.operate_start_date + timedelta(days=365),
                deliverables=["95%+ accuracy sustained", "Cost savings demonstrated", "Client satisfaction 90%+"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.OPERATE,
                milestone_name="Knowledge Documentation",
                description="Complete operational knowledge documentation",
                target_date=project.operate_end_date - timedelta(days=180),
                deliverables=["Process documentation", "Training materials", "Best practices guide"]
            )
        ]
        
        for milestone in operate_milestones:
            await self._insert_milestone(milestone)
    
    async def _create_transfer_milestones(self, project_id: str, project: BOTProject):
        """Create TRANSFER phase milestones (Months 37-48)"""
        transfer_milestones = [
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.TRANSFER,
                milestone_name="Staff Transition Planning",
                description="Plan transition of operations to client staff",
                target_date=project.transfer_start_date + timedelta(days=30),
                deliverables=["Transition plan", "Staff assessments", "Training schedules"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.TRANSFER,
                milestone_name="Knowledge Transfer Execution",
                description="Execute comprehensive knowledge transfer program",
                target_date=project.transfer_start_date + timedelta(days=180),
                deliverables=["Staff training completed", "Documentation transfer", "Process handover"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.TRANSFER,
                milestone_name="Technology Transfer",
                description="Transfer technology platform and licenses",
                target_date=project.transfer_start_date + timedelta(days=270),
                deliverables=["Platform ownership transfer", "License agreements", "Support contracts"]
            ),
            BOTMilestone(
                project_id=project_id,
                phase=BOTPhase.TRANSFER,
                milestone_name="Operational Independence",
                description="Achieve client operational independence",
                target_date=project.transfer_end_date - timedelta(days=30),
                deliverables=["Independent operations", "Performance maintenance", "Support transition"]
            )
        ]
        
        for milestone in transfer_milestones:
            await self._insert_milestone(milestone)
    
    async def _calculate_project_metrics(self, project_id: str) -> Dict[str, Any]:
        """Calculate key project performance metrics"""
        # This would fetch real metrics from the database
        return {
            "financial": {
                "contract_value": 0,
                "revenue_generated": 0,
                "cost_savings_delivered": 0,
                "roi_percentage": 0
            },
            "operational": {
                "claim_acceptance_rate": 0,
                "average_collection_days": 0,
                "denial_rate": 0,
                "staff_productivity": 0
            },
            "training": {
                "students_certified": 0,
                "certification_pass_rate": 0,
                "corporate_programs": 0,
                "knowledge_transfer_completion": 0
            },
            "quality": {
                "sla_compliance": 0,
                "client_satisfaction": 0,
                "error_rate": 0,
                "audit_score": 0
            }
        }
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details"""
        query = "SELECT * FROM bot_projects WHERE id = %s"
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (project_id,))
            return await cursor.fetchone()
    
    async def get_project_milestones(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all milestones for a project"""
        query = "SELECT * FROM bot_milestones WHERE project_id = %s ORDER BY target_date"
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (project_id,))
            return await cursor.fetchall()
    
    async def get_knowledge_transfers(self, project_id: str) -> List[Dict[str, Any]]:
        """Get knowledge transfer records for project"""
        query = "SELECT * FROM knowledge_transfers WHERE project_id = %s"
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (project_id,))
            return await cursor.fetchall()
    
    def _can_transition_to_phase(self, current_phase: str, new_phase: BOTPhase) -> bool:
        """Validate if phase transition is allowed"""
        transitions = {
            "planning": [BOTPhase.BUILD],
            "build": [BOTPhase.OPERATE],
            "operate": [BOTPhase.TRANSFER],
            "transfer": [BOTPhase.COMPLETED]
        }
        return new_phase in transitions.get(current_phase, [])
    
    async def _validate_phase_completion(self, project_id: str, phase: str) -> bool:
        """Validate that phase completion requirements are met"""
        # Check milestone completion for the phase
        query = """
            SELECT COUNT(*) as total, 
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
            FROM bot_milestones 
            WHERE project_id = %s AND phase = %s
        """
        
        async with self.db.cursor() as cursor:
            await cursor.execute(query, (project_id, phase))
            result = await cursor.fetchone()
            
        if result["total"] == 0:
            return True  # No milestones defined
            
        completion_rate = result["completed"] / result["total"]
        return completion_rate >= 0.8  # Require 80% milestone completion
    
    async def _insert_project(self, project: BOTProject) -> str:
        """Insert new BOT project"""
        # Implementation would insert into bot_projects table
        pass
    
    async def _insert_milestone(self, milestone: BOTMilestone):
        """Insert milestone"""
        # Implementation would insert into bot_milestones table
        pass
    
    async def _insert_knowledge_transfer(self, transfer: KnowledgeTransfer):
        """Insert knowledge transfer record"""
        # Implementation would insert into knowledge_transfers table
        pass