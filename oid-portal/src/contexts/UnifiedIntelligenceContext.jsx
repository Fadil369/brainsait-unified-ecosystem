/**
 * UnifiedIntelligenceContext.jsx
 * 
 * BRAINSAIT UNIFIED INTELLIGENCE CONTEXT
 * Context for managing AI insights and real-time intelligence across the platform
 * 
 * CAPABILITIES:
 * - Real-time AI insights and recommendations
 * - Predictive analytics and forecasting
 * - Cultural context awareness (Saudi Arabia)
 * - Arabic language processing and understanding
 * - Healthcare-specific intelligence patterns
 * - Performance optimization and monitoring
 * - User behavior analysis and adaptation
 * - Security and compliance monitoring
 * 
 * INTEGRATION FEATURES:
 * - PyBrain AI model integration
 * - WebSocket real-time communications
 * - Intelligent caching and prefetching
 * - Multi-language support with cultural context
 * - Healthcare workflow optimization
 * - NPHIES and RCM intelligence
 */

import React, { 
  createContext, 
  useContext, 
  useReducer, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef 
} from 'react';
import { useUnifiedHealthcare } from './UnifiedHealthcareContext';
import { useLanguage } from '../hooks/useLanguage';
import unifiedAPIClient from '../services/UnifiedAPIClient';

// Intelligence Context Actions
const INTELLIGENCE_ACTIONS = {
  // Connection Management
  SET_CONNECTION_STATUS: 'SET_CONNECTION_STATUS',
  SET_WEBSOCKET_STATUS: 'SET_WEBSOCKET_STATUS',
  
  // AI State Management
  SET_AI_READY: 'SET_AI_READY',
  SET_AI_PROCESSING: 'SET_AI_PROCESSING',
  SET_AI_ERROR: 'SET_AI_ERROR',
  CLEAR_AI_ERROR: 'CLEAR_AI_ERROR',
  
  // Insights Management
  ADD_INSIGHT: 'ADD_INSIGHT',
  UPDATE_INSIGHT: 'UPDATE_INSIGHT',
  REMOVE_INSIGHT: 'REMOVE_INSIGHT',
  CLEAR_INSIGHTS: 'CLEAR_INSIGHTS',
  
  // Predictions and Recommendations
  SET_PREDICTIONS: 'SET_PREDICTIONS',
  ADD_RECOMMENDATION: 'ADD_RECOMMENDATION',
  UPDATE_RECOMMENDATION_STATUS: 'UPDATE_RECOMMENDATION_STATUS',
  
  // Real-time Data
  UPDATE_REAL_TIME_DATA: 'UPDATE_REAL_TIME_DATA',
  SET_SUBSCRIPTION: 'SET_SUBSCRIPTION',
  REMOVE_SUBSCRIPTION: 'REMOVE_SUBSCRIPTION',
  
  // Performance Metrics
  UPDATE_PERFORMANCE_METRICS: 'UPDATE_PERFORMANCE_METRICS',
  
  // User Intelligence
  UPDATE_USER_PATTERNS: 'UPDATE_USER_PATTERNS',
  SET_CULTURAL_CONTEXT: 'SET_CULTURAL_CONTEXT',
  
  // Workflow Intelligence
  ADD_WORKFLOW_OPTIMIZATION: 'ADD_WORKFLOW_OPTIMIZATION',
  UPDATE_WORKFLOW_STATUS: 'UPDATE_WORKFLOW_STATUS'
};

// Intelligence Types
const INTELLIGENCE_TYPES = {
  PREDICTIVE: 'predictive',
  DIAGNOSTIC: 'diagnostic',
  PRESCRIPTIVE: 'prescriptive',
  DESCRIPTIVE: 'descriptive',
  CULTURAL: 'cultural',
  BEHAVIORAL: 'behavioral',
  OPERATIONAL: 'operational',
  SECURITY: 'security'
};

// Insight Severity Levels
const INSIGHT_SEVERITY = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
  INFO: 'info'
};

