/**
 * UnifiedComponentArchitecture.jsx
 * 
 * BRAINSAIT FRONTEND UNIFICATION STRATEGY
 * Template implementing OidTree's 5-component pattern across the entire platform
 * 
 * ARCHITECTURAL PRINCIPLES:
 * 1. Container Components: Orchestrate state management and data flow
 * 2. Control Components: Handle user interactions and form controls
 * 3. Renderer Components: Focus on display logic and presentation
 * 4. Detail Components: Manage information panels and detailed views
 * 5. Utility Components: Provide reusable logic and helper functions
 * 
 * INTEGRATION FEATURES:
 * - PyBrain AI capabilities integration
 * - Arabic-first RTL support
 * - Real-time intelligence context
 * - Performance optimization
 * - Healthcare compliance
 * - NPHIES FHIR R4 integration
 */

import React, { 
  Suspense, 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  memo,
  useRef 
} from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  CircularProgress, 
  Alert,
  Typography,
  Skeleton,
  useTheme,
  useMediaQuery 
} from '@mui/material';
import { useLanguage } from '../../hooks/useLanguage';
import { useUnifiedHealthcare } from '../../contexts/UnifiedHealthcareContext';
import { useUnifiedPyBrain } from '../../hooks/useUnifiedPyBrain';
import { useUnifiedIntelligence } from '../../contexts/UnifiedIntelligenceContext';
import ErrorBoundary from '../shared/ErrorBoundary';

/**
 * COMPONENT ARCHITECTURE TEMPLATE
 * 
 * This template demonstrates the 5-component pattern used in OidTree
 * and provides a blueprint for all BrainSAIT platform components
 */

// ============================================================================
// 1. CONTAINER COMPONENT - Orchestration and State Management
// ============================================================================

/**
 * Base Container Component Template
 * Handles:
 * - State management and data fetching
 * - Real-time intelligence integration
 * - Healthcare context management
 * - Performance optimization
 * - Error handling and recovery
 */
