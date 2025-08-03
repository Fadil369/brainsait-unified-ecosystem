/**
 * Communication Status Indicator Component
 * Shows real-time communication status for healthcare identities in the OID tree
 * Supports Arabic RTL layout and BrainSAIT healthcare platform styling
 */

import { memo, useMemo } from 'react';
import { Box, Tooltip, Chip, CircularProgress } from '@mui/material';
import {
  Phone as PhoneIcon,
  VideoCall as VideoIcon,
  Message as MessageIcon,
  Email as EmailIcon,
  WhatsApp as WhatsAppIcon,
  LocalHospital as EmergencyIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';
import { COMMUNICATION_STATUS, COMMUNICATION_CHANNELS } from '../../hooks/useCommunication';

// Communication channel icons
const getChannelIcon = (channel, size = 'small') => {
  const iconProps = { fontSize: size };
  
  switch (channel) {
    case COMMUNICATION_CHANNELS.VOICE:
      return <PhoneIcon {...iconProps} />;
    case COMMUNICATION_CHANNELS.VIDEO:
      return <VideoIcon {...iconProps} />;
    case COMMUNICATION_CHANNELS.SMS:
      return <MessageIcon {...iconProps} />;
    case COMMUNICATION_CHANNELS.EMAIL:
      return <EmailIcon {...iconProps} />;
    case COMMUNICATION_CHANNELS.WHATSAPP:
      return <WhatsAppIcon {...iconProps} />;
    default:
      return <MessageIcon {...iconProps} />;
  }
};

// Status colors and icons
const getStatusConfig = (status) => {
  switch (status) {
    case COMMUNICATION_STATUS.ACTIVE:
      return {
        color: 'success',
        icon: <CheckIcon fontSize="small" />,
        bgColor: '#4caf50',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.CONNECTING:
      return {
        color: 'warning',
        icon: <CircularProgress size={12} color="inherit" />,
        bgColor: '#ff9800',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.ENDED:
      return {
        color: 'default',
        icon: <CheckIcon fontSize="small" />,
        bgColor: '#9e9e9e',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.FAILED:
      return {
        color: 'error',
        icon: <CancelIcon fontSize="small" />,
        bgColor: '#f44336',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.SENDING:
      return {
        color: 'info',
        icon: <CircularProgress size={12} color="inherit" />,
        bgColor: '#2196f3',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.DELIVERED:
      return {
        color: 'success',
        icon: <CheckIcon fontSize="small" />,
        bgColor: '#4caf50',
        textColor: '#ffffff'
      };
    case COMMUNICATION_STATUS.READ:
      return {
        color: 'primary',
        icon: <CheckIcon fontSize="small" />,
        bgColor: '#3f51b5',
        textColor: '#ffffff'
      };
    default:
      return {
        color: 'default',
        icon: <ScheduleIcon fontSize="small" />,
        bgColor: '#9e9e9e',
        textColor: '#ffffff'
      };
  }
};

// Helper functions for labels
const getChannelLabel = (channel, currentLanguage) => {
  const labels = {
    [COMMUNICATION_CHANNELS.VOICE]: {
      ar: 'مكالمة صوتية',
      en: 'Voice Call'
    },
    [COMMUNICATION_CHANNELS.VIDEO]: {
      ar: 'مكالمة فيديو',
      en: 'Video Call'
    },
    [COMMUNICATION_CHANNELS.SMS]: {
      ar: 'رسالة نصية',
      en: 'SMS'
    },
    [COMMUNICATION_CHANNELS.EMAIL]: {
      ar: 'بريد إلكتروني',
      en: 'Email'
    },
    [COMMUNICATION_CHANNELS.WHATSAPP]: {
      ar: 'واتساب',
      en: 'WhatsApp'
    }
  };
  return labels[channel]?.[currentLanguage] || channel;
};

const getStatusLabel = (status, currentLanguage) => {
  const labels = {
    [COMMUNICATION_STATUS.ACTIVE]: {
      ar: 'نشط',
      en: 'Active'
    },
    [COMMUNICATION_STATUS.CONNECTING]: {
      ar: 'جاري الاتصال',
      en: 'Connecting'
    },
    [COMMUNICATION_STATUS.ENDED]: {
      ar: 'انتهى',
      en: 'Ended'
    },
    [COMMUNICATION_STATUS.FAILED]: {
      ar: 'فشل',
      en: 'Failed'
    },
    [COMMUNICATION_STATUS.SENDING]: {
      ar: 'جاري الإرسال',
      en: 'Sending'
    },
    [COMMUNICATION_STATUS.DELIVERED]: {
      ar: 'تم التسليم',
      en: 'Delivered'
    },
    [COMMUNICATION_STATUS.READ]: {
      ar: 'تم القراءة',
      en: 'Read'
    }
  };
  return labels[status]?.[currentLanguage] || status;
};

/**
 * Individual Communication Status Badge
 */
const CommunicationBadge = memo(({ channel, status, lastActivity, onClick }) => {
  const { currentLanguage } = useLanguage();
  const statusConfig = getStatusConfig(status);

  const tooltipTitle = useMemo(() => {
    const channelLabel = getChannelLabel(channel, currentLanguage);
    const statusLabel = getStatusLabel(status, currentLanguage);
    const timeLabel = lastActivity 
      ? (currentLanguage === 'ar' ? 'آخر نشاط:' : 'Last activity:') + ' ' + 
        new Date(lastActivity).toLocaleTimeString()
      : '';
    
    return `${channelLabel} - ${statusLabel}${timeLabel ? '\n' + timeLabel : ''}`;
  }, [channel, status, lastActivity, currentLanguage]);

  return (
    <Tooltip title={tooltipTitle} arrow placement="top">
      <Chip
        icon={getChannelIcon(channel, 'small')}
        label={getStatusLabel(status, currentLanguage)}
        size="small"
        clickable={Boolean(onClick)}
        onClick={onClick}
        sx={{
          backgroundColor: statusConfig.bgColor,
          color: statusConfig.textColor,
          fontSize: '0.7rem',
          height: '20px',
          '& .MuiChip-icon': {
            color: statusConfig.textColor,
            fontSize: '14px'
          },
          '& .MuiChip-label': {
            paddingLeft: '4px',
            paddingRight: '4px'
          },
          margin: '1px',
          cursor: onClick ? 'pointer' : 'default',
          '&:hover': onClick ? {
            opacity: 0.8,
            transform: 'scale(1.05)'
          } : {}
        }}
      />
    </Tooltip>
  );
});

CommunicationBadge.displayName = 'CommunicationBadge';

/**
 * Communication Preferences Indicator
 */
const CommunicationPreferences = memo(({ preferences, compact = true }) => {
  const { currentLanguage } = useLanguage();
  
  if (!preferences) return null;

  const enabledChannels = Object.entries(preferences)
    .filter(([key, value]) => key.startsWith('consent_') && value)
    .map(([key]) => key.replace('consent_', ''));

  if (enabledChannels.length === 0) return null;

  return (
    <Box display="flex" flexWrap="wrap" gap={0.5}>
      {enabledChannels.map(channel => (
        <Tooltip
          key={channel}
          title={currentLanguage === 'ar' 
            ? `مفعل: ${getChannelLabel(channel, currentLanguage)}` 
            : `Enabled: ${getChannelLabel(channel, currentLanguage)}`}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'success.light',
              color: 'success.contrastText',
              borderRadius: '50%',
              width: compact ? 16 : 20,
              height: compact ? 16 : 20,
              justifyContent: 'center',
              fontSize: compact ? '10px' : '12px'
            }}
          >
            {getChannelIcon(channel, compact ? 'inherit' : 'small')}
          </Box>
        </Tooltip>
      ))}
    </Box>
  );
});

CommunicationPreferences.displayName = 'CommunicationPreferences';

/**
 * Main Communication Status Indicator Component
 */
const CommunicationStatusIndicator = memo(({ 
  nodeData, 
  communicationStatus = {}, 
  activeConnections = [], 
  preferences = null,
  onCommunicationAction,
  compact = true,
  showPreferences = true 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  
  // Filter active connections for this node
  const nodeConnections = useMemo(() => {
    return activeConnections.filter(conn => 
      conn.patientId === nodeData.patient_id || 
      conn.patientId === nodeData.national_id ||
      conn.patientId === nodeData.nphies_id
    );
  }, [activeConnections, nodeData]);

  // Get communication status for this node
  const nodeStatus = useMemo(() => {
    const patientId = nodeData.patient_id || nodeData.national_id || nodeData.nphies_id;
    return communicationStatus[patientId] || {};
  }, [communicationStatus, nodeData]);

  // Check if any emergency communication is active
  const hasEmergencyAlert = useMemo(() => {
    return nodeConnections.some(conn => conn.priority === 'emergency');
  }, [nodeConnections]);

  const handleBadgeClick = (channel, status) => {
    if (onCommunicationAction) {
      onCommunicationAction({
        action: 'view_details',
        channel,
        status,
        nodeData
      });
    }
  };

  // Don't render if no communication data
  if (Object.keys(nodeStatus).length === 0 && nodeConnections.length === 0 && !preferences) {
    return null;
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isRTL ? 'row-reverse' : 'row',
        alignItems: 'center',
        gap: 0.5,
        flexWrap: 'wrap'
      }}
    >
      {/* Emergency Alert */}
      {hasEmergencyAlert && (
        <Tooltip title={currentLanguage === 'ar' ? 'تنبيه طوارئ نشط' : 'Active Emergency Alert'}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'error.main',
              color: 'error.contrastText',
              borderRadius: '4px',
              padding: '2px 4px',
              animation: 'pulse 1.5s infinite'
            }}
          >
            <EmergencyIcon fontSize="small" />
          </Box>
        </Tooltip>
      )}

      {/* Active Connections */}
      {nodeConnections.map(connection => (
        <CommunicationBadge
          key={connection.id || `${connection.channel}_${connection.startTime}`}
          channel={connection.channel}
          status={connection.status}
          lastActivity={connection.startTime}
          onClick={() => handleBadgeClick(connection.channel, connection.status)}
        />
      ))}

      {/* Recent Communication Status */}
      {Object.entries(nodeStatus).map(([channel, status]) => (
        <CommunicationBadge
          key={channel}
          channel={channel}
          status={status.status}
          lastActivity={status.lastUpdate}
          onClick={() => handleBadgeClick(channel, status.status)}
        />
      ))}

      {/* Communication Preferences */}
      {showPreferences && preferences && (
        <CommunicationPreferences preferences={preferences} compact={compact} />
      )}
    </Box>
  );
});

CommunicationStatusIndicator.displayName = 'CommunicationStatusIndicator';

export default CommunicationStatusIndicator;