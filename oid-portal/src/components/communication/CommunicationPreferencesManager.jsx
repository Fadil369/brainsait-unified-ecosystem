/**
 * Communication Preferences Manager Component
 * Manages patient communication preferences including channels, language, and consent
 * Supports Arabic RTL layout and HIPAA-compliant preference management
 */

import { memo, useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormGroup,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Box,
  Alert,
  TextField,
  Grid,
  Card,
  CardContent,
  CardHeader,
  CircularProgress,
  Snackbar
} from '@mui/material';
import {
  Phone as PhoneIcon,
  VideoCall as VideoIcon,
  Message as MessageIcon,
  Email as EmailIcon,
  WhatsApp as WhatsAppIcon,
  Language as LanguageIcon,
  Security as SecurityIcon,
  AccessTime as TimeIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';
import { useLanguage } from '../../hooks/useLanguage';
import { useCommunication } from '../../hooks/useCommunication';

/**
 * Language Preference Selector
 */
const LanguagePreferenceSelector = memo(({ value, onChange, disabled }) => {
  const { currentLanguage } = useLanguage();
  
  return (
    <FormControl fullWidth disabled={disabled}>
      <InputLabel>
        {currentLanguage === 'ar' ? 'اللغة المفضلة للتواصل' : 'Preferred Communication Language'}
      </InputLabel>
      <Select
        value={value || 'ar'}
        onChange={(e) => onChange(e.target.value)}
        label={currentLanguage === 'ar' ? 'اللغة المفضلة للتواصل' : 'Preferred Communication Language'}
      >
        <MenuItem value="ar">
          العربية (Arabic)
        </MenuItem>
        <MenuItem value="en">
          English (الإنجليزية)
        </MenuItem>
        <MenuItem value="both">
          {currentLanguage === 'ar' ? 'كلاهما' : 'Both Languages'}
        </MenuItem>
      </Select>
    </FormControl>
  );
});

LanguagePreferenceSelector.displayName = 'LanguagePreferenceSelector';

/**
 * Communication Channel Preferences
 */
const ChannelPreferences = memo(({ preferences, onChange, disabled }) => {
  const { currentLanguage } = useLanguage();
  
  const channels = [
    {
      key: 'consent_sms',
      icon: <MessageIcon />,
      label: {
        ar: 'الرسائل النصية (SMS)',
        en: 'Text Messages (SMS)'
      },
      description: {
        ar: 'تلقي تذكيرات المواعيد والنتائج عبر الرسائل النصية',
        en: 'Receive appointment reminders and results via text messages'
      }
    },
    {
      key: 'consent_voice',
      icon: <PhoneIcon />,
      label: {
        ar: 'المكالمات الصوتية',
        en: 'Voice Calls'
      },
      description: {
        ar: 'تلقي مكالمات صوتية للمواعيد المهمة والحالات الطارئة',
        en: 'Receive voice calls for important appointments and emergencies'
      }
    },
    {
      key: 'consent_video',
      icon: <VideoIcon />,
      label: {
        ar: 'استشارات الفيديو',
        en: 'Video Consultations'
      },
      description: {
        ar: 'المشاركة في استشارات طبية عبر مكالمات الفيديو',
        en: 'Participate in medical consultations via video calls'
      }
    },
    {
      key: 'consent_email',
      icon: <EmailIcon />,
      label: {
        ar: 'البريد الإلكتروني',
        en: 'Email Communications'
      },
      description: {
        ar: 'تلقي التقارير الطبية والوثائق عبر البريد الإلكتروني',
        en: 'Receive medical reports and documents via email'
      }
    },
    {
      key: 'consent_whatsapp',
      icon: <WhatsAppIcon />,
      label: {
        ar: 'واتساب',
        en: 'WhatsApp Messaging'
      },
      description: {
        ar: 'تلقي رسائل عبر واتساب للتواصل السريع',
        en: 'Receive messages via WhatsApp for quick communication'
      }
    }
  ];

  const handleChannelChange = useCallback((channelKey, enabled) => {
    onChange({
      ...preferences,
      [channelKey]: enabled
    });
  }, [preferences, onChange]);

  return (
    <Card elevation={2}>
      <CardHeader
        avatar={<NotificationsIcon />}
        title={currentLanguage === 'ar' ? 'قنوات التواصل' : 'Communication Channels'}
        subheader={currentLanguage === 'ar' 
          ? 'اختر الطرق المفضلة لتلقي الرسائل الطبية' 
          : 'Choose your preferred methods for receiving medical communications'
        }
      />
      <CardContent>
        <FormGroup>
          {channels.map((channel) => (
            <Box key={channel.key} mb={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={preferences[channel.key] || false}
                    onChange={(e) => handleChannelChange(channel.key, e.target.checked)}
                    disabled={disabled}
                    color="primary"
                  />
                }
                label={
                  <Box display="flex" alignItems="center" gap={1}>
                    {channel.icon}
                    <Typography variant="body1" fontWeight="medium">
                      {channel.label[currentLanguage]}
                    </Typography>
                  </Box>
                }
              />
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ ml: 5, mt: 0.5 }}
              >
                {channel.description[currentLanguage]}
              </Typography>
            </Box>
          ))}
        </FormGroup>
      </CardContent>
    </Card>
  );
});