const UnifiedContainer = memo(({ 
  context, 
  children, 
  enableAI = true,
  enableRealTime = true,
  performanceMonitoring = true,
  ...props 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { 
    switchContext, 
    getUnifiedData, 
    isLoading,
    hasError,
    getError,
    systemStatus 
  } = useUnifiedHealthcare();
  
  const {
    getAIInsights,
    isAIReady,
    aiState
  } = useUnifiedPyBrain({ enabled: enableAI });

  const {
    subscribeToRealTimeUpdates,
    unsubscribeFromRealTimeUpdates,
    realTimeData
  } = useUnifiedIntelligence({ enabled: enableRealTime });

  const [containerState, setContainerState] = useState({
    initialized: false,
    dataVersion: 0,
    lastUpdate: null,
    aiInsights: null
  });

  const performanceRef = useRef({
    startTime: Date.now(),
    renderCount: 0,
    interactions: 0
  });

  // Initialize container with context-specific data
  useEffect(() => {
    const initializeContainer = async () => {
      try {
        // Switch to the specified context
        if (context) {
          switchContext(context);
        }

        // Initialize AI insights if enabled
        if (enableAI && isAIReady) {
          const insights = await getAIInsights(context, {
            language: currentLanguage,
            userContext: 'healthcare_professional',
            culturalContext: 'saudi_arabia'
          });
          
          setContainerState(prev => ({
            ...prev,
            aiInsights: insights,
            initialized: true,
            lastUpdate: new Date().toISOString()
          }));
        } else {
          setContainerState(prev => ({
            ...prev,
            initialized: true,
            lastUpdate: new Date().toISOString()
          }));
        }

        // Subscribe to real-time updates
        if (enableRealTime && context) {
          subscribeToRealTimeUpdates(context, (data) => {
            setContainerState(prev => ({
              ...prev,
              dataVersion: prev.dataVersion + 1,
              lastUpdate: new Date().toISOString()
            }));
          });
        }

      } catch (error) {
        console.error('Container initialization failed:', error);
      }
    };

    initializeContainer();

    return () => {
      if (enableRealTime && context) {
        unsubscribeFromRealTimeUpdates(context);
      }
    };
  }, [context, enableAI, enableRealTime, currentLanguage, isAIReady]);

  // Performance monitoring
  useEffect(() => {
    if (performanceMonitoring) {
      performanceRef.current.renderCount += 1;
      
      // Log performance metrics every 10 renders
      if (performanceRef.current.renderCount % 10 === 0) {
        const renderTime = Date.now() - performanceRef.current.startTime;
        console.debug('UnifiedContainer Performance:', {
          context,
          renderCount: performanceRef.current.renderCount,
          totalTime: renderTime,
          avgRenderTime: renderTime / performanceRef.current.renderCount,
          aiEnabled: enableAI,
          realTimeEnabled: enableRealTime
        });
      }
    }
  });

  // Enhanced error boundary fallback
  const ErrorFallback = useCallback(({ error, resetError }) => (
    <Alert 
      severity="error" 
      sx={{ 
        m: 2,
        textAlign: isRTL ? 'right' : 'left',
        direction: isRTL ? 'rtl' : 'ltr'
      }}
    >
      <Typography variant="h6" gutterBottom>
        {currentLanguage === 'ar' 
          ? 'خطأ في تحميل المكون' 
          : 'Component Loading Error'}
      </Typography>
      <Typography variant="body2" sx={{ mb: 2 }}>
        {currentLanguage === 'ar'
          ? 'حدث خطأ في تحميل هذا المكون. يرجى المحاولة مرة أخرى.'
          : 'An error occurred while loading this component. Please try again.'}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Context: {context} | Error: {error?.message}
      </Typography>
    </Alert>
  ), [currentLanguage, isRTL, context]);

  return (
    <ErrorBoundary fallback={ErrorFallback}>
      <Box 
        className={`unified-container ${isRTL ? 'rtl' : 'ltr'}`}
        dir={isRTL ? 'rtl' : 'ltr'}
        sx={{
          position: 'relative',
          width: '100%',
          ...props.sx
        }}
        {...props}
      >
        {/* AI Insights Overlay */}
        {enableAI && containerState.aiInsights && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              right: isRTL ? 'auto' : 8,
              left: isRTL ? 8 : 'auto',
              zIndex: 1000,
              backgroundColor: 'background.paper',
              borderRadius: 1,
              p: 1,
              boxShadow: 1,
              maxWidth: 300
            }}
          >
            <Typography variant="caption" color="primary">
              PyBrain AI: {containerState.aiInsights.summary}
            </Typography>
          </Box>
        )}

        {/* Real-time Status Indicator */}
        {enableRealTime && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: isRTL ? 'auto' : 8,
              right: isRTL ? 8 : 'auto',
              zIndex: 999
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: realTimeData?.connected ? 'success.main' : 'error.main',
                animation: realTimeData?.connected ? 'pulse 2s infinite' : 'none'
              }}
            />
          </Box>
        )}

        {/* Main Content */}
        {children}
      </Box>
    </ErrorBoundary>
  );
});

UnifiedContainer.displayName = 'UnifiedContainer';

// ============================================================================
// 2. CONTROL COMPONENT - User Interactions and Form Controls
// ============================================================================

/**
 * Base Control Component Template
 * Handles:
 * - User input and form validation
 * - Arabic-aware input handling
 * - AI-assisted form completion
 * - Real-time validation
 * - Accessibility compliance
 */
