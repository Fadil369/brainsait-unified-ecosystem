#!/usr/bin/env python3
"""
PyHeart Workflow Engine Integration Test Script
Tests the BrainSAIT PyHeart integration without requiring external package installation
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_pyheart_imports():
    """Test PyHeart integration imports"""
    try:
        # Test main PyHeart integration
        from services.communication.integrations.pyheart_integration import (
            PyHeartHealthcareWorkflowEngine,
            HealthcareWorkflowDefinition,
            WorkflowTrigger,
            WorkflowStep,
            WorkflowEventType,
            HealthcareWorkflowType,
            WorkflowState
        )
        logger.info("✅ PyHeart integration imports successful")
        
        # Test workflow definitions
        from services.communication.integrations.workflow_definitions import (
            HealthcareWorkflowTemplates
        )
        logger.info("✅ Workflow definitions imports successful")
        
        # Test workflow orchestrator
        from services.communication.workflow_orchestrator import (
            CommunicationWorkflowOrchestrator
        )
        logger.info("✅ Workflow orchestrator imports successful")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def test_workflow_templates():
    """Test workflow template creation"""
    try:
        from services.communication.integrations.workflow_definitions import (
            HealthcareWorkflowTemplates
        )
        
        # Test patient onboarding workflow
        onboarding_workflow = HealthcareWorkflowTemplates.create_patient_onboarding_workflow()
        logger.info(f"✅ Patient onboarding workflow created: {onboarding_workflow.workflow_id}")
        
        # Test chronic disease management workflow
        chronic_workflow = HealthcareWorkflowTemplates.create_chronic_disease_management_workflow()
        logger.info(f"✅ Chronic disease workflow created: {chronic_workflow.workflow_id}")
        
        # Test post-operative workflow
        post_op_workflow = HealthcareWorkflowTemplates.create_post_operative_workflow()
        logger.info(f"✅ Post-operative workflow created: {post_op_workflow.workflow_id}")
        
        # Test emergency response workflow
        emergency_workflow = HealthcareWorkflowTemplates.create_emergency_response_workflow()
        logger.info(f"✅ Emergency response workflow created: {emergency_workflow.workflow_id}")
        
        # Test get all templates
        all_templates = HealthcareWorkflowTemplates.get_all_workflow_templates()
        logger.info(f"✅ All workflow templates retrieved: {len(all_templates)} templates")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow template test failed: {e}")
        return False

async def test_pyheart_engine_initialization():
    """Test PyHeart engine initialization without external dependencies"""
    try:
        from services.communication.integrations.pyheart_integration import (
            PyHeartHealthcareWorkflowEngine
        )
        
        # Mock the required services for testing
        class MockCommunicationService:
            def __init__(self):
                pass
        
        class MockHealthcareIntegrator:
            def __init__(self):
                pass
        
        class MockNPHIESCompliance:
            def __init__(self):
                pass
        
        # Initialize PyHeart engine with mock services
        mock_comm_service = MockCommunicationService()
        mock_integrator = MockHealthcareIntegrator()
        mock_compliance = MockNPHIESCompliance()
        
        engine = PyHeartHealthcareWorkflowEngine(
            communication_service=mock_comm_service,
            healthcare_integrator=mock_integrator,
            nphies_compliance=mock_compliance
        )
        
        logger.info("✅ PyHeart workflow engine initialized successfully")
        logger.info(f"✅ Engine configuration: {engine.config}")
        logger.info(f"✅ Available actions: {list(engine.actions.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PyHeart engine initialization failed: {e}")
        return False

async def test_workflow_validation():
    """Test workflow definition validation"""
    try:
        from services.communication.integrations.pyheart_integration import (
            PyHeartHealthcareWorkflowEngine
        )
        from services.communication.integrations.workflow_definitions import (
            HealthcareWorkflowTemplates
        )
        
        # Mock services
        class MockService:
            pass
        
        engine = PyHeartHealthcareWorkflowEngine(
            communication_service=MockService(),
            healthcare_integrator=MockService(),
            nphies_compliance=MockService()
        )
        
        # Test workflow validation with a sample workflow
        sample_workflow = HealthcareWorkflowTemplates.create_patient_onboarding_workflow()
        
        validation_result = await engine._validate_workflow_definition(sample_workflow)
        
        if validation_result["valid"]:
            logger.info("✅ Workflow validation successful")
            logger.info(f"✅ Validated workflow: {sample_workflow.workflow_id}")
        else:
            logger.warning(f"⚠️  Workflow validation failed: {validation_result['errors']}")
        
        return validation_result["valid"]
        
    except Exception as e:
        logger.error(f"❌ Workflow validation test failed: {e}")
        return False

async def test_arabic_support():
    """Test Arabic language support in workflows"""
    try:
        from arabic_reshaper import reshape
        from bidi.algorithm import get_display
        
        # Test Arabic text processing
        arabic_text = "مرحبا بك في منصة برين سايت للرعاية الصحية"
        reshaped_text = reshape(arabic_text)
        display_text = get_display(reshaped_text)
        
        logger.info("✅ Arabic text processing libraries working")
        logger.info(f"✅ Original: {arabic_text}")
        logger.info(f"✅ Processed: {display_text}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Arabic support libraries missing: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Arabic support test failed: {e}")
        return False

async def test_workflow_orchestrator_integration():
    """Test integration with the main workflow orchestrator"""
    try:
        from services.communication.workflow_orchestrator import (
            CommunicationWorkflowOrchestrator,
            WorkflowExecution,
            WorkflowStatus
        )
        
        # Test WorkflowExecution creation
        test_execution = WorkflowExecution(
            execution_id="test_execution_001",
            workflow_type="pre_visit",  # Using string instead of enum for simple test
            patient_id="patient_123"
        )
        
        logger.info("✅ Workflow execution object created")
        logger.info(f"✅ Execution ID: {test_execution.execution_id}")
        logger.info(f"✅ Status: {test_execution.status}")
        logger.info(f"✅ Created at: {test_execution.created_at}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow orchestrator integration test failed: {e}")
        return False

async def test_healthcare_workflow_types():
    """Test healthcare workflow type definitions"""
    try:
        from services.communication.integrations.pyheart_integration import (
            HealthcareWorkflowType,
            WorkflowEventType,
            WorkflowState
        )
        
        # Test workflow types
        workflow_types = list(HealthcareWorkflowType)
        logger.info(f"✅ Healthcare workflow types: {[wt.value for wt in workflow_types]}")
        
        # Test event types
        event_types = list(WorkflowEventType)
        logger.info(f"✅ Workflow event types: {[et.value for et in event_types]}")
        
        # Test workflow states
        workflow_states = list(WorkflowState)
        logger.info(f"✅ Workflow states: {[ws.value for ws in workflow_states]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Healthcare workflow types test failed: {e}")
        return False

async def run_integration_verification():
    """Run complete PyHeart integration verification"""
    logger.info("🚀 Starting PyHeart Workflow Engine Integration Verification")
    logger.info("=" * 80)
    
    test_results = {}
    
    # Test 1: Import verification
    logger.info("🔍 Test 1: PyHeart Integration Imports")
    test_results["imports"] = await test_pyheart_imports()
    
    # Test 2: Workflow templates
    logger.info("\n🔍 Test 2: Workflow Template Creation")
    test_results["templates"] = await test_workflow_templates()
    
    # Test 3: Engine initialization
    logger.info("\n🔍 Test 3: PyHeart Engine Initialization")
    test_results["engine_init"] = await test_pyheart_engine_initialization()
    
    # Test 4: Workflow validation
    logger.info("\n🔍 Test 4: Workflow Definition Validation")
    test_results["validation"] = await test_workflow_validation()
    
    # Test 5: Arabic support
    logger.info("\n🔍 Test 5: Arabic Language Support")
    test_results["arabic"] = await test_arabic_support()
    
    # Test 6: Orchestrator integration
    logger.info("\n🔍 Test 6: Workflow Orchestrator Integration")
    test_results["orchestrator"] = await test_workflow_orchestrator_integration()
    
    # Test 7: Healthcare workflow types
    logger.info("\n🔍 Test 7: Healthcare Workflow Types")
    test_results["workflow_types"] = await test_healthcare_workflow_types()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📋 INTEGRATION VERIFICATION SUMMARY")
    logger.info("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper()}: {status}")
    
    logger.info(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - PyHeart integration is fully functional!")
        return True
    else:
        logger.warning(f"⚠️  {total_tests - passed_tests} tests failed - PyHeart integration needs attention")
        return False

if __name__ == "__main__":
    # Run the integration verification
    result = asyncio.run(run_integration_verification())
    sys.exit(0 if result else 1)