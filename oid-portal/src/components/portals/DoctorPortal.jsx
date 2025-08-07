import { useState, useEffect, useCallback, useMemo } from 'react';
import { Routes } from 'react-router-dom';
import { useFHIR } from '../../hooks/useFHIR';
import { useAuth } from '../../hooks/useAuth';
import { useLanguage } from '../../contexts/LanguageContext';
import { useChatAssistant } from '../../hooks/useChatAssistant';
import { useUnifiedHealthcare, HEALTHCARE_CONTEXTS } from '../../contexts/UnifiedHealthcareContext';
import ErrorBoundary from '../shared/ErrorBoundary';
import LoadingSpinner from '../shared/LoadingSpinner';

/**
 * Doctor Portal Component
 * Unified React replacement for doctor_portal.html
 * Enhanced with FHIR integration, Arabic support, and unified state management
 */
const DoctorPortal = () => {
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
    createSOAPNote, 
    searchPatients,
    getPatientAppointments,
    isLoading: fhirLoading,
    error: fhirError 
  } = useFHIR();
  const { sendMessage, messages, isProcessing } = useChatAssistant();
  
  // Combined loading states
  const isLoading = contextLoading || fhirLoading;

  // Local state management (reduced, focused on UI state)
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [soapNote, setSoapNote] = useState({
    subjective: '',
    objective: '',
    assessment: '',
    plan: ''
  });
  const [voiceRecording, setVoiceRecording] = useState(false);
  const [chatInput, setChatInput] = useState('');
  
  // Unified data extraction with memoization
  const dashboardData = useMemo(() => {
    return {
      appointments: unifiedData.operations?.todayAppointments || [],
      patientsToday: unifiedData.operations?.patientsToday || 0,
      newPatients: unifiedData.operations?.newPatients || 0,
      prescriptions: unifiedData.operations?.prescriptionsToday || 0
    };
  }, [unifiedData.operations]);

  // Initialize context and load data on component mount
  useEffect(() => {
    // Switch to operations context for doctor portal data
    if (activeContext !== HEALTHCARE_CONTEXTS.OPERATIONS) {
      switchContext(HEALTHCARE_CONTEXTS.OPERATIONS);
    }
    loadTodaysAppointments();
  }, [activeContext, switchContext]);

  // Load today's appointments using unified API
  const loadTodaysAppointments = useCallback(async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      await callUnifiedAPI(HEALTHCARE_CONTEXTS.OPERATIONS, 'get_today_appointments', {
        doctorId: user?.id,
        date: today
      });
    } catch (error) {
      console.error('Failed to load appointments:', error);
      // Fallback to FHIR if unified API fails
      try {
        const appointmentData = await getPatientAppointments(null, {
          start: today,
          end: today
        });
        
        if (appointmentData && appointmentData.entry) {
          // Update unified context with fallback data
          const appointments = appointmentData.entry.map(entry => entry.resource);
          // This would need to be implemented in the context
        }
      } catch (fallbackError) {
        console.error('Fallback appointment loading failed:', fallbackError);
      }
    }
  }, [callUnifiedAPI, user?.id, getPatientAppointments]);

  // Handle patient search with unified API first, FHIR fallback
  const handlePatientSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;

    try {
      // Try unified API first
      const unifiedResults = await callUnifiedAPI(HEALTHCARE_CONTEXTS.OPERATIONS, 'search_patients', {
        query: searchQuery,
        limit: 10,
        doctorId: user?.id
      });
      
      if (unifiedResults?.data?.patients) {
        setSearchResults(unifiedResults.data.patients);
        return;
      }
    } catch (error) {
      console.warn('Unified patient search failed, trying FHIR fallback:', error);
    }
    
    // Fallback to FHIR
    try {
      const results = await searchPatients(searchQuery, 10);
      if (results && results.entry) {
        setSearchResults(results.entry.map(entry => entry.resource));
      }
    } catch (error) {
      console.error('Patient search failed:', error);
    }
  }, [searchQuery, callUnifiedAPI, user?.id, searchPatients]);

  // Select patient for examination
  const selectPatient = async (patientId) => {
    try {
      const patient = await getPatient(patientId);
      setSelectedPatient(patient);
      setActiveTab('patient-details');
    } catch (error) {
      console.error('Failed to load patient details:', error);
    }
  };

  // Create SOAP note
  const handleCreateSOAPNote = async () => {
    if (!selectedPatient || !soapNote.subjective) return;

    try {
      const result = await createSOAPNote(selectedPatient.id, soapNote);
      if (result) {
        alert(currentLanguage === 'ar' ? 'تم حفظ السجل الطبي بنجاح' : 'SOAP note saved successfully');
        setSoapNote({ subjective: '', objective: '', assessment: '', plan: '' });
      }
    } catch (error) {
      console.error('Failed to create SOAP note:', error);
    }
  };

  // Handle chat with AI assistant
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    await sendMessage(chatInput);
    setChatInput('');
  };

  // Toggle voice recording (placeholder implementation)
  const toggleVoiceRecording = () => {
    setVoiceRecording(!voiceRecording);
    // Voice recording implementation would go here
  };

  // Navigation tabs with i18next integration
  const tabs = useMemo(() => [
    { id: 'dashboard', label: t('dashboard'), icon: '📊' },
    { id: 'patients', label: t('patients') || (isRTL ? 'المرضى' : 'Patients'), icon: '👥' },
    { id: 'appointments', label: t('appointments') || (isRTL ? 'المواعيد' : 'Appointments'), icon: '📅' },
    { id: 'patient-details', label: t('patientDetails') || (isRTL ? 'تفاصيل المريض' : 'Patient Details'), icon: '🏥' },
    { id: 'ai-assistant', label: t('aiAssistant') || (isRTL ? 'المساعد الذكي' : 'AI Assistant'), icon: '🤖' }
  ], [t, isRTL]);
  
  // Combined error handling
  const currentError = getError(HEALTHCARE_CONTEXTS.OPERATIONS) || fhirError;
  const hasCurrentError = hasError(HEALTHCARE_CONTEXTS.OPERATIONS) || !!fhirError;

  return (
    <ErrorBoundary>
      <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className={`flex items-center space-x-4 ${isRTL ? 'space-x-reverse' : ''}`}>
                <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <span className="text-2xl">👨‍⚕️</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold">
                    {t('doctorPortal') || (isRTL ? 'بوابة الطبيب' : 'Doctor Portal')}
                  </h1>
                  <p className="text-blue-100">
                    {isRTL ? `مرحباً د. ${user?.name || user?.nameAr || ''}` : `Welcome Dr. ${user?.name || ''}`}
                  </p>
                </div>
              </div>
              <div className={isRTL ? 'text-left' : 'text-right'}>
                <p className="text-sm text-blue-100">
                  {t('medicalPlatform') || (isRTL ? 'منصة برين سايت الطبية' : 'BrainSAIT Medical Platform')}
                </p>
                <p className="text-xs text-blue-200">
                  {t('fhirCompliant') || (isRTL ? 'متوافق مع معايير FHIR R4' : 'FHIR R4 Compliant')}
                </p>
              </div>
            </div>
          </div>
        </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
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

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'إحصائيات اليوم' : "Today's Stats"}
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">
                    {t('appointments') || (isRTL ? 'المواعيد' : 'Appointments')}
                  </span>
                  <span className="font-semibold">{dashboardData.appointments.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">
                    {t('newPatients') || (isRTL ? 'المرضى الجدد' : 'New Patients')}
                  </span>
                  <span className="font-semibold">{dashboardData.newPatients}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">
                    {t('prescriptions') || (isRTL ? 'الوصفات الطبية' : 'Prescriptions')}
                  </span>
                  <span className="font-semibold">{dashboardData.prescriptions}</span>
                </div>
              </div>
            </div>

            {/* Recent Appointments */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'المواعيد القادمة' : 'Upcoming Appointments'}
              </h3>
              <div className="space-y-3">
                {dashboardData.appointments.slice(0, 3).map((appointment, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <p className="font-medium text-gray-800">
                        {appointment.subject?.display || 'Patient'}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(appointment.start).toLocaleTimeString()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      appointment.status === 'booked' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'إجراءات سريعة' : 'Quick Actions'}
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => setActiveTab('patients')}
                  className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded transition-colors"
                >
                  <div className="flex items-center">
                    <span className="mr-3">🔍</span>
                    <span className="font-medium">
                      {currentLanguage === 'ar' ? 'البحث عن مريض' : 'Search Patient'}
                    </span>
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('ai-assistant')}
                  className="w-full text-left p-3 bg-green-50 hover:bg-green-100 rounded transition-colors"
                >
                  <div className="flex items-center">
                    <span className="mr-3">🤖</span>
                    <span className="font-medium">
                      {currentLanguage === 'ar' ? 'المساعد الذكي' : 'AI Assistant'}
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Patients Tab */}
        {activeTab === 'patients' && (
          <div className="space-y-6">
            {/* Patient Search */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'البحث عن المرضى' : 'Patient Search'}
              </h3>
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={currentLanguage === 'ar' ? 'اسم المريض أو الرقم القومي' : 'Patient name or ID'}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handlePatientSearch}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {currentLanguage === 'ar' ? 'بحث' : 'Search'}
                </button>
              </div>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800">
                    {currentLanguage === 'ar' ? 'نتائج البحث' : 'Search Results'}
                  </h3>
                </div>
                <div className="divide-y divide-gray-200">
                  {searchResults.map((patient) => (
                    <div key={patient.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {patient.displayName || patient.name?.[0]?.family || 'Unknown'}
                          </h4>
                          <p className="text-sm text-gray-600">
                            ID: {patient.id} | 
                            {currentLanguage === 'ar' ? ' العمر: ' : ' Age: '}
                            {patient.birthDate ? new Date().getFullYear() - new Date(patient.birthDate).getFullYear() : 'Unknown'}
                          </p>
                        </div>
                        <button
                          onClick={() => selectPatient(patient.id)}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          {currentLanguage === 'ar' ? 'اختيار' : 'Select'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Patient Details Tab */}
        {activeTab === 'patient-details' && selectedPatient && (
          <div className="space-y-6">
            {/* Patient Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'معلومات المريض' : 'Patient Information'}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'الاسم' : 'Name'}
                  </label>
                  <p className="text-gray-900">{selectedPatient.displayName}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    {currentLanguage === 'ar' ? 'الرقم القومي' : 'Patient ID'}
                  </label>
                  <p className="text-gray-900">{selectedPatient.id}</p>
                </div>
              </div>
            </div>

            {/* SOAP Note Creation */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  {currentLanguage === 'ar' ? 'إنشاء سجل طبي' : 'Create SOAP Note'}
                </h3>
                <button
                  onClick={toggleVoiceRecording}
                  className={`px-4 py-2 rounded-lg ${
                    voiceRecording 
                      ? 'bg-red-600 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {voiceRecording ? '🛑' : '🎤'} 
                  {currentLanguage === 'ar' ? 'تسجيل صوتي' : 'Voice Recording'}
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {currentLanguage === 'ar' ? 'الأعراض الذاتية (S)' : 'Subjective (S)'}
                  </label>
                  <textarea
                    value={soapNote.subjective}
                    onChange={(e) => setSoapNote({...soapNote, subjective: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={currentLanguage === 'ar' ? 'ما يخبرك به المريض...' : 'What the patient tells you...'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {currentLanguage === 'ar' ? 'الفحص الموضوعي (O)' : 'Objective (O)'}
                  </label>
                  <textarea
                    value={soapNote.objective}
                    onChange={(e) => setSoapNote({...soapNote, objective: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={currentLanguage === 'ar' ? 'ما تجده في الفحص...' : 'What you find on examination...'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {currentLanguage === 'ar' ? 'التقييم (A)' : 'Assessment (A)'}
                  </label>
                  <textarea
                    value={soapNote.assessment}
                    onChange={(e) => setSoapNote({...soapNote, assessment: e.target.value})}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={currentLanguage === 'ar' ? 'التشخيص والتقييم...' : 'Diagnosis and assessment...'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {currentLanguage === 'ar' ? 'الخطة (P)' : 'Plan (P)'}
                  </label>
                  <textarea
                    value={soapNote.plan}
                    onChange={(e) => setSoapNote({...soapNote, plan: e.target.value})}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={currentLanguage === 'ar' ? 'العلاج والمتابعة...' : 'Treatment and follow-up...'}
                  />
                </div>

                <button
                  onClick={handleCreateSOAPNote}
                  disabled={!soapNote.subjective || isLoading}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {currentLanguage === 'ar' ? 'حفظ السجل الطبي' : 'Save SOAP Note'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* AI Assistant Tab */}
        {activeTab === 'ai-assistant' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {currentLanguage === 'ar' ? 'المساعد الذكي الطبي' : 'Medical AI Assistant'}
            </h3>
            
            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 mb-4">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <p>{currentLanguage === 'ar' ? 'ابدأ محادثة مع المساعد الذكي' : 'Start a conversation with the AI assistant'}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-800'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                      <span>{currentLanguage === 'ar' ? 'يفكر...' : 'Thinking...'}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleChatSubmit} className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder={currentLanguage === 'ar' ? 'اكتب سؤالك هنا...' : 'Type your question here...'}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isProcessing}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {currentLanguage === 'ar' ? 'إرسال' : 'Send'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
    </ErrorBoundary>
  );
};

export default DoctorPortal;