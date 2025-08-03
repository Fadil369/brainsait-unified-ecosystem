/**
 * useUnifiedPyBrain.js
 * 
 * BRAINSAIT UNIFIED PYBRAIN AI INTEGRATION HOOK
 * Custom hook for integrated PyBrain AI capabilities across the frontend
 * 
 * CAPABILITIES:
 * - Real-time AI insights and predictions
 * - Arabic cultural context awareness
 * - Healthcare-specific AI models
 * - Form assistance and validation
 * - Intelligent recommendations
 * - Performance optimization
 * - Error handling and fallbacks
 * 
 * INTEGRATION FEATURES:
 * - NPHIES claims analysis
 * - Medical coding assistance
 * - Arabic NLP processing
 * - Fraud detection
 * - Duplicate identification
 * - Revenue cycle optimization
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useUnifiedHealthcare } from '../contexts/UnifiedHealthcareContext';
import { useLanguage } from './useLanguage';

// PyBrain AI Models Configuration
const AI_MODELS = {
  HEALTHCARE_INSIGHTS: 'healthcare_insights_v2',
  ARABIC_NLP: 'arabic_nlp_v1',
  CLAIMS_ANALYSIS: 'claims_analysis_v3',
  FRAUD_DETECTION: 'fraud_detection_v2',
  FORM_ASSISTANCE: 'form_assistance_v1',
  REVENUE_OPTIMIZATION: 'revenue_optimization_v1',
  CODING_ASSISTANT: 'medical_coding_v2'
};

// AI Request Types
const AI_REQUEST_TYPES = {
  INSIGHT: 'insight',
  PREDICTION: 'prediction',
  ANALYSIS: 'analysis',
  ASSISTANCE: 'assistance',
  VALIDATION: 'validation',
  RECOMMENDATION: 'recommendation'
};

// Cultural Context Mappings
const CULTURAL_CONTEXTS = {
  SAUDI_ARABIA: {
    language: 'ar',
    calendar: 'hijri',
    currency: 'SAR',
    timezone: 'Asia/Riyadh',
    cultural_norms: ['conservative', 'family_oriented', 'religious'],
    healthcare_preferences: ['gender_segregation', 'islamic_medicine', 'family_involvement']
  },
  GULF_REGION: {
    language: 'ar',
    cultural_norms: ['traditional', 'hospitality', 'respect_for_elders'],
    healthcare_preferences: ['private_healthcare', 'specialist_referrals']
  }
};

// Performance Monitoring
const PERFORMANCE_THRESHOLDS = {
  RESPONSE_TIME_WARNING: 3000, // 3 seconds
  RESPONSE_TIME_ERROR: 10000,  // 10 seconds
  CACHE_TTL: 300000,           // 5 minutes
  MAX_CONCURRENT_REQUESTS: 5
};

/**
 * useUnifiedPyBrain Hook
 * 
 * @param {Object} options - Configuration options
 * @param {boolean} options.enabled - Enable/disable AI features
 * @param {string} options.context - Healthcare context (nphies, rcm, training, etc.)
 * @param {string} options.culturalContext - Cultural context for AI responses
 * @param {boolean} options.enableCaching - Enable response caching
 * @param {boolean} options.enablePerformanceMonitoring - Enable performance tracking
 * @returns {Object} PyBrain AI interface and utilities
 */
