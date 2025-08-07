/**
 * WorkflowProgressVisualization Component
 * Real-time workflow progress visualization with Arabic RTL support
 * Integrated with PyHeart workflow automation and PyBrain AI insights
 */

import { memo, useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Typography,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Alert
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
  Hourglass as WaitingIcon,
  Psychology as AIIcon,
  Speed as PerformanceIcon,
  Timeline as TimelineIcon,
  AutoFixHigh as AutomationIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';
import { useUnifiedPyHeart } from '../../hooks/useUnifiedPyHeart';

// Workflow step status colors
const getStatusColor = (status) => {
  switch (status) {
    case 'completed': return 'success';
    case 'in_progress': return 'warning';
    case 'failed': return 'error';
    case 'pending': return 'default';
    case 'ai_processing': return 'info';
    default: return 'default';
  }
};

// Workflow step status icons
const getStatusIcon = (status) => {
  switch (status) {
    case 'completed': return <CompletedIcon />;
    case 'in_progress': return <PlayIcon />;
    case 'failed': return <ErrorIcon />;
    case 'pending': return <WaitingIcon />;
    case 'ai_processing': return <AIIcon />;
    default: return <WaitingIcon />;
  }
};

// Progress animation component
const AnimatedProgress = memo(({ value, color = "primary", showPercentage = true }) => {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(value);
    }, 100);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
      <Box sx={{ width: '100%', mr: showPercentage ? 1 : 0 }}>
        <LinearProgress 
          variant="determinate" 
          value={animatedValue} 
          color={color}
          sx={{
            height: 8,
            borderRadius: 4,
            '& .MuiLinearProgress-bar': {
              borderRadius: 4,
              transition: 'transform 0.5s ease-in-out'
            }
          }}
        />
      </Box>
      {showPercentage && (
        <Box sx={{ minWidth: 35 }}>
          <Typography variant="body2" color="text.secondary">
            {Math.round(animatedValue)}%
          </Typography>
        </Box>
      )}
    </Box>
  );
});

AnimatedProgress.displayName = 'AnimatedProgress';

