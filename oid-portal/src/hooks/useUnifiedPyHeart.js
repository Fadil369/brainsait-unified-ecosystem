/**
 * useUnifiedPyHeart.js
 * 
 * BRAINSAIT UNIFIED PYHEART WORKFLOW AUTOMATION HOOK
 * Custom hook for integrated PyHeart workflow management and automation
 * 
 * CAPABILITIES:
 * - Healthcare workflow automation
 * - Real-time workflow progress tracking
 * - NPHIES claims workflow integration
 * - Arabic language workflow support
 * - Emergency response automation
 * - Patient communication workflows
 * - Revenue cycle management automation
 * - Medical coding workflow assistance
 * 
 * INTEGRATION FEATURES:
 * - PyBrain AI-powered workflow optimization
 * - FHIR R4 workflow compliance
 * - Arabic RTL workflow interfaces
 * - Real-time workflow status updates
 * - Workflow performance metrics
 * - Cultural context-aware automation
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useUnifiedHealthcare } from '../contexts/UnifiedHealthcareContext';
import { useLanguage } from './useLanguage';
import { useUnifiedPyBrain } from './useUnifiedPyBrain';

// PyHeart Workflow Types
const WORKFLOW_TYPES = {
  PATIENT_REGISTRATION: 'patient_registration',
  NPHIES_CLAIMS: 'nphies_claims',
  EMERGENCY_RESPONSE: 'emergency_response',
  COMMUNICATION: 'communication',
  REVENUE_CYCLE: 'revenue_cycle',
  MEDICAL_CODING: 'medical_coding',
  COMPLIANCE_CHECK: 'compliance_check',
  DATA_VALIDATION: 'data_validation',
  APPOINTMENT_SCHEDULING: 'appointment_scheduling',
  LABORATORY_INTEGRATION: 'laboratory_integration'
};

// Workflow Status Types
const WORKFLOW_STATUS = {
  PENDING: 'pending',
  INITIATED: 'initiated',
  IN_PROGRESS: 'in_progress',
  WAITING_INPUT: 'waiting_input',
  AI_PROCESSING: 'ai_processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  REQUIRES_APPROVAL: 'requires_approval',
  ESCALATED: 'escalated'
};

// Workflow Priority Levels
const WORKFLOW_PRIORITY = {
  LOW: 'low',
  NORMAL: 'normal',
  HIGH: 'high',
  URGENT: 'urgent',
  CRITICAL: 'critical',
  EMERGENCY: 'emergency'
};

// PyHeart Automation Capabilities
const AUTOMATION_CAPABILITIES = {
  AUTO_VALIDATION: 'auto_validation',
  SMART_ROUTING: 'smart_routing',
  PREDICTIVE_ANALYSIS: 'predictive_analysis',
  ANOMALY_DETECTION: 'anomaly_detection',
  AUTO_COMPLETION: 'auto_completion',
  INTELLIGENT_ESCALATION: 'intelligent_escalation',
  CULTURAL_ADAPTATION: 'cultural_adaptation',
  LANGUAGE_OPTIMIZATION: 'language_optimization'
};

// Performance Thresholds for Workflows
const PERFORMANCE_THRESHOLDS = {
  RESPONSE_TIME_WARNING: 5000, // 5 seconds
  RESPONSE_TIME_ERROR: 15000,  // 15 seconds
  WORKFLOW_TIMEOUT: 300000,    // 5 minutes
  MAX_CONCURRENT_WORKFLOWS: 10,
  CACHE_TTL: 600000           // 10 minutes
};

/**
 * useUnifiedPyHeart Hook
 * 
 * @param {Object} options - Configuration options
 * @param {boolean} options.enabled - Enable/disable PyHeart workflows
 * @param {string} options.context - Healthcare context (oid_tree, patient_portal, etc.)
 * @param {string} options.culturalContext - Cultural context for workflows
 * @param {boolean} options.enableAutomation - Enable AI-powered automation
 * @param {boolean} options.enableRealTimeUpdates - Enable real-time workflow updates
 * @returns {Object} PyHeart workflow interface and utilities
 */