const UnifiedControls = memo(({ 
  onAction,
  actions = [],
  enableAIAssist = true,
  enableRealTimeValidation = true,
  ...props 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const {
    getFormAssistance,
    validateInput,
    isAIReady
  } = useUnifiedPyBrain({ enabled: enableAIAssist });

  const [controlState, setControlState] = useState({
    activeAction: null,
    validationResults: {},
    aiSuggestions: {},
    interactionCount: 0
  });

  // Handle action with AI assistance
  const handleAction = useCallback(async (actionType, data) => {
    setControlState(prev => ({
      ...prev,
      activeAction: actionType,
      interactionCount: prev.interactionCount + 1
    }));

    try {
      // Get AI assistance if enabled
      if (enableAIAssist && isAIReady) {
        const assistance = await getFormAssistance(actionType, data, {
          language: currentLanguage,
          culturalContext: 'saudi_healthcare'
        });
        
        setControlState(prev => ({
          ...prev,
          aiSuggestions: {
            ...prev.aiSuggestions,
            [actionType]: assistance
          }
        }));
      }

      // Execute the action
      if (onAction) {
        await onAction(actionType, data);
      }

    } catch (error) {
      console.error('Action execution failed:', error);
    } finally {
      setControlState(prev => ({
        ...prev,
        activeAction: null
      }));
    }
  }, [onAction, enableAIAssist, isAIReady, currentLanguage, getFormAssistance]);

  // Real-time input validation
  const handleInputValidation = useCallback(async (field, value) => {
    if (!enableRealTimeValidation) return;

    try {
      const validation = await validateInput(field, value, {
        language: currentLanguage,
        healthcareContext: true
      });

      setControlState(prev => ({
        ...prev,
        validationResults: {
          ...prev.validationResults,
          [field]: validation
        }
      }));
    } catch (error) {
      console.error('Validation failed:', error);
    }
  }, [enableRealTimeValidation, validateInput, currentLanguage]);

  return (
    <Paper
      elevation={1}
      sx={{
        p: 2,
        direction: isRTL ? 'rtl' : 'ltr',
        backgroundColor: 'background.paper',
        ...props.sx
      }}
    >
      <Grid container spacing={2} direction={isRTL ? 'row-reverse' : 'row'}>
        {actions.map((action, index) => (
          <Grid item xs={12} sm={isMobile ? 12 : 'auto'} key={action.id || index}>
            <Box
              component="button"
              onClick={() => handleAction(action.type, action.data)}
              disabled={controlState.activeAction === action.type}
              sx={{
                width: '100%',
                p: 1.5,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                backgroundColor: 'background.default',
                cursor: 'pointer',
                transition: 'all 0.2s',
                textAlign: isRTL ? 'right' : 'left',
                '&:hover': {
                  backgroundColor: 'action.hover',
                  borderColor: 'primary.main'
                },
                '&:disabled': {
                  opacity: 0.6,
                  cursor: 'not-allowed'
                }
              }}
            >
              <Typography variant="body2">
                {currentLanguage === 'ar' ? action.labelAr : action.label}
              </Typography>
              
              {/* AI Suggestion Indicator */}
              {controlState.aiSuggestions[action.type] && (
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 0.5 }}>
                  AI: {controlState.aiSuggestions[action.type].summary}
                </Typography>
              )}
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Interaction Metrics for Development */}
      {process.env.NODE_ENV === 'development' && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Interactions: {controlState.interactionCount} | AI Ready: {isAIReady ? 'Yes' : 'No'}
        </Typography>
      )}
    </Paper>
  );
});

UnifiedControls.displayName = 'UnifiedControls';

// ============================================================================
// 3. RENDERER COMPONENT - Display Logic and Presentation
// ============================================================================

/**
 * Base Renderer Component Template
 * Handles:
 * - Data visualization and presentation
 * - Arabic typography and RTL layouts
 * - Responsive design patterns
 * - Performance-optimized rendering
 * - Accessibility compliance
 */
