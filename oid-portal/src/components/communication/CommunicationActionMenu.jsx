/**
 * Communication Action Menu Component
 * Right-click context menu for communication actions in the OID tree
 * Supports Arabic RTL layout and healthcare-specific communication workflows
 */

import { memo, useState, useCallback } from 'react';
import {
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Alert,
  Box,
  CircularProgress
} from '@mui/material';
import {
  Phone as PhoneIcon,
  VideoCall as VideoIcon,
  Message as MessageIcon,
  Email as EmailIcon,
  WhatsApp as WhatsAppIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  LocalHospital as EmergencyIcon,
  Cancel as _CancelIcon,
  Send as SendIcon,
  AccountTree as WorkflowIcon,
  PlayArrow as _StartWorkflowIcon,
  AutoFixHigh as AutomationIcon,
  Psychology as AIIcon
} from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';
import { useCommunication, COMMUNICATION_CHANNELS, EMERGENCY_LEVELS } from '../../hooks/useCommunication';
import { useUnifiedPyHeart } from '../../hooks/useUnifiedPyHeart';

/**
 * Quick Message Dialog
 */
const QuickMessageDialog = memo(({ open, onClose, nodeData, onSend }) => {
  const { currentLanguage, isRTL } = useLanguage();
  const [message, setMessage] = useState('');
  const [messageAr, setMessageAr] = useState('');
  const [channel, setChannel] = useState(COMMUNICATION_CHANNELS.SMS);
  const [priority, setPriority] = useState('normal');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = useCallback(async () => {
    if (!message.trim() && !messageAr.trim()) return;

    setIsLoading(true);
    try {
      await onSend({
        channel,
        message: message.trim(),
        message_ar: messageAr.trim(),
        priority
      });
      setMessage('');
      setMessageAr('');
      onClose();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  }, [message, messageAr, channel, priority, onSend, onClose]);

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      <DialogTitle>
        {currentLanguage === 'ar' ? 'إرسال رسالة سريعة' : 'Send Quick Message'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          {/* Channel Selection */}
          <FormControl fullWidth>
            <InputLabel>
              {currentLanguage === 'ar' ? 'قناة الاتصال' : 'Communication Channel'}
            </InputLabel>
            <Select
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              label={currentLanguage === 'ar' ? 'قناة الاتصال' : 'Communication Channel'}
            >
              <MenuItem value={COMMUNICATION_CHANNELS.SMS}>
                <ListItemIcon><MessageIcon /></ListItemIcon>
                <ListItemText primary={currentLanguage === 'ar' ? 'رسالة نصية' : 'SMS'} />
              </MenuItem>
              <MenuItem value={COMMUNICATION_CHANNELS.EMAIL}>
                <ListItemIcon><EmailIcon /></ListItemIcon>
                <ListItemText primary={currentLanguage === 'ar' ? 'بريد إلكتروني' : 'Email'} />
              </MenuItem>
              <MenuItem value={COMMUNICATION_CHANNELS.WHATSAPP}>
                <ListItemIcon><WhatsAppIcon /></ListItemIcon>
                <ListItemText primary={currentLanguage === 'ar' ? 'واتساب' : 'WhatsApp'} />
              </MenuItem>
            </Select>
          </FormControl>

          {/* Priority Selection */}
          <FormControl fullWidth>
            <InputLabel>
              {currentLanguage === 'ar' ? 'الأولوية' : 'Priority'}
            </InputLabel>
            <Select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              label={currentLanguage === 'ar' ? 'الأولوية' : 'Priority'}
            >
              <MenuItem value="low">
                {currentLanguage === 'ar' ? 'منخفضة' : 'Low'}
              </MenuItem>
              <MenuItem value="normal">
                {currentLanguage === 'ar' ? 'عادية' : 'Normal'}
              </MenuItem>
              <MenuItem value="high">
                {currentLanguage === 'ar' ? 'عالية' : 'High'}
              </MenuItem>
              <MenuItem value="urgent">
                {currentLanguage === 'ar' ? 'عاجلة' : 'Urgent'}
              </MenuItem>
            </Select>
          </FormControl>

          {/* English Message */}
          <TextField
            label={currentLanguage === 'ar' ? 'الرسالة (باللغة الإنجليزية)' : 'Message (English)'}
            multiline
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={
              currentLanguage === 'ar' 
                ? 'اكتب رسالتك باللغة الإنجليزية...'
                : 'Type your message in English...'
            }
            dir="ltr"
          />

          {/* Arabic Message */}
          <TextField
            label={currentLanguage === 'ar' ? 'الرسالة (باللغة العربية)' : 'Message (Arabic)'}
            multiline
            rows={3}
            value={messageAr}
            onChange={(e) => setMessageAr(e.target.value)}
            placeholder={
              currentLanguage === 'ar' 
                ? 'اكتب رسالتك باللغة العربية...'
                : 'Type your message in Arabic...'
            }
            dir="rtl"
          />

          {/* Patient Info */}
          <Alert severity="info">
            {currentLanguage === 'ar' ? 'المريض:' : 'Patient:'} {nodeData.name}
            <br />
            {nodeData.phone_number && (
              <>
                {currentLanguage === 'ar' ? 'رقم الهاتف:' : 'Phone:'} {nodeData.phone_number}
              </>
            )}
          </Alert>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isLoading}>
          {currentLanguage === 'ar' ? 'إلغاء' : 'Cancel'}
        </Button>
        <Button 
          onClick={handleSend} 
          variant="contained" 
          disabled={isLoading || (!message.trim() && !messageAr.trim())}
          startIcon={isLoading ? <CircularProgress size={16} /> : <SendIcon />}
        >
          {currentLanguage === 'ar' ? 'إرسال' : 'Send'}
        </Button>
      </DialogActions>
    </Dialog>
  );
});