ChannelPreferences.displayName = 'ChannelPreferences';

/**
 * Emergency Contact Preferences
 */
const EmergencyContactPreferences = memo(({ preferences, onChange, disabled }) => {
  const { currentLanguage } = useLanguage();
  
  const handleChange = useCallback((field, value) => {
    onChange({
      ...preferences,
      [field]: value
    });
  }, [preferences, onChange]);

  return (
    <Card elevation={2}>
      <CardHeader
        avatar={<SecurityIcon color="error" />}
        title={currentLanguage === 'ar' ? 'جهة الاتصال في الطوارئ' : 'Emergency Contact'}
        subheader={currentLanguage === 'ar' 
          ? 'معلومات الاتصال في الحالات الطارئة' 
          : 'Contact information for emergency situations'
        }
      />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label={currentLanguage === 'ar' ? 'اسم جهة الاتصال' : 'Emergency Contact Name'}
              value={preferences.emergency_contact_name || ''}
              onChange={(e) => handleChange('emergency_contact_name', e.target.value)}
              disabled={disabled}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label={currentLanguage === 'ar' ? 'رقم الهاتف' : 'Phone Number'}
              value={preferences.emergency_contact_phone || ''}
              onChange={(e) => handleChange('emergency_contact_phone', e.target.value)}
              disabled={disabled}
              dir="ltr"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label={currentLanguage === 'ar' ? 'صلة القرابة' : 'Relationship'}
              value={preferences.emergency_contact_relationship || ''}
              onChange={(e) => handleChange('emergency_contact_relationship', e.target.value)}
              disabled={disabled}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.emergency_contact_consent || false}
                  onChange={(e) => handleChange('emergency_contact_consent', e.target.checked)}
                  disabled={disabled}
                  color="primary"
                />
              }
              label={currentLanguage === 'ar' 
                ? 'الموافقة على إشعار جهة الاتصال في الطوارئ' 
                : 'Consent to notify emergency contact'
              }
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
});

EmergencyContactPreferences.displayName = 'EmergencyContactPreferences';

/**
 * Communication Time Preferences
 */