const UnifiedRenderer = memo(({ 
  data,
  renderMode = 'list',
  enableVirtualization = false,
  itemHeight = 60,
  ...props 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Memoized render functions for performance
  const renderItem = useCallback((item, index) => (
    <Box
      key={item.id || index}
      sx={{
        p: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        minHeight: itemHeight,
        direction: isRTL ? 'rtl' : 'ltr',
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        '&:hover': {
          backgroundColor: 'action.hover'
        }
      }}
    >
      {/* Item Icon */}
      {item.icon && (
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 1,
            backgroundColor: 'primary.main',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'primary.contrastText'
          }}
        >
          {item.icon}
        </Box>
      )}

      {/* Item Content */}
      <Box sx={{ flex: 1, textAlign: isRTL ? 'right' : 'left' }}>
        <Typography variant="subtitle1" fontWeight="medium">
          {currentLanguage === 'ar' ? item.titleAr || item.title : item.title}
        </Typography>
        
        {item.description && (
          <Typography variant="body2" color="text.secondary">
            {currentLanguage === 'ar' ? item.descriptionAr || item.description : item.description}
          </Typography>
        )}

        {/* Arabic-specific styling */}
        {currentLanguage === 'ar' && (
          <style jsx>{`
            .arabic-text {
              font-family: 'Noto Sans Arabic', 'Cairo', sans-serif;
              line-height: 1.8;
              letter-spacing: 0.02em;
            }
          `}</style>
        )}
      </Box>

      {/* Item Actions */}
      {item.actions && (
        <Box sx={{ display: 'flex', gap: 1 }}>
          {item.actions.map((action, actionIndex) => (
            <Box
              key={actionIndex}
              component="button"
              onClick={() => action.onClick?.(item)}
              sx={{
                p: 1,
                border: 'none',
                borderRadius: 1,
                backgroundColor: 'action.selected',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
            >
              {action.icon}
            </Box>
          ))}
        </Box>
      )}
    </Box>
  ), [currentLanguage, isRTL, itemHeight]);

  // Loading skeleton
  const renderSkeleton = useMemo(() => (
    <Box sx={{ p: 2 }}>
      {Array.from({ length: 5 }).map((_, index) => (
        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Skeleton variant="rectangular" width={40} height={40} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" />
          </Box>
        </Box>
      ))}
    </Box>
  ), []);

  if (!data) {
    return renderSkeleton;
  }

  return (
    <Paper
      elevation={1}
      sx={{
        overflow: 'hidden',
        direction: isRTL ? 'rtl' : 'ltr',
        ...props.sx
      }}
    >
      {/* Header */}
      {props.title && (
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight="bold">
            {currentLanguage === 'ar' ? props.titleAr || props.title : props.title}
          </Typography>
        </Box>
      )}

      {/* Content Renderer */}
      <Box sx={{ maxHeight: props.maxHeight || 400, overflow: 'auto' }}>
        {Array.isArray(data) ? (
          data.map(renderItem)
        ) : (
          renderItem(data, 0)
        )}
      </Box>

      {/* Empty State */}
      {Array.isArray(data) && data.length === 0 && (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            {currentLanguage === 'ar' 
              ? 'لا توجد بيانات للعرض'
              : 'No data to display'}
          </Typography>
        </Box>
      )}
    </Paper>
  );
});

UnifiedRenderer.displayName = 'UnifiedRenderer';

// ============================================================================
// 4. DETAIL COMPONENT - Information Panels and Detailed Views
// ============================================================================

/**
 * Base Detail Component Template
 * Handles:
 * - Detailed information display
 * - Expandable sections
 * - Related data visualization
 * - Action panels
 * - FHIR data integration
 */
const UnifiedDetails = memo(({ 
  selectedItem,
  sections = [],
  enableRelatedData = true,
  enableActions = true,
  ...props 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const [expandedSections, setExpandedSections] = useState(new Set());
  const [relatedData, setRelatedData] = useState({});

  const toggleSection = useCallback((sectionId) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  // Load related data when item changes
  useEffect(() => {
    if (selectedItem && enableRelatedData) {
      // Simulated related data loading
      setRelatedData({
        related_items: [],
        metadata: {},
        audit_trail: []
      });
    }
  }, [selectedItem, enableRelatedData]);

  if (!selectedItem) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', ...props.sx }}>
        <Typography variant="body1" color="text.secondary">
          {currentLanguage === 'ar' 
            ? 'اختر عنصراً لعرض التفاصيل'
            : 'Select an item to view details'}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ overflow: 'hidden', ...props.sx }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" fontWeight="bold" sx={{ textAlign: isRTL ? 'right' : 'left' }}>
          {currentLanguage === 'ar' 
            ? selectedItem.titleAr || selectedItem.title || 'تفاصيل العنصر'
            : selectedItem.title || 'Item Details'}
        </Typography>
      </Box>

      {/* Content Sections */}
      <Box sx={{ maxHeight: 500, overflow: 'auto' }}>
        {sections.map((section) => (
          <Box key={section.id} sx={{ borderBottom: '1px solid', borderColor: 'divider' }}>
            {/* Section Header */}
            <Box
              onClick={() => toggleSection(section.id)}
              sx={{
                p: 2,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
            >
              <Typography variant="subtitle1" fontWeight="medium">
                {currentLanguage === 'ar' ? section.titleAr || section.title : section.title}
              </Typography>
              <Box
                sx={{
                  transform: expandedSections.has(section.id) ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s'
                }}
              >
                ▼
              </Box>
            </Box>

            {/* Section Content */}
            {expandedSections.has(section.id) && (
              <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
                {section.render ? (
                  section.render(selectedItem, relatedData)
                ) : (
                  <Typography variant="body2">
                    {section.content || 'No content available'}
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        ))}
      </Box>

      {/* Actions Footer */}
      {enableActions && selectedItem.actions && (
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Grid container spacing={1}>
            {selectedItem.actions.map((action, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Box
                  component="button"
                  onClick={() => action.onClick?.(selectedItem)}
                  sx={{
                    width: '100%',
                    p: 1,
                    border: '1px solid',
                    borderColor: 'primary.main',
                    borderRadius: 1,
                    backgroundColor: 'transparent',
                    color: 'primary.main',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText'
                    }
                  }}
                >
                  <Typography variant="body2">
                    {currentLanguage === 'ar' ? action.labelAr || action.label : action.label}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Paper>
  );
});

UnifiedDetails.displayName = 'UnifiedDetails';

// ============================================================================
// 5. UTILITY COMPONENT - Reusable Logic and Helper Functions
// ============================================================================

/**
 * Base Utility Component Template
 * Provides:
 * - Common utility functions
 * - Shared component logic
 * - Performance optimization helpers
 * - Arabic text processing
 * - Healthcare data formatting
 */
const UnifiedUtilities = {
  // Arabic text processing
  formatArabicText: (text, options = {}) => {
    if (!text) return '';
    
    const {
      addDiacritics = false,
      normalizeSpacing = true,
      preserveLineBreaks = true
    } = options;

    let processedText = text;

    if (normalizeSpacing) {
      processedText = processedText.replace(/\s+/g, ' ').trim();
    }

    if (!preserveLineBreaks) {
      processedText = processedText.replace(/\n/g, ' ');
    }

    return processedText;
  },

  // Healthcare data formatting
  formatHealthcareData: (data, type, language = 'en') => {
    if (!data) return '';

    switch (type) {
      case 'date':
        return new Intl.DateTimeFormat(language === 'ar' ? 'ar-SA' : 'en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        }).format(new Date(data));

      case 'currency':
        return new Intl.NumberFormat(language === 'ar' ? 'ar-SA' : 'en-US', {
          style: 'currency',
          currency: 'SAR'
        }).format(data);

      case 'percentage':
        return new Intl.NumberFormat(language === 'ar' ? 'ar-SA' : 'en-US', {
          style: 'percent',
          minimumFractionDigits: 1,
          maximumFractionDigits: 2
        }).format(data / 100);

      default:
        return String(data);
    }
  },

  // Performance optimization helpers
  createMemoizedSelector: (selector, dependencies = []) => {
    const memoized = useMemo(selector, dependencies);
    return memoized;
  },

  // Component lazy loading helper
  createLazyComponent: (importFunction, fallback = null) => {
    return React.lazy(importFunction);
  },

  // Responsive breakpoint helper
  useResponsiveValue: (values) => {
    const theme = useTheme();
    const isXs = useMediaQuery(theme.breakpoints.only('xs'));
    const isSm = useMediaQuery(theme.breakpoints.only('sm'));
    const isMd = useMediaQuery(theme.breakpoints.only('md'));
    const isLg = useMediaQuery(theme.breakpoints.only('lg'));

    if (isXs && values.xs !== undefined) return values.xs;
    if (isSm && values.sm !== undefined) return values.sm;
    if (isMd && values.md !== undefined) return values.md;
    if (isLg && values.lg !== undefined) return values.lg;
    
    return values.xl || values.default || values[Object.keys(values)[0]];
  }
};

// ============================================================================
// MAIN UNIFIED COMPONENT ARCHITECTURE EXPORT
// ============================================================================

/**
 * Complete Implementation Example
 * Demonstrates how to use all 5 components together
 */
const UnifiedComponentExample = memo(({ context = 'healthcare' }) => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [data, setData] = useState([]);

  // Example actions for controls
  const actions = [
    {
      id: 'refresh',
      type: 'refresh',
      label: 'Refresh Data',
      labelAr: 'تحديث البيانات',
      data: { context }
    },
    {
      id: 'export',
      type: 'export',
      label: 'Export',
      labelAr: 'تصدير',
      data: { format: 'pdf' }
    }
  ];

  // Example sections for details
  const detailSections = [
    {
      id: 'basic',
      title: 'Basic Information',
      titleAr: 'المعلومات الأساسية',
      render: (item) => (
        <Box>
          <Typography variant="body2">ID: {item.id}</Typography>
          <Typography variant="body2">Status: {item.status}</Typography>
        </Box>
      )
    },
    {
      id: 'metadata',
      title: 'Metadata',
      titleAr: 'البيانات الوصفية',
      render: (item, related) => (
        <Box>
          <Typography variant="body2">Created: {item.created}</Typography>
          <Typography variant="body2">Modified: {item.modified}</Typography>
        </Box>
      )
    }
  ];

  const handleAction = useCallback(async (actionType, actionData) => {
    console.log('Action executed:', actionType, actionData);
    
    // Simulate data refresh
    if (actionType === 'refresh') {
      setData([
        { 
          id: 1, 
          title: 'Sample Item 1', 
          titleAr: 'عنصر تجريبي 1',
          status: 'active',
          created: new Date().toISOString(),
          modified: new Date().toISOString()
        },
        { 
          id: 2, 
          title: 'Sample Item 2', 
          titleAr: 'عنصر تجريبي 2',
          status: 'pending',
          created: new Date().toISOString(),
          modified: new Date().toISOString()
        }
      ]);
    }
  }, []);

  return (
    <UnifiedContainer context={context}>
      <Grid container spacing={3}>
        {/* Controls Section */}
        <Grid item xs={12}>
          <UnifiedControls
            actions={actions}
            onAction={handleAction}
            enableAIAssist={true}
          />
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <UnifiedRenderer
            data={data}
            title="Healthcare Items"
            titleAr="العناصر الصحية"
            onItemSelect={setSelectedItem}
          />
        </Grid>

        {/* Details Panel */}
        <Grid item xs={12} md={4}>
          <UnifiedDetails
            selectedItem={selectedItem}
            sections={detailSections}
            enableRelatedData={true}
            enableActions={true}
          />
        </Grid>
      </Grid>
    </UnifiedContainer>
  );
});

UnifiedComponentExample.displayName = 'UnifiedComponentExample';

export {
  UnifiedContainer,
  UnifiedControls,
  UnifiedRenderer,
  UnifiedDetails,
  UnifiedUtilities,
  UnifiedComponentExample
};

export default {
  Container: UnifiedContainer,
  Controls: UnifiedControls,
  Renderer: UnifiedRenderer,
  Details: UnifiedDetails,
  Utilities: UnifiedUtilities,
  Example: UnifiedComponentExample
};