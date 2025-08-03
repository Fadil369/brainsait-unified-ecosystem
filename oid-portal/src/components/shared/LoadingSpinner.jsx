import React, { memo, useContext } from 'react';
import { LanguageContext } from '../../contexts/LanguageContext';

/**
 * Enhanced Loading Spinner Component
 * Reusable loading indicator with Arabic RTL support and healthcare context
 * Optimized with React.memo for performance
 */
const LoadingSpinner = memo(({ 
  message, 
  size = 'medium', 
  variant = 'default',
  healthcareContext = null,
  fullScreen = false,
  className = ''
}) => {
  const { t, isRTL, dir } = useContext(LanguageContext) || { 
    t: (key) => key, 
    isRTL: false, 
    dir: 'ltr' 
  };

  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-12 h-12',
    large: 'w-16 h-16',
    xlarge: 'w-20 h-20'
  };

  const variantClasses = {
    default: 'border-gray-200 border-t-blue-600',
    healthcare: 'border-green-200 border-t-green-600',
    nphies: 'border-blue-200 border-t-blue-700',
    ai: 'border-purple-200 border-t-purple-600',
    error: 'border-red-200 border-t-red-600'
  };

  // Default messages based on healthcare context
  const getDefaultMessage = () => {
    if (message) return message;
    
    const contextMessages = {
      nphies: t('loadingNPHIES') || (isRTL ? 'جاري الاتصال بنفيس...' : 'Connecting to NPHIES...'),
      patient: t('loadingPatient') || (isRTL ? 'جاري تحميل بيانات المريض...' : 'Loading patient data...'),
      doctor: t('loadingDoctor') || (isRTL ? 'جاري تحميل بيانات الطبيب...' : 'Loading doctor data...'),
      appointments: t('loadingAppointments') || (isRTL ? 'جاري تحميل المواعيد...' : 'Loading appointments...'),
      ai: t('loadingAI') || (isRTL ? 'الذكاء الاصطناعي يعمل...' : 'AI processing...'),
      default: t('loading') || (isRTL ? 'جاري التحميل...' : 'Loading...')
    };
    
    return contextMessages[healthcareContext] || contextMessages.default;
  };

  const containerClasses = fullScreen 
    ? `fixed inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-50 ${dir}`
    : `flex flex-col items-center justify-center p-8 ${className}`;

  // Healthcare-specific loading animations
  const getHealthcareIcon = () => {
    const iconMap = {
      nphies: '🔗',
      patient: '🏥',
      doctor: '👨‍⚕️',
      appointments: '📅',
      ai: '🤖',
      default: null
    };
    
    return iconMap[healthcareContext] || iconMap.default;
  };

  const icon = getHealthcareIcon();

  return (
    <div className={containerClasses} dir={dir}>
      {/* Icon indicator for healthcare context */}
      {icon && (
        <div className="mb-4 text-3xl opacity-70 animate-pulse">
          {icon}
        </div>
      )}
      
      {/* Spinner */}
      <div className={`animate-spin rounded-full border-4 ${variantClasses[variant]} ${sizeClasses[size]}`}></div>
      
      {/* Message */}
      <p className={`mt-4 text-gray-600 text-center ${isRTL ? 'font-arabic' : ''}`}>
        {getDefaultMessage()}
      </p>
      
      {/* Progress indicator for longer operations */}
      {healthcareContext === 'nphies' && (
        <div className="mt-4 w-48 bg-gray-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
      )}
      
      {/* Healthcare compliance notice */}
      {fullScreen && (
        <div className="mt-6 max-w-sm text-center">
          <p className="text-xs text-gray-500">
            {t('dataSecure') || (isRTL 
              ? 'بياناتك الصحية محمية ومشفرة' 
              : 'Your healthcare data is secure and encrypted'
            )}
          </p>
        </div>
      )}
    </div>
  );
});

// Display name for debugging
LoadingSpinner.displayName = 'LoadingSpinner';

// Specialized loading spinners for different healthcare contexts
export const NPHIESLoadingSpinner = memo((props) => (
  <LoadingSpinner 
    variant="nphies" 
    healthcareContext="nphies" 
    {...props} 
  />
));

export const PatientLoadingSpinner = memo((props) => (
  <LoadingSpinner 
    variant="healthcare" 
    healthcareContext="patient" 
    {...props} 
  />
));

export const DoctorLoadingSpinner = memo((props) => (
  <LoadingSpinner 
    variant="healthcare" 
    healthcareContext="doctor" 
    {...props} 
  />
));

export const AILoadingSpinner = memo((props) => (
  <LoadingSpinner 
    variant="ai" 
    healthcareContext="ai" 
    {...props} 
  />
));

export default LoadingSpinner;