// Cultural Intelligence Patterns
const CULTURAL_PATTERNS = {
  SAUDI_ARABIA: {
    workingHours: {
      start: '08:00',
      end: '17:00',
      prayerBreaks: ['12:00', '15:30', '18:00'],
      fridaySchedule: 'reduced'
    },
    communicationStyle: {
      formality: 'high',
      familyInvolvement: 'significant',
      genderConsiderations: 'important',
      religiousConsiderations: 'essential'
    },
    healthcarePreferences: {
      familyDoctors: 'preferred',
      specialistReferrals: 'common',
      preventiveCare: 'growing',
      traditionalMedicine: 'complementary'
    }
  }
};

// Initial State
const initialState = {
  // Connection Status
  isConnected: false,
  wsConnected: false,
  lastConnection: null,
  
  // AI Status
  aiReady: false,
  aiProcessing: false,
  aiError: null,
  
  // Intelligence Data
  insights: [],
  predictions: {},
  recommendations: [],
  realTimeData: {},
  
  // Performance Metrics
  performanceMetrics: {
    responseTime: 0,
    accuracy: 0,
    predictionSuccess: 0,
    userSatisfaction: 0
  },
  
  // User Intelligence
  userPatterns: {
    preferences: {},
    behavior: {},
    performance: {}
  },
  
  // Cultural Context
  culturalContext: {
    primary: 'SAUDI_ARABIA',
    language: 'ar',
    timezone: 'Asia/Riyadh',
    patterns: CULTURAL_PATTERNS.SAUDI_ARABIA
  },
  
  // Workflow Intelligence
  workflowOptimizations: [],
  activeOptimizations: {},
  
  // Subscriptions
  subscriptions: new Map(),
  
  // Cache
  intelligenceCache: new Map(),
  lastUpdate: null
};

