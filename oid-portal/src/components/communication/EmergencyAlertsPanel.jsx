/**
 * Emergency Alerts Panel Component
 * Displays and manages emergency communication alerts for the healthcare platform
 * Supports Arabic RTL layout and real-time emergency notifications
 */

import { memo, useState, useCallback, useMemo } from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Typography,
  Chip,
  Box,
  Button,
  Alert,
  Badge,
  Collapse,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  LocalHospital as EmergencyIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as ResolvedIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Phone as PhoneIcon,
  Message as MessageIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';
import { useCommunication } from '../../hooks/useCommunication';

/**
 * Emergency Level Configuration
 */
const getEmergencyConfig = (level) => {
  switch (level) {
    case 'critical':
      return {
        color: 'error',
        icon: <EmergencyIcon />,
        bgColor: '#d32f2f',
        textColor: '#ffffff',
        priority: 4
      };
    case 'high':
      return {
        color: 'warning',
        icon: <WarningIcon />,
        bgColor: '#f57c00',
        textColor: '#ffffff',
        priority: 3
      };
    case 'medium':
      return {
        color: 'info',
        icon: <InfoIcon />,
        bgColor: '#1976d2',
        textColor: '#ffffff',
        priority: 2
      };
    case 'low':
      return {
        color: 'success',
        icon: <InfoIcon />,
        bgColor: '#388e3c',
        textColor: '#ffffff',
        priority: 1
      };
    default:
      return {
        color: 'default',
        icon: <InfoIcon />,
        bgColor: '#757575',
        textColor: '#ffffff',
        priority: 0
      };
  }
};

/**
 * Emergency Alert Item Component
 */
