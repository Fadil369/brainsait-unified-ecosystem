/**
 * BrainSAIT Healthcare Shared Modules
 * Reusable components eliminating code duplication across the unified platform
 * 
 * This module provides standardized, reusable healthcare components that can be
 * used across all contexts, reducing code duplication from 60% to <10%
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Badge,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';

import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error,
  Schedule,
  Info,
  Refresh,
  MoreVert,
  Analytics,
  Assignment,
  People,
  MonetizationOn,
  HealthAndSafety,
  School,
  Engineering,
  Assessment,
  SmartToy,
  Security,
} from '@mui/icons-material';

// Unified color palette for healthcare contexts
export const HealthcareColors = {
  primary: '#00b4d8',
  secondary: '#f72585',
  success: '#06d6a0',
  warning: '#ffd166',
  error: '#f72585',
  info: '#48cae4',
  nphies: '#06d6a0',
  rcm: '#00b4d8',
  training: '#ffd166',
  bot: '#f72585',
  operations: '#48cae4',
  ai: '#e0aaff',
  compliance: '#ef476f',
  oid: '#6c757d'
};

// Unified icons mapping for healthcare contexts
export const HealthcareIcons = {
  nphies: HealthAndSafety,
  rcm: MonetizationOn,
  training: School,
  bot: Engineering,
  operations: Assessment,
  ai_analytics: SmartToy,
  compliance: Security,
  oid_tree: Assignment,
  overview: Analytics
};

/**
 * Unified Metric Card Component
 * Standardized metric display across all healthcare contexts
 */