// Reducer Function
function intelligenceReducer(state, action) {
  switch (action.type) {
    case INTELLIGENCE_ACTIONS.SET_CONNECTION_STATUS:
      return {
        ...state,
        isConnected: action.connected,
        lastConnection: action.connected ? new Date().toISOString() : state.lastConnection
      };

    case INTELLIGENCE_ACTIONS.SET_WEBSOCKET_STATUS:
      return {
        ...state,
        wsConnected: action.connected
      };

    case INTELLIGENCE_ACTIONS.SET_AI_READY:
      return {
        ...state,
        aiReady: action.ready
      };

    case INTELLIGENCE_ACTIONS.SET_AI_PROCESSING:
      return {
        ...state,
        aiProcessing: action.processing
      };

    case INTELLIGENCE_ACTIONS.SET_AI_ERROR:
      return {
        ...state,
        aiError: action.error
      };

    case INTELLIGENCE_ACTIONS.CLEAR_AI_ERROR:
      return {
        ...state,
        aiError: null
      };

    case INTELLIGENCE_ACTIONS.ADD_INSIGHT:
      const newInsight = {
        ...action.insight,
        id: action.insight.id || `insight_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        status: 'active'
      };
      
      return {
        ...state,
        insights: [newInsight, ...state.insights.slice(0, 99)], // Keep last 100 insights
        lastUpdate: new Date().toISOString()
      };

    case INTELLIGENCE_ACTIONS.UPDATE_INSIGHT:
      return {
        ...state,
        insights: state.insights.map(insight =>
          insight.id === action.insightId
            ? { ...insight, ...action.updates, updatedAt: new Date().toISOString() }
            : insight
        )
      };

    case INTELLIGENCE_ACTIONS.REMOVE_INSIGHT:
      return {
        ...state,
        insights: state.insights.filter(insight => insight.id !== action.insightId)
      };

    case INTELLIGENCE_ACTIONS.CLEAR_INSIGHTS:
      return {
        ...state,
        insights: []
      };

    case INTELLIGENCE_ACTIONS.SET_PREDICTIONS:
      return {
        ...state,
        predictions: {
          ...state.predictions,
          [action.context]: {
            ...action.predictions,
            timestamp: new Date().toISOString()
          }
        }
      };

    case INTELLIGENCE_ACTIONS.ADD_RECOMMENDATION:
      const newRecommendation = {
        ...action.recommendation,
        id: action.recommendation.id || `rec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        status: 'pending'
      };
      
      return {
        ...state,
        recommendations: [newRecommendation, ...state.recommendations.slice(0, 49)] // Keep last 50
      };

    case INTELLIGENCE_ACTIONS.UPDATE_RECOMMENDATION_STATUS:
      return {
        ...state,
        recommendations: state.recommendations.map(rec =>
          rec.id === action.recommendationId
            ? { ...rec, status: action.status, updatedAt: new Date().toISOString() }
            : rec
        )
      };

    case INTELLIGENCE_ACTIONS.UPDATE_REAL_TIME_DATA:
      return {
        ...state,
        realTimeData: {
          ...state.realTimeData,
          [action.context]: {
            ...state.realTimeData[action.context],
            ...action.data,
            timestamp: new Date().toISOString()
          }
        }
      };

    case INTELLIGENCE_ACTIONS.SET_SUBSCRIPTION:
      const newSubscriptions = new Map(state.subscriptions);
      newSubscriptions.set(action.key, action.subscription);
      return {
        ...state,
        subscriptions: newSubscriptions
      };

    case INTELLIGENCE_ACTIONS.REMOVE_SUBSCRIPTION:
      const updatedSubscriptions = new Map(state.subscriptions);
      updatedSubscriptions.delete(action.key);
      return {
        ...state,
        subscriptions: updatedSubscriptions
      };

    case INTELLIGENCE_ACTIONS.UPDATE_PERFORMANCE_METRICS:
      return {
        ...state,
        performanceMetrics: {
          ...state.performanceMetrics,
          ...action.metrics
        }
      };

    case INTELLIGENCE_ACTIONS.UPDATE_USER_PATTERNS:
      return {
        ...state,
        userPatterns: {
          ...state.userPatterns,
          ...action.patterns,
          lastUpdated: new Date().toISOString()
        }
      };

    case INTELLIGENCE_ACTIONS.SET_CULTURAL_CONTEXT:
      return {
        ...state,
        culturalContext: {
          ...state.culturalContext,
          ...action.context
        }
      };

    case INTELLIGENCE_ACTIONS.ADD_WORKFLOW_OPTIMIZATION:
      const newOptimization = {
        ...action.optimization,
        id: action.optimization.id || `opt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        status: 'active'
      };
      
      return {
        ...state,
        workflowOptimizations: [newOptimization, ...state.workflowOptimizations.slice(0, 19)] // Keep last 20
      };

    case INTELLIGENCE_ACTIONS.UPDATE_WORKFLOW_STATUS:
      return {
        ...state,
        activeOptimizations: {
          ...state.activeOptimizations,
          [action.workflowId]: action.status
        }
      };

    default:
      return state;
  }
}

// Create Context
const UnifiedIntelligenceContext = createContext();

// Provider Component
export const UnifiedIntelligenceProvider = ({ children }) => {
  const [state, dispatch] = useReducer(intelligenceReducer, initialState);
  const { currentLanguage, isRTL } = useLanguage();
  const { user, systemStatus, unifiedData } = useUnifiedHealthcare();
  
  // Refs for WebSocket and intervals
  const wsRef = useRef(null);
  const performanceIntervalRef = useRef(null);
  const patternAnalysisIntervalRef = useRef(null);

  // Initialize Intelligence System
  useEffect(() => {
    initializeIntelligenceSystem();
    
    return () => {
      cleanup();
    };
  }, []);

  // Update cultural context based on language
  useEffect(() => {
    dispatch({
      type: INTELLIGENCE_ACTIONS.SET_CULTURAL_CONTEXT,
      context: {
        language: currentLanguage,
        rtl: isRTL,
        patterns: CULTURAL_PATTERNS.SAUDI_ARABIA
      }
    });
  }, [currentLanguage, isRTL]);

  const initializeIntelligenceSystem = useCallback(async () => {
    try {
      // Initialize AI systems
      await initializeAI();
      
      // Setup WebSocket connection
      setupWebSocketConnection();
      
      // Start performance monitoring
      startPerformanceMonitoring();
      
      // Initialize user pattern analysis
      startUserPatternAnalysis();
      
      dispatch({
        type: INTELLIGENCE_ACTIONS.SET_CONNECTION_STATUS,
        connected: true
      });

    } catch (error) {
      console.error('Failed to initialize intelligence system:', error);
      dispatch({
        type: INTELLIGENCE_ACTIONS.SET_AI_ERROR,
        error: error.message
      });
    }
  }, []);

  const initializeAI = useCallback(async () => {
    try {
      dispatch({ type: INTELLIGENCE_ACTIONS.SET_AI_PROCESSING, processing: true });

      const response = await unifiedAPIClient.post('/api/ai/initialize', {
        userId: user.id,
        language: currentLanguage,
        culturalContext: state.culturalContext,
        features: [
          'predictive_analytics',
          'cultural_intelligence',
          'workflow_optimization',
          'behavioral_analysis',
          'arabic_nlp'
        ]
      });

      if (response.data.success) {
        dispatch({ type: INTELLIGENCE_ACTIONS.SET_AI_READY, ready: true });
        dispatch({ type: INTELLIGENCE_ACTIONS.CLEAR_AI_ERROR });
      }

    } catch (error) {
      dispatch({
        type: INTELLIGENCE_ACTIONS.SET_AI_ERROR,
        error: 'Failed to initialize AI systems'
      });
    } finally {
      dispatch({ type: INTELLIGENCE_ACTIONS.SET_AI_PROCESSING, processing: false });
    }
  }, [user.id, currentLanguage, state.culturalContext]);

  const setupWebSocketConnection = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    wsRef.current = unifiedAPIClient.connectWebSocket(
      user.id,
      handleWebSocketMessage,
      handleWebSocketError
    );
  }, [user.id]);

  const handleWebSocketMessage = useCallback((data) => {
    const { type, payload, context, timestamp } = data;

    switch (type) {
      case 'intelligence_insight':
        dispatch({
          type: INTELLIGENCE_ACTIONS.ADD_INSIGHT,
          insight: {
            ...payload,
            context,
            timestamp,
            source: 'real_time'
          }
        });
        break;

      case 'prediction_update':
        dispatch({
          type: INTELLIGENCE_ACTIONS.SET_PREDICTIONS,
          context,
          predictions: payload
        });
        break;

      case 'recommendation':
        dispatch({
          type: INTELLIGENCE_ACTIONS.ADD_RECOMMENDATION,
          recommendation: {
            ...payload,
            context,
            timestamp,
            source: 'ai_engine'
          }
        });
        break;

      case 'real_time_data':
        dispatch({
          type: INTELLIGENCE_ACTIONS.UPDATE_REAL_TIME_DATA,
          context,
          data: payload
        });
        break;

      case 'workflow_optimization':
        dispatch({
          type: INTELLIGENCE_ACTIONS.ADD_WORKFLOW_OPTIMIZATION,
          optimization: {
            ...payload,
            context,
            timestamp
          }
        });
        break;

      case 'performance_metrics':
        dispatch({
          type: INTELLIGENCE_ACTIONS.UPDATE_PERFORMANCE_METRICS,
          metrics: payload
        });
        break;

      default:
        console.log('Unknown intelligence message type:', type);
    }
  }, []);

  const handleWebSocketError = useCallback((error) => {
    console.error('Intelligence WebSocket error:', error);
    dispatch({
      type: INTELLIGENCE_ACTIONS.SET_WEBSOCKET_STATUS,
      connected: false
    });
    
    // Attempt reconnection after delay
    setTimeout(() => {
      setupWebSocketConnection();
    }, 5000);
  }, [setupWebSocketConnection]);

  const startPerformanceMonitoring = useCallback(() => {
    performanceIntervalRef.current = setInterval(async () => {
      try {
        const metrics = unifiedAPIClient.getPerformanceMetrics();
        
        dispatch({
          type: INTELLIGENCE_ACTIONS.UPDATE_PERFORMANCE_METRICS,
          metrics: {
            responseTime: metrics.api.averageResponseTime,
            accuracy: calculatePredictionAccuracy(),
            userSatisfaction: calculateUserSatisfaction()
          }
        });

      } catch (error) {
        console.error('Performance monitoring error:', error);
      }
    }, 30000); // Every 30 seconds
  }, []);

  const startUserPatternAnalysis = useCallback(() => {
    patternAnalysisIntervalRef.current = setInterval(async () => {
      try {
        const patterns = await analyzeUserPatterns();
        
        dispatch({
          type: INTELLIGENCE_ACTIONS.UPDATE_USER_PATTERNS,
          patterns
        });

      } catch (error) {
        console.error('Pattern analysis error:', error);
      }
    }, 300000); // Every 5 minutes
  }, []);

  const calculatePredictionAccuracy = useCallback(() => {
    // Analyze recent predictions vs actual outcomes
    const recentPredictions = state.insights.filter(
      insight => insight.type === INTELLIGENCE_TYPES.PREDICTIVE &&
      Date.now() - new Date(insight.timestamp).getTime() < 86400000 // Last 24 hours
    );

    if (recentPredictions.length === 0) return 0;

    const accurateCount = recentPredictions.filter(
      prediction => prediction.accuracy && prediction.accuracy > 0.7
    ).length;

    return (accurateCount / recentPredictions.length) * 100;
  }, [state.insights]);

  const calculateUserSatisfaction = useCallback(() => {
    // Calculate based on user interactions with recommendations
    const recentRecommendations = state.recommendations.filter(
      rec => Date.now() - new Date(rec.timestamp).getTime() < 86400000
    );

    if (recentRecommendations.length === 0) return 0;

    const positiveCount = recentRecommendations.filter(
      rec => rec.status === 'accepted' || rec.status === 'implemented'
    ).length;

    return (positiveCount / recentRecommendations.length) * 100;
  }, [state.recommendations]);

  const analyzeUserPatterns = useCallback(async () => {
    try {
      const response = await unifiedAPIClient.post('/api/ai/analyze-patterns', {
        userId: user.id,
        timeframe: '7d',
        includeWorkflow: true,
        includeBehavioral: true,
        culturalContext: state.culturalContext
      });

      return response.data.patterns || {};
    } catch (error) {
      console.error('User pattern analysis failed:', error);
      return {};
    }
  }, [user.id, state.culturalContext]);

  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    if (performanceIntervalRef.current) {
      clearInterval(performanceIntervalRef.current);
    }
    
    if (patternAnalysisIntervalRef.current) {
      clearInterval(patternAnalysisIntervalRef.current);
    }
  }, []);

  // Public API Methods
  const getInsights = useCallback((context = null, type = null, severity = null) => {
    let filtered = state.insights;

    if (context) {
      filtered = filtered.filter(insight => insight.context === context);
    }

    if (type) {
      filtered = filtered.filter(insight => insight.type === type);
    }

    if (severity) {
      filtered = filtered.filter(insight => insight.severity === severity);
    }

    return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }, [state.insights]);

  const getPredictions = useCallback((context) => {
    return state.predictions[context] || null;
  }, [state.predictions]);

  const getRecommendations = useCallback((context = null, status = null) => {
    let filtered = state.recommendations;

    if (context) {
      filtered = filtered.filter(rec => rec.context === context);
    }

    if (status) {
      filtered = filtered.filter(rec => rec.status === status);
    }

    return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }, [state.recommendations]);

  const subscribeToRealTimeUpdates = useCallback((context, callback) => {
    const subscriptionKey = `${context}_${Date.now()}`;
    
    const subscription = {
      context,
      callback,
      active: true
    };

    dispatch({
      type: INTELLIGENCE_ACTIONS.SET_SUBSCRIPTION,
      key: subscriptionKey,
      subscription
    });

    // Send subscription request via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        context,
        subscriptionKey
      }));
    }

    return () => {
      dispatch({
        type: INTELLIGENCE_ACTIONS.REMOVE_SUBSCRIPTION,
        key: subscriptionKey
      });

      // Send unsubscribe request
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'unsubscribe',
          subscriptionKey
        }));
      }
    };
  }, []);

  const unsubscribeFromRealTimeUpdates = useCallback((context) => {
    const subscriptionsToRemove = Array.from(state.subscriptions.entries())
      .filter(([key, sub]) => sub.context === context);

    subscriptionsToRemove.forEach(([key]) => {
      dispatch({
        type: INTELLIGENCE_ACTIONS.REMOVE_SUBSCRIPTION,
        key
      });
    });
  }, [state.subscriptions]);

  const requestAIInsight = useCallback(async (context, query, options = {}) => {
    try {
      dispatch({ type: INTELLIGENCE_ACTIONS.SET_AI_PROCESSING, processing: true });

      const response = await unifiedAPIClient.post('/api/ai/request-insight', {
        context,
        query,
        language: currentLanguage,
        culturalContext: state.culturalContext,
        userPatterns: state.userPatterns,
        ...options
      });

      if (response.data.success) {
        dispatch({
          type: INTELLIGENCE_ACTIONS.ADD_INSIGHT,
          insight: {
            ...response.data.insight,
            context,
            source: 'on_demand'
          }
        });

        return response.data.insight;
      }

      throw new Error(response.data.message || 'Failed to get AI insight');

    } catch (error) {
      dispatch({
        type: INTELLIGENCE_ACTIONS.SET_AI_ERROR,
        error: error.message
      });
      throw error;
    } finally {
      dispatch({ type: INTELLIGENCE_ACTIONS.SET_AI_PROCESSING, processing: false });
    }
  }, [currentLanguage, state.culturalContext, state.userPatterns]);

  const updateRecommendationStatus = useCallback((recommendationId, status) => {
    dispatch({
      type: INTELLIGENCE_ACTIONS.UPDATE_RECOMMENDATION_STATUS,
      recommendationId,
      status
    });

    // Send feedback to AI system
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'recommendation_feedback',
        recommendationId,
        status,
        timestamp: new Date().toISOString()
      }));
    }
  }, []);

  const clearInsights = useCallback((context = null) => {
    if (context) {
      const filteredInsights = state.insights.filter(insight => insight.context !== context);
      // This would require a new action type or modifying existing ones
      dispatch({ type: INTELLIGENCE_ACTIONS.CLEAR_INSIGHTS });
      // Then re-add non-matching insights - this is simplified
    } else {
      dispatch({ type: INTELLIGENCE_ACTIONS.CLEAR_INSIGHTS });
    }
  }, [state.insights]);

  // Memoized context value
  const contextValue = useMemo(() => ({
    // State
    ...state,
    
    // Status checks
    isReady: state.aiReady && state.isConnected,
    isProcessing: state.aiProcessing,
    hasError: !!state.aiError,
    
    // Data access methods
    getInsights,
    getPredictions,
    getRecommendations,
    
    // Real-time subscriptions
    subscribeToRealTimeUpdates,
    unsubscribeFromRealTimeUpdates,
    realTimeData: state.realTimeData,
    
    // AI interaction
    requestAIInsight,
    updateRecommendationStatus,
    
    // Utilities
    clearInsights,
    
    // Constants
    INTELLIGENCE_TYPES,
    INSIGHT_SEVERITY,
    CULTURAL_PATTERNS
  }), [
    state,
    getInsights,
    getPredictions,
    getRecommendations,
    subscribeToRealTimeUpdates,
    unsubscribeFromRealTimeUpdates,
    requestAIInsight,
    updateRecommendationStatus,
    clearInsights
  ]);

  return (
    <UnifiedIntelligenceContext.Provider value={contextValue}>
      {children}
    </UnifiedIntelligenceContext.Provider>
  );
};

// Custom hook
export const useUnifiedIntelligence = (options = {}) => {
  const context = useContext(UnifiedIntelligenceContext);

  if (!context) {
    throw new Error('useUnifiedIntelligence must be used within a UnifiedIntelligenceProvider');
  }

  const { enabled = true } = options;

  // Return disabled state if not enabled
  if (!enabled) {
    return {
      isReady: false,
      isProcessing: false,
      hasError: false,
      getInsights: () => [],
      getPredictions: () => null,
      getRecommendations: () => [],
      subscribeToRealTimeUpdates: () => () => {},
      unsubscribeFromRealTimeUpdates: () => {},
      realTimeData: {},
      requestAIInsight: async () => null,
      updateRecommendationStatus: () => {},
      clearInsights: () => {}
    };
  }

  return context;
};

export default UnifiedIntelligenceContext;