QuickMessageDialog.displayName = 'QuickMessageDialog';

/**
 * Main Communication Action Menu Component
 */
const CommunicationActionMenu = memo(({ 
  anchorEl, 
  open, 
  onClose, 
  nodeData,
  onCommunicationAction 
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const {
    sendMessage,
    initiateVoiceCall,
    initiateVideoConsultation,
    getCommunicationHistory,
    triggerEmergencyCommunication,
    isLoading
  } = useCommunication();

  const {
    isPyHeartReady,
    initiateCommunicationWorkflow,
    initiatePatientRegistrationWorkflow,
    initiateEmergencyResponseWorkflow,
    automationEnabled,
    _WORKFLOW_TYPES
  } = useUnifiedPyHeart({
    enabled: true,
    context: 'communication_menu',
    culturalContext: 'SAUDI_ARABIA',
    enableAutomation: true,
    enableRealTimeUpdates: true
  });

  const [quickMessageOpen, setQuickMessageOpen] = useState(false);

  // Check if node has patient data for communication
  const hasPatientData = nodeData && (
    nodeData.patient_id || 
    nodeData.national_id || 
    nodeData.nphies_id ||
    nodeData.phone_number
  );

  // Check if communication is enabled for this node
  const hasCommEnabled = nodeData && (
    nodeData.consent_sms || 
    nodeData.consent_voice || 
    nodeData.consent_email ||
    nodeData.voiceEnabled
  );

  const handleMenuItemClick = useCallback((action) => {
    onClose();
    
    switch (action) {
      case 'send_message':
        setQuickMessageOpen(true);
        break;
      
      case 'voice_call':
        if (hasPatientData) {
          initiateVoiceCall({
            patient_id: nodeData.patient_id || nodeData.national_id,
            phone_number: nodeData.phone_number,
            name: nodeData.name
          });
        }
        break;
      
      case 'video_consultation':
        if (hasPatientData) {
          initiateVideoConsultation(
            {
              patient_id: nodeData.patient_id || nodeData.national_id,
              name: nodeData.name
            },
            {
              provider_id: 'current_user', // This would come from auth context
              type: 'general_consultation',
              duration: 30
            }
          );
        }
        break;
      
      case 'view_history':
        if (hasPatientData) {
          getCommunicationHistory(nodeData.patient_id || nodeData.national_id);
          if (onCommunicationAction) {
            onCommunicationAction({
              action: 'view_history',
              nodeData
            });
          }
        }
        break;
      
      case 'manage_preferences':
        if (onCommunicationAction) {
          onCommunicationAction({
            action: 'manage_preferences',
            nodeData
          });
        }
        break;
      
      case 'emergency_alert':
        triggerEmergencyCommunication({
          event: {
            event_id: `emergency_${Date.now()}`,
            emergency_type: 'medical',
            emergency_level: EMERGENCY_LEVELS.HIGH,
            patient_id: nodeData.patient_id || nodeData.national_id,
            location: nodeData.location || 'Unknown',
            description: 'Emergency communication initiated from OID tree',
            description_ar: 'تم بدء اتصال الطوارئ من شجرة OID',
            initiated_by: 'current_user'
          },
          contacts: [], // This would be populated from emergency contacts
          patient_data: nodeData,
          user_id: 'current_user'
        });
        
        // Also trigger PyHeart emergency workflow if available
        if (isPyHeartReady && automationEnabled) {
          initiateEmergencyResponseWorkflow({
            patient_id: nodeData.patient_id || nodeData.national_id,
            patient_data: nodeData,
            emergency_type: 'medical',
            priority: 'critical',
            initiated_from: 'communication_menu'
          });
        }
        break;

      case 'start_communication_workflow':
        if (isPyHeartReady && hasPatientData) {
          initiateCommunicationWorkflow({
            patient_id: nodeData.patient_id || nodeData.national_id,
            patient_data: nodeData,
            workflow_type: 'comprehensive_communication',
            channels: [COMMUNICATION_CHANNELS.SMS, COMMUNICATION_CHANNELS.EMAIL],
            language: currentLanguage,
            automation_level: 'high'
          });
        }
        break;

      case 'start_patient_registration_workflow':
        if (isPyHeartReady && hasPatientData) {
          initiatePatientRegistrationWorkflow({
            patient_data: nodeData,
            registration_type: 'update_verification',
            include_communication_preferences: true,
            automation_level: 'medium'
          });
        }
        break;

      case 'ai_assisted_communication':
        if (isPyHeartReady && automationEnabled && hasPatientData) {
          initiateCommunicationWorkflow({
            patient_id: nodeData.patient_id || nodeData.national_id,
            patient_data: nodeData,
            workflow_type: 'ai_assisted_communication',
            ai_features: ['message_optimization', 'cultural_adaptation', 'language_detection'],
            automation_level: 'high'
          });
        }
        break;
      
      default:
        console.log('Unknown action:', action);
    }
  }, [
    onClose, 
    hasPatientData, 
    nodeData, 
    initiateVoiceCall, 
    initiateVideoConsultation,
    getCommunicationHistory,
    triggerEmergencyCommunication,
    onCommunicationAction,
    isPyHeartReady,
    automationEnabled,
    initiateCommunicationWorkflow,
    initiatePatientRegistrationWorkflow,
    initiateEmergencyResponseWorkflow,
    currentLanguage
  ]);

  const handleSendMessage = useCallback(async (messageData) => {
    if (!hasPatientData) return;

    return await sendMessage(
      {
        patient_id: nodeData.patient_id || nodeData.national_id,
        phone_number: nodeData.phone_number,
        name: nodeData.name
      },
      messageData
    );
  }, [hasPatientData, nodeData, sendMessage]);

  // Don't render menu if no patient data
  if (!hasPatientData) {
    return null;
  }

  return (
    <>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={onClose}
        transformOrigin={{
          vertical: 'top',
          horizontal: isRTL ? 'right' : 'left',
        }}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: isRTL ? 'right' : 'left',
        }}
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        {/* Send Message */}
        <MenuItem 
          onClick={() => handleMenuItemClick('send_message')}
          disabled={isLoading || !hasCommEnabled}
        >
          <ListItemIcon>
            <MessageIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText 
            primary={currentLanguage === 'ar' ? 'إرسال رسالة' : 'Send Message'} 
          />
        </MenuItem>

        {/* Voice Call */}
        {nodeData.consent_voice && (
          <MenuItem 
            onClick={() => handleMenuItemClick('voice_call')}
            disabled={isLoading || !nodeData.phone_number}
          >
            <ListItemIcon>
              <PhoneIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText 
              primary={currentLanguage === 'ar' ? 'مكالمة صوتية' : 'Voice Call'} 
            />
          </MenuItem>
        )}

        {/* Video Consultation */}
        {nodeData.voiceEnabled && (
          <MenuItem 
            onClick={() => handleMenuItemClick('video_consultation')}
            disabled={isLoading}
          >
            <ListItemIcon>
              <VideoIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText 
              primary={currentLanguage === 'ar' ? 'استشارة فيديو' : 'Video Consultation'} 
            />
          </MenuItem>
        )}

        <Divider />

        {/* Communication History */}
        <MenuItem onClick={() => handleMenuItemClick('view_history')}>
          <ListItemIcon>
            <HistoryIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText 
            primary={currentLanguage === 'ar' ? 'تاريخ الاتصالات' : 'Communication History'} 
          />
        </MenuItem>

        {/* Preferences */}
        <MenuItem onClick={() => handleMenuItemClick('manage_preferences')}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText 
            primary={currentLanguage === 'ar' ? 'إدارة التفضيلات' : 'Manage Preferences'} 
          />
        </MenuItem>

        <Divider />

        {/* PyHeart Workflow Options */}
        {isPyHeartReady && automationEnabled && (
          <>
            <MenuItem 
              onClick={() => handleMenuItemClick('start_communication_workflow')}
              disabled={isLoading || !hasPatientData}
            >
              <ListItemIcon>
                <WorkflowIcon fontSize="small" color="secondary" />
              </ListItemIcon>
              <ListItemText 
                primary={currentLanguage === 'ar' ? 'بدء سير عمل التواصل' : 'Start Communication Workflow'} 
              />
            </MenuItem>

            <MenuItem 
              onClick={() => handleMenuItemClick('ai_assisted_communication')}
              disabled={isLoading || !hasPatientData}
            >
              <ListItemIcon>
                <AIIcon fontSize="small" color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary={currentLanguage === 'ar' ? 'تواصل بمساعدة الذكاء الاصطناعي' : 'AI-Assisted Communication'} 
              />
            </MenuItem>

            <MenuItem 
              onClick={() => handleMenuItemClick('start_patient_registration_workflow')}
              disabled={isLoading || !hasPatientData}
            >
              <ListItemIcon>
                <AutomationIcon fontSize="small" color="success" />
              </ListItemIcon>
              <ListItemText 
                primary={currentLanguage === 'ar' ? 'تحديث بيانات المريض' : 'Update Patient Registration'} 
              />
            </MenuItem>

            <Divider />
          </>
        )}

        {/* Emergency Alert */}
        <MenuItem 
          onClick={() => handleMenuItemClick('emergency_alert')}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <EmergencyIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText 
            primary={currentLanguage === 'ar' ? 'تنبيه طوارئ' : 'Emergency Alert'} 
          />
        </MenuItem>
      </Menu>

      {/* Quick Message Dialog */}
      <QuickMessageDialog
        open={quickMessageOpen}
        onClose={() => setQuickMessageOpen(false)}
        nodeData={nodeData}
        onSend={handleSendMessage}
      />
    </>
  );
});

CommunicationActionMenu.displayName = 'CommunicationActionMenu';

export default CommunicationActionMenu;