export const useUnifiedPyBrain = ({
  enabled = true,
  context = 'healthcare',
  culturalContext = 'SAUDI_ARABIA',
  enableCaching = true,
  enablePerformanceMonitoring = true
} = {}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { 
    callUnifiedAPI, 
    systemStatus,
    user,
    performance 
  } = useUnifiedHealthcare();

  // AI State Management
  const [aiState, setAIState] = useState({
    isReady: false,
    isProcessing: false,
    isConnected: false,
    currentModel: null,
    lastRequest: null,
    errorCount: 0,
    successCount: 0,
    avgResponseTime: 0
  });

  // Request Queue and Cache
  const requestQueue = useRef([]);
  const responseCache = useRef(new Map());
  const performanceMetrics = useRef({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    totalResponseTime: 0,
    concurrentRequests: 0
  });

  // WebSocket connection for real-time AI
  const wsConnection = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Initialize PyBrain AI connection
  useEffect(() => {
    if (!enabled) return;

    const initializeAI = async () => {
      try {
        setAIState(prev => ({ ...prev, isProcessing: true }));

        // Check system status first
        if (systemStatus.status !== 'operational' && systemStatus.status !== 'offline') {
          console.warn('System not ready for AI initialization');
          return;
        }

        // Initialize AI models
        const initResponse = await callUnifiedAPI('ai_analytics', 'initialize', {
          models: Object.values(AI_MODELS),
          language: currentLanguage,
          culturalContext: CULTURAL_CONTEXTS[culturalContext],
          userContext: {
            role: user.role,
            permissions: user.permissions,
            preferences: user.preferences
          }
        });

        if (initResponse.success) {
          setAIState(prev => ({
            ...prev,
            isReady: true,
            isConnected: true,
            currentModel: AI_MODELS.HEALTHCARE_INSIGHTS
          }));

          // Initialize WebSocket for real-time AI
          if (enablePerformanceMonitoring) {
            initializeWebSocket();
          }
        }

      } catch (error) {
        console.error('PyBrain AI initialization failed:', error);
        setAIState(prev => ({
          ...prev,
          isReady: false,
          isConnected: false,
          errorCount: prev.errorCount + 1
        }));
      } finally {
        setAIState(prev => ({ ...prev, isProcessing: false }));
      }
    };

    initializeAI();

    // Cleanup function
    return () => {
      if (wsConnection.current) {
        wsConnection.current.close();
      }
    };
  }, [enabled, currentLanguage, culturalContext, callUnifiedAPI, systemStatus.status, user]);

  // Initialize WebSocket connection for real-time AI
  const initializeWebSocket = useCallback(() => {
    if (wsConnection.current) return;

    try {
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/ai/${user.id}`;
      wsConnection.current = new WebSocket(wsUrl);

      wsConnection.current.onopen = () => {
        console.log('PyBrain AI WebSocket connected');
        setAIState(prev => ({ ...prev, isConnected: true }));
        reconnectAttempts.current = 0;
      };

      wsConnection.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleRealTimeAIUpdate(data);
        } catch (error) {
          console.error('Failed to parse AI WebSocket message:', error);
        }
      };

      wsConnection.current.onclose = () => {
        console.log('PyBrain AI WebSocket disconnected');
        setAIState(prev => ({ ...prev, isConnected: false }));
        
        // Attempt reconnection
        if (reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current += 1;
            initializeWebSocket();
          }, Math.pow(2, reconnectAttempts.current) * 1000);
        }
      };

      wsConnection.current.onerror = (error) => {
        console.error('PyBrain AI WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to initialize PyBrain AI WebSocket:', error);
    }
  }, [user.id]);

  // Handle real-time AI updates
  const handleRealTimeAIUpdate = useCallback((data) => {
    const { type, payload, timestamp } = data;

    switch (type) {
      case 'model_update':
        setAIState(prev => ({
          ...prev,
          currentModel: payload.model,
          lastRequest: timestamp
        }));
        break;

      case 'performance_metrics':
        performanceMetrics.current = {
          ...performanceMetrics.current,
          ...payload
        };
        break;

      case 'insight_ready':
        // Handle real-time insights
        if (payload.context === context) {
          // Trigger insight callback if registered
          window.dispatchEvent(new CustomEvent('pybrain-insight', {
            detail: payload
          }));
        }
        break;

      default:
        console.log('Unknown AI update type:', type);
    }
  }, [context]);

  // Cache management
  const getCachedResponse = useCallback((key) => {
    if (!enableCaching) return null;
    
    const cached = responseCache.current.get(key);
    if (cached && Date.now() - cached.timestamp < PERFORMANCE_THRESHOLDS.CACHE_TTL) {
      return cached.data;
    }
    
    responseCache.current.delete(key);
    return null;
  }, [enableCaching]);

  const setCachedResponse = useCallback((key, data) => {
    if (!enableCaching) return;
    
    responseCache.current.set(key, {
      data,
      timestamp: Date.now()
    });

    // Cleanup old cache entries
    if (responseCache.current.size > 100) {
      const entries = Array.from(responseCache.current.entries());
      entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
      
      // Remove oldest 20 entries
      for (let i = 0; i < 20; i++) {
        responseCache.current.delete(entries[i][0]);
      }
    }
  }, [enableCaching]);

  // Core AI request function
  const makeAIRequest = useCallback(async (requestType, model, payload, options = {}) => {
    if (!enabled || !aiState.isReady) {
      throw new Error('PyBrain AI not ready');
    }

    const startTime = Date.now();
    const requestId = `${requestType}_${model}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Check cache first
    const cacheKey = `${model}_${JSON.stringify(payload)}`;
    const cachedResponse = getCachedResponse(cacheKey);
    if (cachedResponse && !options.forceRefresh) {
      return cachedResponse;
    }

    // Check concurrent request limit
    if (performanceMetrics.current.concurrentRequests >= PERFORMANCE_THRESHOLDS.MAX_CONCURRENT_REQUESTS) {
      throw new Error('Too many concurrent AI requests');
    }

    try {
      performanceMetrics.current.concurrentRequests += 1;
      performanceMetrics.current.totalRequests += 1;

      setAIState(prev => ({ 
        ...prev, 
        isProcessing: true,
        lastRequest: requestId
      }));

      const requestPayload = {
        requestId,
        requestType,
        model,
        payload: {
          ...payload,
          language: currentLanguage,
          culturalContext: CULTURAL_CONTEXTS[culturalContext],
          userContext: {
            role: user.role,
            preferences: user.preferences
          },
          rtl: isRTL,
          timestamp: new Date().toISOString()
        },
        options
      };

      const response = await callUnifiedAPI('ai_analytics', 'process_ai_request', requestPayload);

      const responseTime = Date.now() - startTime;
      
      // Update performance metrics
      performanceMetrics.current.successfulRequests += 1;
      performanceMetrics.current.totalResponseTime += responseTime;
      
      setAIState(prev => ({
        ...prev,
        successCount: prev.successCount + 1,
        avgResponseTime: performanceMetrics.current.totalResponseTime / performanceMetrics.current.totalRequests
      }));

      // Performance warnings
      if (enablePerformanceMonitoring) {
        if (responseTime > PERFORMANCE_THRESHOLDS.RESPONSE_TIME_WARNING) {
          console.warn(`PyBrain AI slow response: ${responseTime}ms for ${requestType}`);
        }
        if (responseTime > PERFORMANCE_THRESHOLDS.RESPONSE_TIME_ERROR) {
          console.error(`PyBrain AI timeout risk: ${responseTime}ms for ${requestType}`);
        }
      }

      // Cache successful response
      if (response.success && response.data) {
        setCachedResponse(cacheKey, response.data);
      }

      return response.data;

    } catch (error) {
      performanceMetrics.current.failedRequests += 1;
      
      setAIState(prev => ({
        ...prev,
        errorCount: prev.errorCount + 1
      }));

      console.error('PyBrain AI request failed:', error);
      throw error;

    } finally {
      performanceMetrics.current.concurrentRequests -= 1;
      setAIState(prev => ({ ...prev, isProcessing: false }));
    }
  }, [
    enabled, 
    aiState.isReady, 
    currentLanguage, 
    culturalContext, 
    isRTL, 
    user, 
    callUnifiedAPI,
    getCachedResponse,
    setCachedResponse,
    enablePerformanceMonitoring
  ]);

  // Healthcare-specific AI functions
  const getAIInsights = useCallback(async (context, options = {}) => {
    return makeAIRequest(
      AI_REQUEST_TYPES.INSIGHT,
      AI_MODELS.HEALTHCARE_INSIGHTS,
      { context, ...options }
    );
  }, [makeAIRequest]);

  const analyzeHealthcareData = useCallback(async (data, analysisType = 'general') => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ANALYSIS,
      AI_MODELS.HEALTHCARE_INSIGHTS,
      { data, analysisType }
    );
  }, [makeAIRequest]);

  const processArabicText = useCallback(async (text, operation = 'analyze') => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ANALYSIS,
      AI_MODELS.ARABIC_NLP,
      { text, operation }
    );
  }, [makeAIRequest]);

  const analyzeClaims = useCallback(async (claims, options = {}) => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ANALYSIS,
      AI_MODELS.CLAIMS_ANALYSIS,
      { claims, ...options }
    );
  }, [makeAIRequest]);

  const detectFraud = useCallback(async (transactionData) => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ANALYSIS,
      AI_MODELS.FRAUD_DETECTION,
      { transactionData }
    );
  }, [makeAIRequest]);

  const getFormAssistance = useCallback(async (formType, currentData, options = {}) => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ASSISTANCE,
      AI_MODELS.FORM_ASSISTANCE,
      { formType, currentData, ...options }
    );
  }, [makeAIRequest]);

  const validateInput = useCallback(async (field, value, validationRules = {}) => {
    return makeAIRequest(
      AI_REQUEST_TYPES.VALIDATION,
      AI_MODELS.FORM_ASSISTANCE,
      { field, value, validationRules }
    );
  }, [makeAIRequest]);

  const getRevenueRecommendations = useCallback(async (revenueData, timeframe = '30d') => {
    return makeAIRequest(
      AI_REQUEST_TYPES.RECOMMENDATION,
      AI_MODELS.REVENUE_OPTIMIZATION,
      { revenueData, timeframe }
    );
  }, [makeAIRequest]);

  const getMedicalCodingAssistance = useCallback(async (medicalRecord, codingType = 'ICD10') => {
    return makeAIRequest(
      AI_REQUEST_TYPES.ASSISTANCE,
      AI_MODELS.CODING_ASSISTANT,
      { medicalRecord, codingType }
    );
  }, [makeAIRequest]);

  const getPredictiveAnalytics = useCallback(async (dataSet, predictionType, timeHorizon = '30d') => {
    return makeAIRequest(
      AI_REQUEST_TYPES.PREDICTION,
      AI_MODELS.HEALTHCARE_INSIGHTS,
      { dataSet, predictionType, timeHorizon }
    );
  }, [makeAIRequest]);

  // Batch processing for multiple AI requests
  const processBatchRequests = useCallback(async (requests) => {
    const batchId = `batch_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return makeAIRequest(
      'batch_process',
      AI_MODELS.HEALTHCARE_INSIGHTS,
      { batchId, requests }
    );
  }, [makeAIRequest]);

  // Real-time AI event subscription
  const subscribeToAIInsights = useCallback((callback) => {
    const handleInsight = (event) => {
      callback(event.detail);
    };

    window.addEventListener('pybrain-insight', handleInsight);
    
    return () => {
      window.removeEventListener('pybrain-insight', handleInsight);
    };
  }, []);

  // Performance and diagnostics
  const getAIPerformanceMetrics = useCallback(() => {
    return {
      ...performanceMetrics.current,
      aiState,
      cacheSize: responseCache.current.size,
      connectionStatus: wsConnection.current?.readyState || 'disconnected'
    };
  }, [aiState]);

  const clearAICache = useCallback(() => {
    responseCache.current.clear();
    console.log('PyBrain AI cache cleared');
  }, []);

  // Memoized return object
  const pyBrainInterface = useMemo(() => ({
    // State
    aiState,
    isAIReady: aiState.isReady && enabled,
    isProcessing: aiState.isProcessing,
    isConnected: aiState.isConnected,

    // Core AI functions
    getAIInsights,
    analyzeHealthcareData,
    processArabicText,
    analyzeClaims,
    detectFraud,
    getFormAssistance,
    validateInput,
    getRevenueRecommendations,
    getMedicalCodingAssistance,
    getPredictiveAnalytics,

    // Batch and real-time
    processBatchRequests,
    subscribeToAIInsights,

    // Utilities
    getAIPerformanceMetrics,
    clearAICache,

    // Raw request function for advanced usage
    makeAIRequest,

    // Constants
    AI_MODELS,
    AI_REQUEST_TYPES,
    CULTURAL_CONTEXTS
  }), [
    aiState,
    enabled,
    getAIInsights,
    analyzeHealthcareData,
    processArabicText,
    analyzeClaims,
    detectFraud,
    getFormAssistance,
    validateInput,
    getRevenueRecommendations,
    getMedicalCodingAssistance,
    getPredictiveAnalytics,
    processBatchRequests,
    subscribeToAIInsights,
    getAIPerformanceMetrics,
    clearAICache,
    makeAIRequest
  ]);

  return pyBrainInterface;
};

export default useUnifiedPyBrain;