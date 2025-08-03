import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useFHIR } from '../../hooks/useFHIR';
import { useAuth } from '../../hooks/useAuth';
import { useLanguage } from '../../contexts/LanguageContext';
import { useUnifiedHealthcare, HEALTHCARE_CONTEXTS } from '../../contexts/UnifiedHealthcareContext';
import ErrorBoundary from '../shared/ErrorBoundary';
import LoadingSpinner from '../shared/LoadingSpinner';

/**
 * Patient Portal Component
 * Unified React replacement for patient_portal.html
 * Enhanced with FHIR integration, patient self-service features, and unified state management
 */
const PatientPortal = () => {
  // Unified context integration
  const {
    unifiedData,
    activeContext,
    switchContext,
    callUnifiedAPI,
    isLoading: contextLoading,
    hasError,
    getError
  } = useUnifiedHealthcare();
  
  const { t, language, isRTL } = useLanguage();
  const { user } = useAuth();
  const { 
    getPatient, 
    getPatientAppointments,
    createFHIRResource,
    searchPatients,
    isLoading: fhirLoading,
    error: fhirError 
  } = useFHIR();
  
  // Combined loading states
  const isLoading = contextLoading || fhirLoading;

  // Local state management (reduced, focused on UI state)
  const [activeTab, setActiveTab] = useState('overview');
  const [patientData, setPatientData] = useState(null);
  const [appointmentRequest, setAppointmentRequest] = useState({
    type: '',
    preferredDate: '',
    notes: ''
  });
  
  // Unified data extraction with memoization
  const patientPortalData = useMemo(() => {
    const patientContext = unifiedData.overview || {};
    return {
      appointments: patientContext.appointments || [],
      labResults: patientContext.labResults || [],
      prescriptions: patientContext.prescriptions || [],
      medicalHistory: patientContext.medicalHistory || [],
      visitsThisYear: patientContext.visitsThisYear || 12
    };
  }, [unifiedData.overview]);

  // Initialize context and load patient data on component mount
  useEffect(() => {
    // Switch to overview context for patient portal data
    if (activeContext !== HEALTHCARE_CONTEXTS.OVERVIEW) {
      switchContext(HEALTHCARE_CONTEXTS.OVERVIEW);
    }
    loadPatientData();
  }, [activeContext, switchContext]);

  // Load patient's own data using unified API
  const loadPatientData = useCallback(async () => {
    try {
      const patientId = user.patientId || user.id;
      
      // Try unified API first
      await callUnifiedAPI(HEALTHCARE_CONTEXTS.OVERVIEW, 'get_patient_data', {
        patientId: patientId
      });
      
      // Load patient basic info via FHIR as fallback
      const patient = await getPatient(patientId);
      setPatientData(patient);
    } catch (error) {
      console.error('Failed to load patient data:', error);
      // Graceful fallback - try FHIR only
      try {
        const patientId = user.patientId || user.id;
        const patient = await getPatient(patientId);
        setPatientData(patient);
      } catch (fallbackError) {
        console.error('Fallback patient loading failed:', fallbackError);
      }
    }
  }, [callUnifiedAPI, user, getPatient]);

  // Load appointments using unified API with FHIR fallback
  const loadAppointments = useCallback(async (patientId) => {
    try {
      await callUnifiedAPI(HEALTHCARE_CONTEXTS.OVERVIEW, 'get_patient_appointments', {
        patientId: patientId
      });
    } catch (error) {
      console.warn('Unified appointments loading failed, trying FHIR fallback:', error);
      try {
        const appointmentData = await getPatientAppointments(patientId);
        if (appointmentData && appointmentData.entry) {
          // Would need to update unified context with this data
          console.log('Fallback appointments loaded:', appointmentData.entry.length);
        }
      } catch (fallbackError) {
        console.error('Failed to load appointments:', fallbackError);
      }
    }
  }, [callUnifiedAPI, getPatientAppointments]);

  // These functions are no longer needed as data comes from unified context
  // Data is now managed by the UnifiedHealthcareContext

  // Request new appointment using unified API with FHIR fallback
  const requestAppointment = useCallback(async () => {
    if (!appointmentRequest.type || !appointmentRequest.preferredDate) return;

    try {
      // Try unified API first
      const result = await callUnifiedAPI(HEALTHCARE_CONTEXTS.OVERVIEW, 'request_appointment', {
        patientId: patientData?.id || user.patientId || user.id,
        type: appointmentRequest.type,
        preferredDate: appointmentRequest.preferredDate,
        notes: appointmentRequest.notes
      });
      
      if (result) {
        alert(t('appointmentRequested') || (isRTL ? 'تم إرسال طلب الموعد بنجاح' : 'Appointment request submitted successfully'));
        setAppointmentRequest({ type: '', preferredDate: '', notes: '' });
        return;
      }
    } catch (error) {
      console.warn('Unified appointment request failed, trying FHIR fallback:', error);
    }
    
    // Fallback to FHIR
    try {
      const appointment = {
        resourceType: "Appointment",
        status: "proposed",
        serviceType: [{
          coding: [{
            system: "http://terminology.hl7.org/CodeSystem/service-type",
            code: appointmentRequest.type,
            display: appointmentRequest.type
          }]
        }],
        participant: [{
          actor: {
            reference: `Patient/${patientData?.id || user.patientId || user.id}`,
            display: patientData?.displayName || user?.name
          },
          status: "accepted"
        }],
        requestedPeriod: [{
          start: new Date(appointmentRequest.preferredDate).toISOString()
        }],
        comment: appointmentRequest.notes
      };

      const result = await createFHIRResource('Appointment', appointment);
      if (result) {
        alert(t('appointmentRequested') || (isRTL ? 'تم إرسال طلب الموعد بنجاح' : 'Appointment request submitted successfully'));
        setAppointmentRequest({ type: '', preferredDate: '', notes: '' });
        loadAppointments(patientData?.id || user.patientId || user.id);
      }
    } catch (error) {
      console.error('Failed to request appointment:', error);
    }
  }, [appointmentRequest, patientData, user, callUnifiedAPI, createFHIRResource, loadAppointments, t, isRTL]);

  // Navigation tabs with i18next integration
  const tabs = useMemo(() => [
    { id: 'overview', label: t('overview') || (isRTL ? 'نظرة عامة' : 'Overview'), icon: '🏠' },
    { id: 'appointments', label: t('myAppointments') || (isRTL ? 'مواعيدي' : 'My Appointments'), icon: '📅' },
    { id: 'lab-results', label: t('labResults') || (isRTL ? 'نتائج الفحوصات' : 'Lab Results'), icon: '🧪' },
    { id: 'prescriptions', label: t('prescriptions') || (isRTL ? 'الأدوية' : 'Prescriptions'), icon: '💊' },
    { id: 'medical-history', label: t('medicalHistory') || (isRTL ? 'التاريخ الطبي' : 'Medical History'), icon: '📋' },
    { id: 'request-appointment', label: t('requestAppointment') || (isRTL ? 'طلب موعد' : 'Request Appointment'), icon: '➕' }
  ], [t, isRTL]);
  
  // Combined error handling
  const currentError = getError(HEALTHCARE_CONTEXTS.OVERVIEW) || fhirError;
  const hasCurrentError = hasError(HEALTHCARE_CONTEXTS.OVERVIEW) || !!fhirError;

  return (
    <ErrorBoundary>
      <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className={`flex items-center space-x-4 ${isRTL ? 'space-x-reverse' : ''}`}>
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <span className="text-2xl">🏥</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">
                  {t('patientPortal') || (isRTL ? 'بوابة المريض' : 'Patient Portal')}
                </h1>
                <p className="text-purple-100">
                  {isRTL ? `مرحباً ${user?.nameAr || user?.name || ''}` : `Welcome ${user?.name || ''}`}
                </p>
              </div>
            </div>
            <div className={isRTL ? 'text-left' : 'text-right'}>
              <p className="text-sm text-purple-100">
                {t('digitalPatientServices') || (isRTL ? 'خدمات المرضى الرقمية' : 'Digital Patient Services')}
              </p>
              <p className="text-xs text-purple-200">
                {t('yourCareMatters') || (isRTL ? 'رعايتك تهمنا' : 'Your Care Matters')}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-8">
            <LoadingSpinner message={t('loading') || (isRTL ? 'جاري التحميل...' : 'Loading...')} />
          </div>
        )}

        {/* Error State */}
        {hasCurrentError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <p className="text-red-800">{currentError}</p>
              <button 
                onClick={() => window.location.reload()}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                {t('refresh') || (isRTL ? 'تحديث' : 'Refresh')}
              </button>
            </div>
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && patientData && (
          <div className="space-y-6">
            {/* Patient Summary */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'معلوماتي الشخصية' : 'My Information'}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'الاسم' : 'Name'}
                  </label>
                  <p className="text-gray-900 font-medium">{patientData.displayName}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'رقم المريض' : 'Patient ID'}
                  </label>
                  <p className="text-gray-900">{patientData.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'تاريخ الميلاد' : 'Date of Birth'}
                  </label>
                  <p className="text-gray-900">{patientData.birthDate || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'الجنس' : 'Gender'}
                  </label>
                  <p className="text-gray-900">{patientData.gender || 'Not specified'}</p>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-2xl font-bold text-blue-600">{patientPortalData.appointments.length}</div>
                <div className="text-gray-600 text-sm">
                  {t('upcomingAppointments') || (isRTL ? 'المواعيد القادمة' : 'Upcoming Appointments')}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-2xl font-bold text-green-600">{patientPortalData.labResults.length}</div>
                <div className="text-gray-600 text-sm">
                  {t('labResults') || (isRTL ? 'نتائج الفحوصات' : 'Lab Results')}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-2xl font-bold text-purple-600">{patientPortalData.prescriptions.length}</div>
                <div className="text-gray-600 text-sm">
                  {t('activePrescriptions') || (isRTL ? 'الأدوية الحالية' : 'Active Prescriptions')}
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-2xl font-bold text-orange-600">{patientPortalData.visitsThisYear}</div>
                <div className="text-gray-600 text-sm">
                  {t('visitsThisYear') || (isRTL ? 'الزيارات هذا العام' : 'Visits This Year')}
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'النشاط الأخير' : 'Recent Activity'}
              </h3>
              <div className="space-y-3">
                <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                  <span className="mr-3 text-blue-600">📅</span>
                  <div>
                    <p className="font-medium text-blue-900">
                      {currentLanguage === 'ar' ? 'موعد مجدول' : 'Appointment Scheduled'}
                    </p>
                    <p className="text-sm text-blue-700">
                      {currentLanguage === 'ar' ? 'موعد مع د. أحمد في 25 يناير' : 'Appointment with Dr. Ahmed on Jan 25'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center p-3 bg-green-50 rounded-lg">
                  <span className="mr-3 text-green-600">🧪</span>
                  <div>
                    <p className="font-medium text-green-900">
                      {currentLanguage === 'ar' ? 'نتائج التحاليل متاحة' : 'Lab Results Available'}
                    </p>
                    <p className="text-sm text-green-700">
                      {currentLanguage === 'ar' ? 'تحليل الدم الشامل - طبيعي' : 'Complete Blood Count - Normal'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                  <span className="mr-3 text-purple-600">💊</span>
                  <div>
                    <p className="font-medium text-purple-900">
                      {currentLanguage === 'ar' ? 'وصفة طبية جديدة' : 'New Prescription'}
                    </p>
                    <p className="text-sm text-purple-700">
                      {currentLanguage === 'ar' ? 'أسبرين 100 مج - يومياً' : 'Aspirin 100mg - Daily'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                {currentLanguage === 'ar' ? 'مواعيدي' : 'My Appointments'}
              </h3>
            </div>
            <div className="p-6">
              {patientPortalData.appointments.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl text-gray-400">📅</span>
                  </div>
                  <p className="text-gray-600">
                    {t('noAppointments') || (isRTL ? 'لا توجد مواعيد مجدولة' : 'No appointments scheduled')}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {patientPortalData.appointments.map((appointment, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {appointment.serviceType?.[0]?.display || 'General Consultation'}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {currentLanguage === 'ar' ? 'التاريخ: ' : 'Date: '}
                            {new Date(appointment.start).toLocaleDateString()}
                          </p>
                          <p className="text-sm text-gray-600">
                            {currentLanguage === 'ar' ? 'الوقت: ' : 'Time: '}
                            {new Date(appointment.start).toLocaleTimeString()}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          appointment.status === 'booked' 
                            ? 'bg-green-100 text-green-800' 
                            : appointment.status === 'proposed'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {appointment.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Lab Results Tab */}
        {activeTab === 'lab-results' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                {currentLanguage === 'ar' ? 'نتائج الفحوصات' : 'Lab Results'}
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {patientPortalData.labResults.map((result) => (
                  <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{result.test}</h4>
                        <p className="text-sm text-gray-600">
                          {currentLanguage === 'ar' ? 'التاريخ: ' : 'Date: '}{result.date}
                        </p>
                        <p className="text-sm font-medium text-green-600">
                          {currentLanguage === 'ar' ? 'النتيجة: ' : 'Result: '}{result.result}
                        </p>
                      </div>
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        {result.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Prescriptions Tab */}
        {activeTab === 'prescriptions' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800">
                {currentLanguage === 'ar' ? 'الأدوية الحالية' : 'Current Prescriptions'}
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {patientPortalData.prescriptions.map((prescription) => (
                  <div key={prescription.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{prescription.medication}</h4>
                        <p className="text-sm text-gray-600">
                          {currentLanguage === 'ar' ? 'الجرعة: ' : 'Dosage: '}{prescription.dosage}
                        </p>
                        <p className="text-sm text-gray-600">
                          {currentLanguage === 'ar' ? 'الطبيب: ' : 'Prescribed by: '}{prescription.prescriber}
                        </p>
                        <p className="text-sm text-gray-600">
                          {currentLanguage === 'ar' ? 'التاريخ: ' : 'Date: '}{prescription.date}
                        </p>
                      </div>
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        {prescription.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Request Appointment Tab */}
        {activeTab === 'request-appointment' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-6">
              {currentLanguage === 'ar' ? 'طلب موعد جديد' : 'Request New Appointment'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {currentLanguage === 'ar' ? 'نوع الموعد' : 'Appointment Type'}
                </label>
                <select
                  value={appointmentRequest.type}
                  onChange={(e) => setAppointmentRequest({...appointmentRequest, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">
                    {currentLanguage === 'ar' ? 'اختر نوع الموعد' : 'Select appointment type'}
                  </option>
                  <option value="general">
                    {currentLanguage === 'ar' ? 'استشارة عامة' : 'General Consultation'}
                  </option>
                  <option value="followup">
                    {currentLanguage === 'ar' ? 'متابعة' : 'Follow-up'}
                  </option>
                  <option value="specialist">
                    {currentLanguage === 'ar' ? 'استشاري متخصص' : 'Specialist Consultation'}
                  </option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {currentLanguage === 'ar' ? 'التاريخ المفضل' : 'Preferred Date'}
                </label>
                <input
                  type="date"
                  value={appointmentRequest.preferredDate}
                  onChange={(e) => setAppointmentRequest({...appointmentRequest, preferredDate: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {currentLanguage === 'ar' ? 'ملاحظات إضافية' : 'Additional Notes'}
                </label>
                <textarea
                  value={appointmentRequest.notes}
                  onChange={(e) => setAppointmentRequest({...appointmentRequest, notes: e.target.value})}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  placeholder={currentLanguage === 'ar' 
                    ? 'اكتب أي ملاحظات أو أعراض تريد مناقشتها...' 
                    : 'Write any notes or symptoms you want to discuss...'}
                />
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={requestAppointment}
                  disabled={!appointmentRequest.type || !appointmentRequest.preferredDate || isLoading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {currentLanguage === 'ar' ? 'إرسال الطلب' : 'Submit Request'}
                </button>
                
                <button
                  onClick={() => setAppointmentRequest({ type: '', preferredDate: '', notes: '' })}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                >
                  {currentLanguage === 'ar' ? 'مسح' : 'Clear'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
    </ErrorBoundary>
  );
};

export default PatientPortal;