// Workflow step component
const WorkflowStep = memo(({ step, index, currentLanguage, isRTL, onStepAction }) => {
  const [expanded, setExpanded] = useState(false);

  const handleToggleExpand = useCallback(() => {
    setExpanded(prev => !prev);
  }, []);

  const getStepTitle = (step) => {
    return currentLanguage === 'ar' ? step.title_ar || step.title : step.title;
  };

  const getStepDescription = (step) => {
    return currentLanguage === 'ar' ? step.description_ar || step.description : step.description;
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        border: '1px solid',
        borderColor: step.status === 'in_progress' ? 'warning.main' : 'divider',
        borderLeft: isRTL ? 'none' : '4px solid',
        borderRight: isRTL ? '4px solid' : 'none',
        borderLeftColor: isRTL ? 'transparent' : `${getStatusColor(step.status)}.main`,
        borderRightColor: isRTL ? `${getStatusColor(step.status)}.main` : 'transparent'
      }}
    >
      <CardContent sx={{ pb: expanded ? 1 : 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2} flex={1}>
            <Avatar 
              sx={{ 
                bgcolor: `${getStatusColor(step.status)}.main`,
                width: 32,
                height: 32
              }}
            >
              {getStatusIcon(step.status)}
            </Avatar>
            
            <Box flex={1}>
              <Typography variant="subtitle2" fontWeight="bold">
                {getStepTitle(step)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {getStepDescription(step)}
              </Typography>
              
              {step.progress !== undefined && (
                <Box mt={1}>
                  <AnimatedProgress 
                    value={step.progress} 
                    color={getStatusColor(step.status)}
                  />
                </Box>
              )}
            </Box>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={step.status}
              size="small"
              color={getStatusColor(step.status)}
              variant="outlined"
            />
            
            {step.aiAssisted && (
              <Tooltip title={currentLanguage === 'ar' ? 'بمساعدة الذكاء الاصطناعي' : 'AI Assisted'}>
                <Chip 
                  icon={<AIIcon />}
                  label={currentLanguage === 'ar' ? 'ذكي' : 'AI'}
                  size="small"
                  color="info"
                  variant="outlined"
                />
              </Tooltip>
            )}
            
            {step.automated && (
              <Tooltip title={currentLanguage === 'ar' ? 'أتمتة' : 'Automated'}>
                <Chip 
                  icon={<AutomationIcon />}
                  label={currentLanguage === 'ar' ? 'آلي' : 'Auto'}
                  size="small"
                  color="secondary"
                  variant="outlined"
                />
              </Tooltip>
            )}

            <IconButton size="small" onClick={handleToggleExpand}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Collapse in={expanded}>
          <Box mt={2}>
            <Divider sx={{ mb: 2 }} />
            
            {/* Step Details */}
            <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2} mb={2}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  {currentLanguage === 'ar' ? 'وقت البدء:' : 'Start Time:'}
                </Typography>
                <Typography variant="body2">
                  {step.startTime ? new Date(step.startTime).toLocaleString() : '-'}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="caption" color="text.secondary">
                  {currentLanguage === 'ar' ? 'المدة المقدرة:' : 'Estimated Duration:'}
                </Typography>
                <Typography variant="body2">
                  {step.estimatedDuration ? `${step.estimatedDuration}s` : '-'}
                </Typography>
              </Box>
              
              {step.assignedTo && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    {currentLanguage === 'ar' ? 'مخصص لـ:' : 'Assigned To:'}
                  </Typography>
                  <Typography variant="body2">
                    {step.assignedTo}
                  </Typography>
                </Box>
              )}
              
              {step.lastUpdate && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    {currentLanguage === 'ar' ? 'آخر تحديث:' : 'Last Update:'}
                  </Typography>
                  <Typography variant="body2">
                    {new Date(step.lastUpdate).toLocaleString()}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Step Actions */}
            {step.status === 'in_progress' && step.actions && step.actions.length > 0 && (
              <Box display="flex" gap={1} flexWrap="wrap">
                {step.actions.map((action, idx) => (
                  <Button
                    key={idx}
                    size="small"
                    variant="outlined"
                    onClick={() => onStepAction && onStepAction(step.id, action)}
                  >
                    {currentLanguage === 'ar' ? action.label_ar || action.label : action.label}
                  </Button>
                ))}
              </Box>
            )}

            {/* Error Details */}
            {step.status === 'failed' && step.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  {currentLanguage === 'ar' ? step.error.message_ar || step.error.message : step.error.message}
                </Typography>
              </Alert>
            )}

            {/* AI Insights */}
            {step.aiInsights && step.aiInsights.length > 0 && (
              <Box mt={2}>
                <Typography variant="caption" fontWeight="bold" color="primary.main">
                  {currentLanguage === 'ar' ? 'رؤى الذكاء الاصطناعي:' : 'AI Insights:'}
                </Typography>
                {step.aiInsights.map((insight, idx) => (
                  <Typography key={idx} variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    • {currentLanguage === 'ar' ? insight.message_ar || insight.message : insight.message}
                  </Typography>
                ))}
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
});

WorkflowStep.displayName = 'WorkflowStep';