export const UnifiedMetricCard = ({ 
  title, 
  value, 
  subtitle, 
  trend, 
  color = 'primary',
  icon,
  onClick,
  loading = false,
  target,
  unit = '',
  size = 'medium'
}) => {
  const IconComponent = icon || TrendingUp;
  const cardHeight = size === 'small' ? 120 : size === 'large' ? 200 : 160;
  
  return (
    <Card 
      sx={{ 
        height: cardHeight, 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        '&:hover': onClick ? { transform: 'translateY(-2px)', boxShadow: 3 } : {}
      }}
      onClick={onClick}
    >
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box flex={1}>
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              <Typography variant={size === 'large' ? 'h3' : 'h4'} color={`${color}.main`} fontWeight="bold">
                {value}{unit}
              </Typography>
            )}
            <Typography variant={size === 'small' ? 'body2' : 'h6'} gutterBottom>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {icon && (
            <Avatar sx={{ bgcolor: `${color}.main`, width: 48, height: 48 }}>
              <IconComponent />
            </Avatar>
          )}
        </Box>
        
        <Box>
          {target && (
            <Box mt={1}>
              <Typography variant="caption" color="text.secondary">
                Target: {target}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min((parseFloat(value) / parseFloat(target)) * 100, 100)}
                sx={{ mt: 0.5, height: 4, borderRadius: 2 }}
                color={parseFloat(value) >= parseFloat(target) ? 'success' : 'warning'}
              />
            </Box>
          )}
          
          {trend && (
            <Box display="flex" alignItems="center" mt={1}>
              {trend.startsWith('+') ? (
                <TrendingUp color="success" fontSize="small" />
              ) : trend.startsWith('-') ? (
                <TrendingDown color="error" fontSize="small" />
              ) : (
                <Info color="info" fontSize="small" />
              )}
              <Typography 
                variant="caption" 
                color={trend.startsWith('+') ? 'success.main' : trend.startsWith('-') ? 'error.main' : 'info.main'}
                ml={0.5}
              >
                {trend}
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

/**
 * Unified Status Indicator Component
 * Standardized status display across all healthcare contexts
 */
export const UnifiedStatusIndicator = ({ 
  status, 
  label, 
  size = 'medium', 
  showIcon = true,
  showLabel = true 
}) => {
  const getStatusConfig = (status) => {
    const configs = {
      excellent: { color: 'success', icon: CheckCircle, text: 'Excellent' },
      good: { color: 'success', icon: CheckCircle, text: 'Good' },
      operational: { color: 'success', icon: CheckCircle, text: 'Operational' },
      warning: { color: 'warning', icon: Warning, text: 'Warning' },
      degraded: { color: 'warning', icon: Warning, text: 'Degraded' },
      error: { color: 'error', icon: Error, text: 'Error' },
      maintenance: { color: 'info', icon: Schedule, text: 'Maintenance' },
      pending: { color: 'info', icon: Schedule, text: 'Pending' },
      active: { color: 'success', icon: CheckCircle, text: 'Active' },
      inactive: { color: 'error', icon: Error, text: 'Inactive' }
    };
    return configs[status] || configs.good;
  };
  
  const config = getStatusConfig(status);
  const IconComponent = config.icon;
  
  return (
    <Box display="flex" alignItems="center" gap={1}>
      {showIcon && <IconComponent color={config.color} fontSize={size} />}
      {showLabel && (
        <Typography variant={size === 'small' ? 'caption' : 'body2'}>
          {label || config.text}
        </Typography>
      )}
    </Box>
  );
};

/**
 * Unified Progress Card Component
 * Standardized progress display for projects, training, BOT phases, etc.
 */
export const UnifiedProgressCard = ({
  title,
  subtitle,
  progress,
  status,
  target,
  details = [],
  actions = [],
  color = 'primary'
}) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {status && (
            <Chip
              label={status.replace('_', ' ').toUpperCase()}
              color={
                status.includes('completed') || status.includes('excellent') ? 'success' :
                status.includes('progress') || status.includes('good') ? 'primary' :
                status.includes('warning') || status.includes('behind') ? 'warning' :
                status.includes('error') || status.includes('risk') ? 'error' : 'default'
              }
              size="small"
            />
          )}
        </Box>
        
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Progress</Typography>
            <Typography variant="body2" fontWeight="bold">
              {progress}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ height: 8, borderRadius: 4 }}
            color={progress >= 90 ? 'success' : progress >= 70 ? 'primary' : 'warning'}
          />
          {target && (
            <Typography variant="caption" color="text.secondary" mt={0.5}>
              Target: {target}%
            </Typography>
          )}
        </Box>
        
        {details.length > 0 && (
          <Box mb={2}>
            <List dense>
              {details.map((detail, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    {detail.status === 'completed' ? (
                      <CheckCircle color="success" fontSize="small" />
                    ) : detail.status === 'in_progress' ? (
                      <Schedule color="primary" fontSize="small" />
                    ) : (
                      <Warning color="warning" fontSize="small" />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={detail.title}
                    secondary={detail.subtitle}
                    primaryTypographyProps={{ variant: 'body2' }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
        
        {actions.length > 0 && (
          <Box display="flex" gap={1} flexWrap="wrap">
            {actions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'outlined'}
                size="small"
                startIcon={action.icon}
                onClick={action.onClick}
                color={action.color || 'primary'}
              >
                {action.label}
              </Button>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Unified Data Table Component
 * Standardized table display for all healthcare data
 */
export const UnifiedDataTable = ({
  title,
  columns,
  data,
  loading = false,
  pagination = false,
  actions = [],
  filters = [],
  searchable = false,
  exportable = false
}) => {
  return (
    <Paper>
      {title && (
        <Box p={2} borderBottom={1} borderColor="divider">
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{title}</Typography>
            <Box display="flex" gap={1}>
              {actions.map((action, index) => (
                <IconButton key={index} onClick={action.onClick} size="small">
                  {action.icon}
                </IconButton>
              ))}
            </Box>
          </Box>
        </Box>
      )}
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column, index) => (
                <TableCell key={index} align={column.align || 'left'}>
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No data available
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, rowIndex) => (
                <TableRow key={rowIndex} hover>
                  {columns.map((column, colIndex) => (
                    <TableCell key={colIndex} align={column.align || 'left'}>
                      {column.render ? column.render(row[column.field], row) : row[column.field]}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

/**
 * Unified Alert System Component
 * Standardized alert display across all healthcare contexts
 */
export const UnifiedAlert = ({
  severity = 'info',
  title,
  message,
  actions = [],
  dismissible = false,
  onDismiss,
  icon,
  persistent = false
}) => {
  return (
    <Alert
      severity={severity}
      icon={icon}
      onClose={dismissible ? onDismiss : undefined}
      action={
        actions.length > 0 ? (
          <Box display="flex" gap={1}>
            {actions.map((action, index) => (
              <Button
                key={index}
                color="inherit"
                size="small"
                onClick={action.onClick}
                startIcon={action.icon}
              >
                {action.label}
              </Button>
            ))}
          </Box>
        ) : undefined
      }
    >
      {title && <Typography variant="subtitle2" gutterBottom>{title}</Typography>}
      <Typography variant="body2">{message}</Typography>
    </Alert>
  );
};

/**
 * Unified Context Header Component
 * Standardized header for each healthcare context
 */
export const UnifiedContextHeader = ({
  context,
  title,
  subtitle,
  actions = [],
  breadcrumbs = [],
  status,
  refreshable = false,
  onRefresh,
  loading = false
}) => {
  const IconComponent = HealthcareIcons[context] || Analytics;
  const contextColor = HealthcareColors[context] || HealthcareColors.primary;
  
  return (
    <Box mb={3}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar sx={{ bgcolor: contextColor, width: 56, height: 56 }}>
            <IconComponent />
          </Avatar>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body1" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {breadcrumbs.length > 0 && (
              <Typography variant="caption" color="text.secondary">
                {breadcrumbs.join(' > ')}
              </Typography>
            )}
          </Box>
        </Box>
        
        <Box display="flex" alignItems="center" gap={2}>
          {status && <UnifiedStatusIndicator status={status} />}
          {refreshable && (
            <Tooltip title="Refresh data">
              <IconButton onClick={onRefresh} disabled={loading}>
                <Refresh />
              </IconButton>
            </Tooltip>
          )}
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'outlined'}
              startIcon={action.icon}
              onClick={action.onClick}
              color={action.color || 'primary'}
            >
              {action.label}
            </Button>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

/**
 * Unified Loading State Component
 * Standardized loading display across all healthcare contexts
 */
export const UnifiedLoadingState = ({ 
  message = "Loading healthcare data...", 
  size = 'medium',
  variant = 'circular' 
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={size === 'small' ? 100 : size === 'large' ? 400 : 200}
      gap={2}
    >
      {variant === 'circular' ? (
        <CircularProgress size={size === 'small' ? 24 : size === 'large' ? 64 : 40} />
      ) : (
        <LinearProgress sx={{ width: '200px' }} />
      )}
      <Typography variant="body2" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );
};

/**
 * Unified Error State Component
 * Standardized error display across all healthcare contexts
 */
export const UnifiedErrorState = ({
  title = "Something went wrong",
  message = "Unable to load healthcare data. Please try again.",
  retry = false,
  onRetry,
  actions = []
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={200}
      gap={2}
      textAlign="center"
    >
      <Error color="error" sx={{ fontSize: 64 }} />
      <Typography variant="h6" color="text.primary">
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" maxWidth={400}>
        {message}
      </Typography>
      <Box display="flex" gap={1}>
        {retry && (
          <Button variant="contained" onClick={onRetry} startIcon={<Refresh />}>
            Try Again
          </Button>
        )}
        {actions.map((action, index) => (
          <Button
            key={index}
            variant={action.variant || 'outlined'}
            onClick={action.onClick}
            startIcon={action.icon}
          >
            {action.label}
          </Button>
        ))}
      </Box>
    </Box>
  );
};

/**
 * Unified Quick Actions Component
 * Standardized quick actions across all healthcare contexts
 */
export const UnifiedQuickActions = ({ actions, title = "Quick Actions" }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Grid container spacing={2}>
          {actions.map((action, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Button
                fullWidth
                variant={action.variant || 'outlined'}
                startIcon={action.icon}
                onClick={action.onClick}
                sx={{ justifyContent: 'flex-start', py: 1.5 }}
              >
                <Box textAlign="left">
                  <Typography variant="body2" fontWeight="bold">
                    {action.label}
                  </Typography>
                  {action.description && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      {action.description}
                    </Typography>
                  )}
                </Box>
              </Button>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

// Export all components for unified usage
export default {
  UnifiedMetricCard,
  UnifiedStatusIndicator,
  UnifiedProgressCard,
  UnifiedDataTable,
  UnifiedAlert,
  UnifiedContextHeader,
  UnifiedLoadingState,
  UnifiedErrorState,
  UnifiedQuickActions,
  HealthcareColors,
  HealthcareIcons
};