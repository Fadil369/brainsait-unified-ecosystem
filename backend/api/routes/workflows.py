"""
BrainSAIT Workflows Routes - Container Components
Following OidTree 5-component pattern
"""

from fastapi import APIRouter, HTTPException, status, Depends
from models.communication import WorkflowRequest
from services.workflow_service import WorkflowService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


@router.post("/appointment/reminder", response_model=dict)
async def trigger_appointment_reminder(
    workflow: WorkflowRequest,
    service: WorkflowService = Depends()
):
    """Trigger appointment reminder workflow"""
    try:
        return await service.trigger_appointment_reminder(workflow)
    except Exception as e:
        logger.error(f"Error triggering appointment reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger appointment reminder"
        )


@router.post("/clinical/results", response_model=dict)
async def trigger_clinical_results(
    workflow: WorkflowRequest,
    service: WorkflowService = Depends()
):
    """Trigger clinical results notification workflow"""
    try:
        return await service.trigger_clinical_results(workflow)
    except Exception as e:
        logger.error(f"Error triggering clinical results workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger clinical results workflow"
        )


@router.post("/emergency/alert", response_model=dict)
async def trigger_emergency_alert(
    workflow: WorkflowRequest,
    service: WorkflowService = Depends()
):
    """Trigger emergency alert workflow"""
    try:
        return await service.trigger_emergency_alert(workflow)
    except Exception as e:
        logger.error(f"Error triggering emergency alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger emergency alert"
        )


@router.get("/status/{workflow_id}", response_model=dict)
async def get_workflow_status(
    workflow_id: str,
    service: WorkflowService = Depends()
):
    """Get workflow execution status"""
    try:
        return await service.get_workflow_status(workflow_id)
    except Exception as e:
        logger.error(f"Error retrieving workflow status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow status"
        )