// Main workflow progress visualization component
const WorkflowProgressVisualization = memo(({ 
  workflow,
  compact = false,
  showControls = true,
  onWorkflowAction,
  onClose
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const {
    isPyHeartReady,
    pauseWorkflow,
    resumeWorkflow,
    cancelWorkflow,
    getWorkflowStatus,
    WORKFLOW_STATUS
  } = useUnifiedPyHeart();

  const [localWorkflow, setLocalWorkflow] = useState(workflow);
  const [showDetails, setShowDetails] = useState(!compact);
  const [actionDialog, setActionDialog] = useState({ open: false, action: null });

  // Real-time workflow updates
  useEffect(() => {
    if (!isPyHeartReady || !workflow?.id) return;

    const updateInterval = setInterval(async () => {
      try {
        const updatedWorkflow = getWorkflowStatus(workflow.id);
        if (updatedWorkflow) {
          setLocalWorkflow(updatedWorkflow);
        }
      } catch (error) {
        console.error('Failed to update workflow status:', error);
      }
    }, 2000); // Update every 2 seconds

    return () => clearInterval(updateInterval);
  }, [isPyHeartReady, workflow?.id, getWorkflowStatus]);

  const handleWorkflowAction = useCallback(async (action) => {
    if (!localWorkflow?.id) return;

    try {
      switch (action) {
        case 'pause':
          await pauseWorkflow(localWorkflow.id);
          break;
        case 'resume':
          await resumeWorkflow(localWorkflow.id);
          break;
        case 'cancel':
          await cancelWorkflow(localWorkflow.id);
          break;
        default:
          break;
      }
      
      if (onWorkflowAction) {
        onWorkflowAction(action, localWorkflow);
      }
    } catch (error) {
      console.error(`Failed to ${action} workflow:`, error);
    }
    
    setActionDialog({ open: false, action: null });
  }, [localWorkflow, pauseWorkflow, resumeWorkflow, cancelWorkflow, onWorkflowAction]);

  const handleStepAction = useCallback((stepId, action) => {
    // Handle individual step actions
    if (onWorkflowAction) {
      onWorkflowAction('step_action', { stepId, action, workflow: localWorkflow });
    }
  }, [localWorkflow, onWorkflowAction]);

  if (!localWorkflow) {
    return null;
  }

  const overallProgress = localWorkflow.progress || 0;
  const isActive = localWorkflow.status === WORKFLOW_STATUS.IN_PROGRESS;
  const isCompleted = localWorkflow.status === WORKFLOW_STATUS.COMPLETED;
  const isFailed = localWorkflow.status === WORKFLOW_STATUS.FAILED;

  return (
    <Card 
      sx={{ 
        width: '100%',
        maxWidth: compact ? 400 : 800,
        direction: isRTL ? 'rtl' : 'ltr'
      }}
    >
      <CardContent>
        {/* Workflow Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2} flex={1}>
            <Avatar 
              sx={{ 
                bgcolor: isCompleted ? 'success.main' : isFailed ? 'error.main' : 'warning.main',
                width: 40,
                height: 40
              }}
            >
              {isCompleted ? <CompletedIcon /> : isFailed ? <ErrorIcon /> : <TimelineIcon />}
            </Avatar>
            
            <Box flex={1}>
              <Typography variant="h6" fontWeight="bold">
                {currentLanguage === 'ar' ? localWorkflow.title_ar || localWorkflow.type : localWorkflow.title || localWorkflow.type}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {currentLanguage === 'ar' ? 'معرف سير العمل:' : 'Workflow ID:'} {localWorkflow.id}
              </Typography>
            </Box>
          </Box>

          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={localWorkflow.status}
              color={getStatusColor(localWorkflow.status)}
              size="small"
            />
            
            {showControls && isActive && (
              <>
                <Tooltip title={currentLanguage === 'ar' ? 'إيقاف مؤقت' : 'Pause'}>
                  <IconButton 
                    size="small" 
                    onClick={() => setActionDialog({ open: true, action: 'pause' })}
                  >
                    <PauseIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title={currentLanguage === 'ar' ? 'إلغاء' : 'Cancel'}>
                  <IconButton 
                    size="small" 
                    onClick={() => setActionDialog({ open: true, action: 'cancel' })}
                    color="error"
                  >
                    <StopIcon />
                  </IconButton>
                </Tooltip>
              </>
            )}

            {onClose && (
              <IconButton size="small" onClick={onClose}>
                <CloseIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        {/* Overall Progress */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" fontWeight="bold">
              {currentLanguage === 'ar' ? 'التقدم الإجمالي' : 'Overall Progress'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {Math.round(overallProgress)}%
            </Typography>
          </Box>
          <AnimatedProgress 
            value={overallProgress} 
            color={getStatusColor(localWorkflow.status)}
            showPercentage={false}
          />
        </Box>

        {/* Workflow Statistics */}
        <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(120px, 1fr))" gap={2} mb={3}>
          <Box textAlign="center">
            <Typography variant="h6" color="primary.main">
              {localWorkflow.steps?.length || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentLanguage === 'ar' ? 'إجمالي الخطوات' : 'Total Steps'}
            </Typography>
          </Box>
          
          <Box textAlign="center">
            <Typography variant="h6" color="success.main">
              {localWorkflow.steps?.filter(s => s.status === 'completed').length || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentLanguage === 'ar' ? 'مكتملة' : 'Completed'}
            </Typography>
          </Box>
          
          <Box textAlign="center">
            <Typography variant="h6" color="warning.main">
              {localWorkflow.steps?.filter(s => s.status === 'in_progress').length || 0}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentLanguage === 'ar' ? 'قيد التنفيذ' : 'In Progress'}
            </Typography>
          </Box>
          
          {localWorkflow.estimatedDuration && (
            <Box textAlign="center">
              <Typography variant="h6" color="info.main">
                {Math.round(localWorkflow.estimatedDuration / 60)}m
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {currentLanguage === 'ar' ? 'المدة المقدرة' : 'Est. Duration'}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Toggle Details Button */}
        {!compact && (
          <Box textAlign="center" mb={2}>
            <Button
              startIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              onClick={() => setShowDetails(!showDetails)}
              size="small"
              variant="outlined"
            >
              {showDetails 
                ? (currentLanguage === 'ar' ? 'إخفاء التفاصيل' : 'Hide Details')
                : (currentLanguage === 'ar' ? 'عرض التفاصيل' : 'Show Details')
              }
            </Button>
          </Box>
        )}

        {/* Workflow Steps */}
        <Collapse in={showDetails}>
          <Box>
            <Typography variant="subtitle2" fontWeight="bold" mb={2}>
              {currentLanguage === 'ar' ? 'خطوات سير العمل:' : 'Workflow Steps:'}
            </Typography>
            
            {localWorkflow.steps?.map((step, index) => (
              <WorkflowStep
                key={step.id || index}
                step={step}
                index={index}
                currentLanguage={currentLanguage}
                isRTL={isRTL}
                onStepAction={handleStepAction}
              />
            )) || (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                {currentLanguage === 'ar' ? 'لا توجد خطوات متاحة' : 'No steps available'}
              </Typography>
            )}
          </Box>
        </Collapse>
      </CardContent>

      {/* Action Confirmation Dialog */}
      <Dialog
        open={actionDialog.open}
        onClose={() => setActionDialog({ open: false, action: null })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          {currentLanguage === 'ar' ? 'تأكيد الإجراء' : 'Confirm Action'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {currentLanguage === 'ar' 
              ? `هل أنت متأكد من أنك تريد ${actionDialog.action === 'pause' ? 'إيقاف' : 'إلغاء'} سير العمل هذا؟`
              : `Are you sure you want to ${actionDialog.action} this workflow?`
            }
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog({ open: false, action: null })}>
            {currentLanguage === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button 
            onClick={() => handleWorkflowAction(actionDialog.action)}
            color={actionDialog.action === 'cancel' ? 'error' : 'primary'}
            variant="contained"
          >
            {currentLanguage === 'ar' ? 'تأكيد' : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
});

WorkflowProgressVisualization.displayName = 'WorkflowProgressVisualization';

export default WorkflowProgressVisualization;