export const useUnifiedPyHeart = ({
  enabled = true,
  context = 'healthcare',
  culturalContext = 'SAUDI_ARABIA',
  enableAutomation = true,
  enableRealTimeUpdates = true
} = {}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { 
    callUnifiedAPI, 
    systemStatus,
    user,
    performance 
  } = useUnifiedHealthcare();
  
  const { 
    isAIReady, 
    getAIInsights,
    subscribeToAIInsights,
    processArabicText 
  } = useUnifiedPyBrain({
    enabled: enableAutomation,
    context: 'pyheart_workflows',
    culturalContext,
    enableCaching: true
  });

  // PyHeart State Management
  const [pyHeartState, setPyHeartState] = useState({
    isReady: false,
    isProcessing: false,
    isConnected: false,
    activeWorkflows: new Map(),
    workflowQueue: [],
    automationEnabled: enableAutomation,
    lastActivity: null,
    errorCount: 0,
    successCount: 0,
    avgProcessingTime: 0
  });

  // Workflow Cache and Queue Management
  const workflowCache = useRef(new Map());
  const performanceMetrics = useRef({
    totalWorkflows: 0,
    successfulWorkflows: 0,
    failedWorkflows: 0,
    totalProcessingTime: 0,
    concurrentWorkflows: 0,
    automationSavings: 0
  });

  // WebSocket connection for real-time workflow updates
  const wsConnection = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Initialize PyHeart workflow engine
  useEffect(() => {
    if (!enabled) return;

    const initializePyHeart = async () => {
      try {
        setPyHeartState(prev => ({ ...prev, isProcessing: true }));

        // Check system readiness
        if (systemStatus.status !== 'operational' && systemStatus.status !== 'offline') {
          console.warn('System not ready for PyHeart initialization');
          return;
        }

        // Initialize workflow engine
        const initResponse = await callUnifiedAPI('workflow_engine', 'initialize', {
          workflowTypes: Object.values(WORKFLOW_TYPES),
          automationCapabilities: Object.values(AUTOMATION_CAPABILITIES),
          language: currentLanguage,
          culturalContext,
          enableAutomation,
          userContext: {
            role: user.role,
            permissions: user.permissions,
            preferences: user.preferences
          }
        });

        if (initResponse.success) {
          setPyHeartState(prev => ({
            ...prev,
            isReady: true,
            isConnected: true,
            automationEnabled: enableAutomation && initResponse.data.automationAvailable
          }));

          // Initialize WebSocket for real-time updates
          if (enableRealTimeUpdates) {
            initializeWorkflowWebSocket();
          }
        }

      } catch (error) {
        console.error('PyHeart workflow initialization failed:', error);
        setPyHeartState(prev => ({
          ...prev,
          isReady: false,
          isConnected: false,
          errorCount: prev.errorCount + 1
        }));
      } finally {
        setPyHeartState(prev => ({ ...prev, isProcessing: false }));
      }
    };

    initializePyHeart();

    // Cleanup function
    return () => {
      if (wsConnection.current) {
        wsConnection.current.close();
      }
    };
  }, [enabled, currentLanguage, culturalContext, enableAutomation, callUnifiedAPI, systemStatus.status, user]);

  // Initialize WebSocket connection for real-time workflow updates
  const initializeWorkflowWebSocket = useCallback(() => {
    if (wsConnection.current) return;

    try {
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/workflows/${user.id}`;
      wsConnection.current = new WebSocket(wsUrl);

      wsConnection.current.onopen = () => {
        console.log('PyHeart workflow WebSocket connected');
        setPyHeartState(prev => ({ ...prev, isConnected: true }));
        reconnectAttempts.current = 0;
      };

      wsConnection.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleRealTimeWorkflowUpdate(data);
        } catch (error) {
          console.error('Failed to parse workflow WebSocket message:', error);
        }
      };

      wsConnection.current.onclose = () => {
        console.log('PyHeart workflow WebSocket disconnected');
        setPyHeartState(prev => ({ ...prev, isConnected: false }));
        
        // Attempt reconnection
        if (reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current += 1;
            initializeWorkflowWebSocket();
          }, Math.pow(2, reconnectAttempts.current) * 1000);
        }
      };

      wsConnection.current.onerror = (error) => {
        console.error('PyHeart workflow WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to initialize PyHeart workflow WebSocket:', error);
    }
  }, [user.id]);

  // Handle real-time workflow updates
  const handleRealTimeWorkflowUpdate = useCallback((data) => {
    const { type, payload, timestamp } = data;

    switch (type) {
      case 'workflow_status_update':
        setPyHeartState(prev => {
          const updatedWorkflows = new Map(prev.activeWorkflows);
          updatedWorkflows.set(payload.workflowId, {
            ...updatedWorkflows.get(payload.workflowId),
            status: payload.status,
            progress: payload.progress,
            lastUpdate: timestamp,
            message: payload.message,
            message_ar: payload.message_ar
          });
          
          return {
            ...prev,
            activeWorkflows: updatedWorkflows,
            lastActivity: timestamp
          };
        });
        break;

      case 'workflow_completed':
        setPyHeartState(prev => {
          const updatedWorkflows = new Map(prev.activeWorkflows);
          const workflow = updatedWorkflows.get(payload.workflowId);
          
          if (workflow) {
            // Move to completed and remove from active
            updatedWorkflows.delete(payload.workflowId);
            performanceMetrics.current.successfulWorkflows += 1;
            
            // Calculate processing time
            const processingTime = timestamp - workflow.startTime;
            performanceMetrics.current.totalProcessingTime += processingTime;
          }
          
          return {
            ...prev,
            activeWorkflows: updatedWorkflows,
            successCount: prev.successCount + 1,
            avgProcessingTime: performanceMetrics.current.totalProcessingTime / performanceMetrics.current.successfulWorkflows
          };
        });
        break;

      case 'workflow_failed':
        setPyHeartState(prev => {
          const updatedWorkflows = new Map(prev.activeWorkflows);
          updatedWorkflows.delete(payload.workflowId);
          performanceMetrics.current.failedWorkflows += 1;
          
          return {
            ...prev,
            activeWorkflows: updatedWorkflows,
            errorCount: prev.errorCount + 1
          };
        });
        break;

      case 'automation_insight':
        // Handle automation insights from PyBrain
        if (isAIReady && payload.context === context) {
          window.dispatchEvent(new CustomEvent('pyheart-automation-insight', {
            detail: payload
          }));
        }
        break;

      default:
        console.log('Unknown workflow update type:', type);
    }
  }, [context, isAIReady]);

  // Core workflow initiation function
  const initiateWorkflow = useCallback(async (workflowType, workflowData, options = {}) => {
    if (!enabled || !pyHeartState.isReady) {
      throw new Error('PyHeart workflow engine not ready');
    }

    const startTime = Date.now();
    const workflowId = `${workflowType}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Check concurrent workflow limit
    if (performanceMetrics.current.concurrentWorkflows >= PERFORMANCE_THRESHOLDS.MAX_CONCURRENT_WORKFLOWS) {
      throw new Error('Maximum concurrent workflows exceeded');
    }

    try {
      performanceMetrics.current.concurrentWorkflows += 1;
      performanceMetrics.current.totalWorkflows += 1;

      setPyHeartState(prev => ({ 
        ...prev, 
        isProcessing: true,
        lastActivity: workflowId
      }));

      // Prepare workflow payload with cultural context
      const workflowPayload = {
        workflowId,
        workflowType,
        data: {
          ...workflowData,
          language: currentLanguage,
          culturalContext,
          isRTL,
          userContext: {
            role: user.role,
            preferences: user.preferences
          },
          automationEnabled: pyHeartState.automationEnabled,
          timestamp: new Date().toISOString()
        },
        options: {
          ...options,
          priority: options.priority || WORKFLOW_PRIORITY.NORMAL,
          timeout: options.timeout || PERFORMANCE_THRESHOLDS.WORKFLOW_TIMEOUT
        }
      };

      // AI-powered workflow optimization
      if (isAIReady && pyHeartState.automationEnabled) {
        try {
          const aiOptimization = await getAIInsights('workflow_optimization', {
            workflowType,
            workflowData,
            context,
            language: currentLanguage
          });
          
          if (aiOptimization && aiOptimization.recommendations) {
            workflowPayload.aiRecommendations = aiOptimization.recommendations;
            workflowPayload.optimizationScore = aiOptimization.confidence_score;
          }
        } catch (aiError) {
          console.warn('AI workflow optimization failed, proceeding without:', aiError);
        }
      }

      const response = await callUnifiedAPI('workflow_engine', 'initiate_workflow', workflowPayload);

      if (response.success) {
        // Add to active workflows
        setPyHeartState(prev => {
          const updatedWorkflows = new Map(prev.activeWorkflows);
          updatedWorkflows.set(workflowId, {
            id: workflowId,
            type: workflowType,
            status: WORKFLOW_STATUS.INITIATED,
            progress: 0,
            startTime,
            data: workflowData,
            options,
            lastUpdate: Date.now()
          });
          
          return {
            ...prev,
            activeWorkflows: updatedWorkflows
          };
        });

        return {
          workflowId,
          status: WORKFLOW_STATUS.INITIATED,
          estimatedDuration: response.data.estimatedDuration,
          nextSteps: response.data.nextSteps
        };
      } else {
        throw new Error(response.error || 'Workflow initiation failed');
      }

    } catch (error) {
      performanceMetrics.current.failedWorkflows += 1;
      
      setPyHeartState(prev => ({
        ...prev,
        errorCount: prev.errorCount + 1
      }));

      console.error('PyHeart workflow initiation failed:', error);
      throw error;

    } finally {
      performanceMetrics.current.concurrentWorkflows -= 1;
      setPyHeartState(prev => ({ ...prev, isProcessing: false }));
    }
  }, [
    enabled, 
    pyHeartState.isReady, 
    pyHeartState.automationEnabled,
    currentLanguage, 
    culturalContext, 
    isRTL, 
    user, 
    callUnifiedAPI,
    isAIReady,
    getAIInsights,
    context
  ]);

  // Workflow-specific functions
  const initiatePatientRegistrationWorkflow = useCallback(async (patientData, options = {}) => {
    return initiateWorkflow(WORKFLOW_TYPES.PATIENT_REGISTRATION, patientData, {
      ...options,
      automationCapabilities: [
        AUTOMATION_CAPABILITIES.AUTO_VALIDATION,
        AUTOMATION_CAPABILITIES.CULTURAL_ADAPTATION
      ]
    });
  }, [initiateWorkflow]);

  const initiateNPHIESClaimsWorkflow = useCallback(async (claimsData, options = {}) => {
    return initiateWorkflow(WORKFLOW_TYPES.NPHIES_CLAIMS, claimsData, {
      ...options,
      priority: WORKFLOW_PRIORITY.HIGH,
      automationCapabilities: [
        AUTOMATION_CAPABILITIES.AUTO_VALIDATION,
        AUTOMATION_CAPABILITIES.ANOMALY_DETECTION,
        AUTOMATION_CAPABILITIES.PREDICTIVE_ANALYSIS
      ]
    });
  }, [initiateWorkflow]);

  const initiateEmergencyResponseWorkflow = useCallback(async (emergencyData, options = {}) => {
    return initiateWorkflow(WORKFLOW_TYPES.EMERGENCY_RESPONSE, emergencyData, {
      ...options,
      priority: WORKFLOW_PRIORITY.EMERGENCY,
      automationCapabilities: [
        AUTOMATION_CAPABILITIES.SMART_ROUTING,
        AUTOMATION_CAPABILITIES.INTELLIGENT_ESCALATION
      ]
    });
  }, [initiateWorkflow]);

  const initiateCommunicationWorkflow = useCallback(async (communicationData, options = {}) => {
    return initiateWorkflow(WORKFLOW_TYPES.COMMUNICATION, communicationData, {
      ...options,
      automationCapabilities: [
        AUTOMATION_CAPABILITIES.LANGUAGE_OPTIMIZATION,
        AUTOMATION_CAPABILITIES.CULTURAL_ADAPTATION
      ]
    });
  }, [initiateWorkflow]);

  const initiateMedicalCodingWorkflow = useCallback(async (codingData, options = {}) => {
    return initiateWorkflow(WORKFLOW_TYPES.MEDICAL_CODING, codingData, {
      ...options,
      automationCapabilities: [
        AUTOMATION_CAPABILITIES.AUTO_COMPLETION,
        AUTOMATION_CAPABILITIES.PREDICTIVE_ANALYSIS
      ]
    });
  }, [initiateWorkflow]);

  // Workflow management functions
  const getWorkflowStatus = useCallback((workflowId) => {
    return pyHeartState.activeWorkflows.get(workflowId) || null;
  }, [pyHeartState.activeWorkflows]);

  const cancelWorkflow = useCallback(async (workflowId) => {
    try {
      const response = await callUnifiedAPI('workflow_engine', 'cancel_workflow', {
        workflowId
      });

      if (response.success) {
        setPyHeartState(prev => {
          const updatedWorkflows = new Map(prev.activeWorkflows);
          updatedWorkflows.delete(workflowId);
          return {
            ...prev,
            activeWorkflows: updatedWorkflows
          };
        });
      }

      return response;
    } catch (error) {
      console.error('Failed to cancel workflow:', error);
      throw error;
    }
  }, [callUnifiedAPI]);

  const pauseWorkflow = useCallback(async (workflowId) => {
    try {
      return await callUnifiedAPI('workflow_engine', 'pause_workflow', {
        workflowId
      });
    } catch (error) {
      console.error('Failed to pause workflow:', error);
      throw error;
    }
  }, [callUnifiedAPI]);

  const resumeWorkflow = useCallback(async (workflowId) => {
    try {
      return await callUnifiedAPI('workflow_engine', 'resume_workflow', {
        workflowId
      });
    } catch (error) {
      console.error('Failed to resume workflow:', error);
      throw error;
    }
  }, [callUnifiedAPI]);

  // Automation insights subscription
  const subscribeToAutomationInsights = useCallback((callback) => {
    const handleInsight = (event) => {
      callback(event.detail);
    };

    window.addEventListener('pyheart-automation-insight', handleInsight);
    
    return () => {
      window.removeEventListener('pyheart-automation-insight', handleInsight);
    };
  }, []);

  // Performance and diagnostics
  const getWorkflowPerformanceMetrics = useCallback(() => {
    return {
      ...performanceMetrics.current,
      pyHeartState,
      activeWorkflowCount: pyHeartState.activeWorkflows.size,
      connectionStatus: wsConnection.current?.readyState || 'disconnected',
      cacheSize: workflowCache.current.size
    };
  }, [pyHeartState]);

  const clearWorkflowCache = useCallback(() => {
    workflowCache.current.clear();
    console.log('PyHeart workflow cache cleared');
  }, []);

  // Memoized return object
  const pyHeartInterface = useMemo(() => ({
    // State
    pyHeartState,
    isPyHeartReady: pyHeartState.isReady && enabled,
    isProcessing: pyHeartState.isProcessing,
    isConnected: pyHeartState.isConnected,
    activeWorkflows: Array.from(pyHeartState.activeWorkflows.values()),
    automationEnabled: pyHeartState.automationEnabled,

    // Core workflow functions
    initiateWorkflow,
    initiatePatientRegistrationWorkflow,
    initiateNPHIESClaimsWorkflow,
    initiateEmergencyResponseWorkflow,
    initiateCommunicationWorkflow,
    initiateMedicalCodingWorkflow,

    // Workflow management
    getWorkflowStatus,
    cancelWorkflow,
    pauseWorkflow,
    resumeWorkflow,

    // Real-time and automation
    subscribeToAutomationInsights,

    // Utilities
    getWorkflowPerformanceMetrics,
    clearWorkflowCache,

    // Constants
    WORKFLOW_TYPES,
    WORKFLOW_STATUS,
    WORKFLOW_PRIORITY,
    AUTOMATION_CAPABILITIES
  }), [
    pyHeartState,
    enabled,
    initiateWorkflow,
    initiatePatientRegistrationWorkflow,
    initiateNPHIESClaimsWorkflow,
    initiateEmergencyResponseWorkflow,
    initiateCommunicationWorkflow,
    initiateMedicalCodingWorkflow,
    getWorkflowStatus,
    cancelWorkflow,
    pauseWorkflow,
    resumeWorkflow,
    subscribeToAutomationInsights,
    getWorkflowPerformanceMetrics,
    clearWorkflowCache
  ]);

  return pyHeartInterface;
};

export default useUnifiedPyHeart;