const TimePreferences = memo(({ preferences, onChange, disabled }) => {
  const { currentLanguage } = useLanguage();
  
  const handleChange = useCallback((field, value) => {
    onChange({
      ...preferences,
      [field]: value
    });
  }, [preferences, onChange]);

  return (
    <Card elevation={2}>
      <CardHeader
        avatar={<TimeIcon />}
        title={currentLanguage === 'ar' ? 'أوقات التواصل المفضلة' : 'Preferred Communication Times'}
        subheader={currentLanguage === 'ar' 
          ? 'تحديد الأوقات المناسبة لتلقي الاتصالات' 
          : 'Set your preferred times for receiving communications'
        }
      />
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="time"
              label={currentLanguage === 'ar' ? 'من الساعة' : 'Available From'}
              value={preferences.available_from || '08:00'}
              onChange={(e) => handleChange('available_from', e.target.value)}
              disabled={disabled}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="time"
              label={currentLanguage === 'ar' ? 'إلى الساعة' : 'Available Until'}
              value={preferences.available_until || '18:00'}
              onChange={(e) => handleChange('available_until', e.target.value)}
              disabled={disabled}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth disabled={disabled}>
              <InputLabel>
                {currentLanguage === 'ar' ? 'المنطقة الزمنية' : 'Time Zone'}
              </InputLabel>
              <Select
                value={preferences.timezone || 'Asia/Riyadh'}
                onChange={(e) => handleChange('timezone', e.target.value)}
                label={currentLanguage === 'ar' ? 'المنطقة الزمنية' : 'Time Zone'}
              >
                <MenuItem value="Asia/Riyadh">
                  {currentLanguage === 'ar' ? 'توقيت الرياض (GMT+3)' : 'Riyadh Time (GMT+3)'}
                </MenuItem>
                <MenuItem value="Asia/Dubai">
                  {currentLanguage === 'ar' ? 'توقيت دبي (GMT+4)' : 'Dubai Time (GMT+4)'}
                </MenuItem>
                <MenuItem value="UTC">
                  {currentLanguage === 'ar' ? 'التوقيت العالمي المنسق' : 'UTC Time'}
                </MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
});

TimePreferences.displayName = 'TimePreferences';

/**
 * Main Communication Preferences Manager Component
 */
const CommunicationPreferencesManager = memo(({ 
  open, 
  onClose, 
  nodeData,
  initialPreferences = {}
}) => {
  const { currentLanguage, isRTL } = useLanguage();
  const { updateCommunicationPreferences, isLoading } = useCommunication();
  
  const [preferences, setPreferences] = useState(initialPreferences);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Update preferences when initial preferences change
  useEffect(() => {
    setPreferences(initialPreferences);
    setHasChanges(false);
  }, [initialPreferences]);

  // Track changes
  useEffect(() => {
    const hasChanged = JSON.stringify(preferences) !== JSON.stringify(initialPreferences);
    setHasChanges(hasChanged);
  }, [preferences, initialPreferences]);

  const handlePreferenceChange = useCallback((updates) => {
    setPreferences(prev => ({ ...prev, ...updates }));
  }, []);

  const handleSave = useCallback(async () => {
    if (!nodeData?.patient_id && !nodeData?.national_id) {
      setSaveError('Patient ID not found');
      return;
    }

    try {
      setSaveError(null);
      const patientId = nodeData.patient_id || nodeData.national_id;
      
      await updateCommunicationPreferences(patientId, preferences);
      
      setSaveSuccess(true);
      setHasChanges(false);
      
      // Auto-close after successful save
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 2000);
      
    } catch (error) {
      setSaveError(error.message || 'Failed to save preferences');
    }
  }, [nodeData, preferences, updateCommunicationPreferences, onClose]);

  const handleClose = useCallback(() => {
    if (hasChanges) {
      const confirmClose = window.confirm(
        currentLanguage === 'ar' 
          ? 'لديك تغييرات غير محفوظة. هل تريد المغادرة بدون حفظ؟'
          : 'You have unsaved changes. Do you want to leave without saving?'
      );
      if (!confirmClose) return;
    }
    
    setPreferences(initialPreferences);
    setHasChanges(false);
    setSaveError(null);
    onClose();
  }, [hasChanges, initialPreferences, currentLanguage, onClose]);

  return (
    <>
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <LanguageIcon />
            <Typography variant="h6">
              {currentLanguage === 'ar' 
                ? 'إدارة تفضيلات التواصل' 
                : 'Manage Communication Preferences'
              }
            </Typography>
          </Box>
          {nodeData && (
            <Typography variant="subtitle2" color="text.secondary">
              {currentLanguage === 'ar' ? 'المريض:' : 'Patient:'} {nodeData.name}
            </Typography>
          )}
        </DialogTitle>

        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            {/* Language Preference */}
            <Card elevation={2}>
              <CardHeader
                avatar={<LanguageIcon />}
                title={currentLanguage === 'ar' ? 'تفضيلات اللغة' : 'Language Preferences'}
              />
              <CardContent>
                <LanguagePreferenceSelector
                  value={preferences.preferred_language}
                  onChange={(value) => handlePreferenceChange({ preferred_language: value })}
                  disabled={isLoading}
                />
              </CardContent>
            </Card>

            {/* Communication Channels */}
            <ChannelPreferences
              preferences={preferences}
              onChange={handlePreferenceChange}
              disabled={isLoading}
            />

            {/* Time Preferences */}
            <TimePreferences
              preferences={preferences}
              onChange={handlePreferenceChange}
              disabled={isLoading}
            />

            {/* Emergency Contact */}
            <EmergencyContactPreferences
              preferences={preferences}
              onChange={handlePreferenceChange}
              disabled={isLoading}
            />

            {/* HIPAA Compliance Notice */}
            <Alert severity="info">
              <Typography variant="body2">
                {currentLanguage === 'ar' 
                  ? 'جميع تفضيلات التواصل محمية وفقاً لقوانين خصوصية البيانات الصحية (HIPAA) ونظام حماية البيانات الشخصية السعودي.'
                  : 'All communication preferences are protected under HIPAA privacy laws and Saudi Personal Data Protection regulations.'
                }
              </Typography>
            </Alert>

            {/* Error Display */}
            {saveError && (
              <Alert severity="error">
                {saveError}
              </Alert>
            )}
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isLoading}>
            {currentLanguage === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={isLoading || !hasChanges}
            startIcon={isLoading ? <CircularProgress size={16} /> : null}
          >
            {currentLanguage === 'ar' ? 'حفظ التفضيلات' : 'Save Preferences'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={saveSuccess}
        autoHideDuration={3000}
        onClose={() => setSaveSuccess(false)}
        message={currentLanguage === 'ar' 
          ? 'تم حفظ تفضيلات التواصل بنجاح' 
          : 'Communication preferences saved successfully'
        }
      />
    </>
  );
});

CommunicationPreferencesManager.displayName = 'CommunicationPreferencesManager';

export default CommunicationPreferencesManager;