const EmergencyAlertItem = memo(({ 
  alert, 
  onResolve, 
  onExpand, 
  expanded = false,
  currentLanguage 
}) => {
  const config = getEmergencyConfig(alert.level);
  
  const handleResolve = useCallback(() => {
    onResolve(alert.id);
  }, [onResolve, alert.id]);

  const timeAgo = useMemo(() => {
    const diff = Date.now() - new Date(alert.timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
      return currentLanguage === 'ar' 
        ? `منذ ${days} ${days === 1 ? 'يوم' : 'أيام'}` 
        : `${days} day${days === 1 ? '' : 's'} ago`;
    } else if (hours > 0) {
      return currentLanguage === 'ar' 
        ? `منذ ${hours} ${hours === 1 ? 'ساعة' : 'ساعات'}` 
        : `${hours} hour${hours === 1 ? '' : 's'} ago`;
    } else {
      return currentLanguage === 'ar' 
        ? `منذ ${minutes} ${minutes === 1 ? 'دقيقة' : 'دقائق'}` 
        : `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    }
  }, [alert.timestamp, currentLanguage]);

  return (
    <Card 
      elevation={alert.resolved ? 1 : 3} 
      sx={{ 
        mb: 1,
        borderLeft: `4px solid ${config.bgColor}`,
        opacity: alert.resolved ? 0.7 : 1
      }}
    >
      <ListItem
        button
        onClick={() => onExpand(alert.id)}
        sx={{ 
          py: 1,
          backgroundColor: alert.resolved ? 'grey.100' : 'background.paper'
        }}
      >
        <ListItemAvatar>
          <Avatar 
            sx={{ 
              backgroundColor: config.bgColor,
              color: config.textColor,
              width: 40,
              height: 40
            }}
          >
            {alert.resolved ? <ResolvedIcon /> : config.icon}
          </Avatar>
        </ListItemAvatar>
        
        <ListItemText
          primary={
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="subtitle2" component="span">
                {currentLanguage === 'ar' ? alert.description_ar || alert.description : alert.description}
              </Typography>
              <Chip
                size="small"
                label={alert.level.toUpperCase()}
                sx={{
                  backgroundColor: config.bgColor,
                  color: config.textColor,
                  fontSize: '0.7rem'
                }}
              />
              {alert.resolved && (
                <Chip
                  size="small"
                  label={currentLanguage === 'ar' ? 'محلول' : 'Resolved'}
                  color="success"
                  variant="outlined"
                />
              )}
            </Box>
          }
          secondary={
            <Box display="flex" justifyContent="space-between" alignItems="center" mt={0.5}>
              <Typography variant="caption" color="text.secondary">
                {alert.type} • {timeAgo}
              </Typography>
              {alert.patientId && (
                <Typography variant="caption" color="primary">
                  {currentLanguage === 'ar' ? 'معرف المريض:' : 'Patient ID:'} {alert.patientId}
                </Typography>
              )}
            </Box>
          }
        />
        
        <ListItemSecondaryAction>
          <Box display="flex" alignItems="center" gap={1}>
            {!alert.resolved && (
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleResolve();
                }}
                sx={{ color: 'success.main' }}
              >
                <ResolvedIcon />
              </IconButton>
            )}
            <IconButton size="small">
              {expanded ? <CollapseIcon /> : <ExpandIcon />}
            </IconButton>
          </Box>
        </ListItemSecondaryAction>
      </ListItem>
      
      <Collapse in={expanded}>
        <CardContent sx={{ pt: 0 }}>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>{currentLanguage === 'ar' ? 'النوع:' : 'Type:'}</strong> {alert.type}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            <strong>{currentLanguage === 'ar' ? 'الوقت:' : 'Time:'}</strong> {new Date(alert.timestamp).toLocaleString()}
          </Typography>
          {alert.patientId && (
            <Typography variant="body2" color="text.secondary" paragraph>
              <strong>{currentLanguage === 'ar' ? 'معرف المريض:' : 'Patient ID:'}</strong> {alert.patientId}
            </Typography>
          )}
          
          {/* Action Buttons */}
          <Box display="flex" gap={1} mt={2}>
            <Button
              size="small"
              startIcon={<PhoneIcon />}
              variant="outlined"
              color="primary"
              disabled={alert.resolved}
            >
              {currentLanguage === 'ar' ? 'اتصال' : 'Call'}
            </Button>
            <Button
              size="small"
              startIcon={<MessageIcon />}
              variant="outlined"
              color="secondary"
              disabled={alert.resolved}
            >
              {currentLanguage === 'ar' ? 'رسالة' : 'Message'}
            </Button>
          </Box>
        </CardContent>
      </Collapse>
    </Card>
  );
});

EmergencyAlertItem.displayName = 'EmergencyAlertItem';

/**
 * Emergency Filter Controls
 */
const EmergencyFilters = memo(({ 
  levelFilter, 
  onLevelFilterChange, 
  typeFilter, 
  onTypeFilterChange,
  showResolved,
  onShowResolvedChange,
  currentLanguage 
}) => {
  return (
    <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
      <FormControl size="small" sx={{ minWidth: 120 }}>
        <InputLabel>
          {currentLanguage === 'ar' ? 'المستوى' : 'Level'}
        </InputLabel>
        <Select
          value={levelFilter}
          onChange={(e) => onLevelFilterChange(e.target.value)}
          label={currentLanguage === 'ar' ? 'المستوى' : 'Level'}
        >
          <MenuItem value="all">
            {currentLanguage === 'ar' ? 'الكل' : 'All'}
          </MenuItem>
          <MenuItem value="critical">
            {currentLanguage === 'ar' ? 'حرج' : 'Critical'}
          </MenuItem>
          <MenuItem value="high">
            {currentLanguage === 'ar' ? 'عالي' : 'High'}
          </MenuItem>
          <MenuItem value="medium">
            {currentLanguage === 'ar' ? 'متوسط' : 'Medium'}
          </MenuItem>
          <MenuItem value="low">
            {currentLanguage === 'ar' ? 'منخفض' : 'Low'}
          </MenuItem>
        </Select>
      </FormControl>
      
      <FormControl size="small" sx={{ minWidth: 120 }}>
        <InputLabel>
          {currentLanguage === 'ar' ? 'النوع' : 'Type'}
        </InputLabel>
        <Select
          value={typeFilter}
          onChange={(e) => onTypeFilterChange(e.target.value)}
          label={currentLanguage === 'ar' ? 'النوع' : 'Type'}
        >
          <MenuItem value="all">
            {currentLanguage === 'ar' ? 'الكل' : 'All'}
          </MenuItem>
          <MenuItem value="medical">
            {currentLanguage === 'ar' ? 'طبي' : 'Medical'}
          </MenuItem>
          <MenuItem value="system">
            {currentLanguage === 'ar' ? 'نظام' : 'System'}
          </MenuItem>
          <MenuItem value="security">
            {currentLanguage === 'ar' ? 'أمان' : 'Security'}
          </MenuItem>
        </Select>
      </FormControl>
      
      <Button
        size="small"
        variant={showResolved ? "contained" : "outlined"}
        onClick={() => onShowResolvedChange(!showResolved)}
        startIcon={<ResolvedIcon />}
      >
        {currentLanguage === 'ar' ? 'عرض المحلولة' : 'Show Resolved'}
      </Button>
    </Box>
  );
});

EmergencyFilters.displayName = 'EmergencyFilters';

/**
 * Main Emergency Alerts Panel Component
 */
const EmergencyAlertsPanel = memo(({ compact = false }) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { emergencyAlerts, resolveEmergencyAlert } = useCommunication();
  
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [levelFilter, setLevelFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [showResolved, setShowResolved] = useState(false);

  // Filter alerts
  const filteredAlerts = useMemo(() => {
    let alerts = emergencyAlerts;
    
    // Filter by resolution status
    if (!showResolved) {
      alerts = alerts.filter(alert => !alert.resolved);
    }
    
    // Filter by level
    if (levelFilter !== 'all') {
      alerts = alerts.filter(alert => alert.level === levelFilter);
    }
    
    // Filter by type
    if (typeFilter !== 'all') {
      alerts = alerts.filter(alert => alert.type === typeFilter);
    }
    
    // Sort by priority and timestamp
    return alerts.sort((a, b) => {
      const configA = getEmergencyConfig(a.level);
      const configB = getEmergencyConfig(b.level);
      
      if (configA.priority !== configB.priority) {
        return configB.priority - configA.priority; // Higher priority first
      }
      
      return new Date(b.timestamp) - new Date(a.timestamp); // Newer first
    });
  }, [emergencyAlerts, showResolved, levelFilter, typeFilter]);

  const handleResolveAlert = useCallback((alertId) => {
    resolveEmergencyAlert(alertId);
  }, [resolveEmergencyAlert]);

  const handleExpandAlert = useCallback((alertId) => {
    setExpandedAlert(expandedAlert === alertId ? null : alertId);
  }, [expandedAlert]);

  const unresolvedCount = useMemo(() => {
    return emergencyAlerts.filter(alert => !alert.resolved).length;
  }, [emergencyAlerts]);

  return (
    <Card elevation={2} sx={{ height: compact ? 'auto' : '100%' }}>
      <CardHeader
        avatar={
          <Badge badgeContent={unresolvedCount} color="error">
            <EmergencyIcon color={unresolvedCount > 0 ? 'error' : 'disabled'} />
          </Badge>
        }
        title={currentLanguage === 'ar' ? 'تنبيهات الطوارئ' : 'Emergency Alerts'}
        subheader={
          unresolvedCount > 0
            ? (currentLanguage === 'ar' 
                ? `${unresolvedCount} تنبيه نشط` 
                : `${unresolvedCount} active alert${unresolvedCount === 1 ? '' : 's'}`)
            : (currentLanguage === 'ar' ? 'لا توجد تنبيهات نشطة' : 'No active alerts')
        }
        action={
          <IconButton size="small">
            <RefreshIcon />
          </IconButton>
        }
      />
      
      <CardContent sx={{ pt: 0 }}>
        {!compact && (
          <EmergencyFilters
            levelFilter={levelFilter}
            onLevelFilterChange={setLevelFilter}
            typeFilter={typeFilter}
            onTypeFilterChange={setTypeFilter}
            showResolved={showResolved}
            onShowResolvedChange={setShowResolved}
            currentLanguage={currentLanguage}
          />
        )}
        
        {filteredAlerts.length === 0 ? (
          <Alert severity="info">
            {currentLanguage === 'ar' 
              ? 'لا توجد تنبيهات طوارئ تطابق المرشحات' 
              : 'No emergency alerts match the current filters'}
          </Alert>
        ) : (
          <Box 
            sx={{ 
              maxHeight: compact ? 300 : 500, 
              overflowY: 'auto',
              direction: isRTL ? 'rtl' : 'ltr'
            }}
          >
            {filteredAlerts.map((alert) => (
              <EmergencyAlertItem
                key={alert.id}
                alert={alert}
                onResolve={handleResolveAlert}
                onExpand={handleExpandAlert}
                expanded={expandedAlert === alert.id}
                currentLanguage={currentLanguage}
              />
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
});

EmergencyAlertsPanel.displayName = 'EmergencyAlertsPanel';

export default EmergencyAlertsPanel;