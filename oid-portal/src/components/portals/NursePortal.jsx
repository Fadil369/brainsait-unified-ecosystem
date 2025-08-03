import React, { useState, useEffect } from 'react';
import { useFHIR } from '../../hooks/useFHIR';
import { useAuth } from '../../hooks/useAuth';
import { useLanguage } from '../../hooks/useLanguage';

/**
 * Nurse Portal Component
 * Unified React replacement for nurse_portal.html
 * Enhanced with FHIR integration and patient care workflows
 */
const NursePortal = () => {
  const { currentLanguage, isRTL } = useLanguage();
  const { user } = useAuth();
  const { 
    getPatient, 
    getPatientAppointments,
    createFHIRResource,
    updateFHIRResource,
    searchPatients,
    isLoading,
    error 
  } = useFHIR();

  // State management
  const [activeTab, setActiveTab] = useState('patient-care');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientList, setPatientList] = useState([]);
  const [vitals, setVitals] = useState({
    temperature: '',
    bloodPressure: '',
    heartRate: '',
    respiratoryRate: '',
    oxygenSaturation: '',
    painLevel: ''
  });
  const [medicationLog, setMedicationLog] = useState([]);
  const [nursingNotes, setNursingNotes] = useState('');
  const [careplan, setCareplan] = useState([]);

  // Load assigned patients on component mount
  useEffect(() => {
    loadAssignedPatients();
  }, []);

  // Load patients assigned to this nurse
  const loadAssignedPatients = async () => {
    try {
      // In a real implementation, this would filter by nurse assignment
      const patients = await searchPatients('', 20);
      if (patients && patients.entry) {
        setPatientList(patients.entry.map(entry => entry.resource));
      }
    } catch (error) {
      console.error('Failed to load assigned patients:', error);
    }
  };

  // Select patient for care
  const selectPatientForCare = async (patientId) => {
    try {
      const patient = await getPatient(patientId);
      setSelectedPatient(patient);
      loadPatientCareData(patientId);
    } catch (error) {
      console.error('Failed to load patient details:', error);
    }
  };

  // Load patient care data (vitals, medications, etc.)
  const loadPatientCareData = async (patientId) => {
    try {
      // Load recent vitals, medications, and care plans
      // This would be implemented with proper FHIR queries
      setVitals({
        temperature: '36.5°C',
        bloodPressure: '120/80',
        heartRate: '72',
        respiratoryRate: '16',
        oxygenSaturation: '98%',
        painLevel: '2/10'
      });
    } catch (error) {
      console.error('Failed to load patient care data:', error);
    }
  };

  // Record vital signs
  const recordVitalSigns = async () => {
    if (!selectedPatient) return;

    try {
      const vitalSignsObservation = {
        resourceType: "Observation",
        status: "final",
        category: [{
          coding: [{
            system: "http://terminology.hl7.org/CodeSystem/observation-category",
            code: "vital-signs",
            display: "Vital Signs"
          }]
        }],
        subject: {
          reference: `Patient/${selectedPatient.id}`
        },
        effectiveDateTime: new Date().toISOString(),
        performer: [{
          reference: `Practitioner/${user.id}`,
          display: user.name
        }],
        component: [
          {
            code: { coding: [{ system: "http://loinc.org", code: "8310-5", display: "Body temperature" }] },
            valueQuantity: { value: parseFloat(vitals.temperature), unit: "Cel" }
          },
          {
            code: { coding: [{ system: "http://loinc.org", code: "8480-6", display: "Systolic blood pressure" }] },
            valueQuantity: { value: parseInt(vitals.bloodPressure.split('/')[0]), unit: "mmHg" }
          },
          {
            code: { coding: [{ system: "http://loinc.org", code: "8867-4", display: "Heart rate" }] },
            valueQuantity: { value: parseInt(vitals.heartRate), unit: "/min" }
          }
        ]
      };

      const result = await createFHIRResource('Observation', vitalSignsObservation);
      if (result) {
        alert(currentLanguage === 'ar' ? 'تم حفظ العلامات الحيوية بنجاح' : 'Vital signs recorded successfully');
      }
    } catch (error) {
      console.error('Failed to record vital signs:', error);
    }
  };

  // Create nursing note
  const createNursingNote = async () => {
    if (!selectedPatient || !nursingNotes.trim()) return;

    try {
      const nursingNote = {
        resourceType: "DocumentReference",
        status: "current",
        type: {
          coding: [{
            system: "http://loinc.org",
            code: "34109-9",
            display: "Nursing note"
          }]
        },
        subject: {
          reference: `Patient/${selectedPatient.id}`
        },
        author: [{
          reference: `Practitioner/${user.id}`,
          display: user.name
        }],
        date: new Date().toISOString(),
        content: [{
          attachment: {
            contentType: "text/plain",
            data: btoa(nursingNotes)
          }
        }]
      };

      const result = await createFHIRResource('DocumentReference', nursingNote);
      if (result) {
        alert(currentLanguage === 'ar' ? 'تم حفظ الملاحظة التمريضية بنجاح' : 'Nursing note created successfully');
        setNursingNotes('');
      }
    } catch (error) {
      console.error('Failed to create nursing note:', error);
    }
  };

  // Navigation tabs
  const tabs = [
    { id: 'patient-care', label: currentLanguage === 'ar' ? 'رعاية المرضى' : 'Patient Care', icon: '🏥' },
    { id: 'vital-signs', label: currentLanguage === 'ar' ? 'العلامات الحيوية' : 'Vital Signs', icon: '💓' },
    { id: 'medications', label: currentLanguage === 'ar' ? 'الأدوية' : 'Medications', icon: '💊' },
    { id: 'nursing-notes', label: currentLanguage === 'ar' ? 'الملاحظات التمريضية' : 'Nursing Notes', icon: '📝' },
    { id: 'care-plans', label: currentLanguage === 'ar' ? 'خطط الرعاية' : 'Care Plans', icon: '📋' }
  ];

  return (
    <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <span className="text-2xl">👩‍⚕️</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">
                  {currentLanguage === 'ar' ? 'بوابة الممرضة' : 'Nurse Portal'}
                </h1>
                <p className="text-green-100">
                  {currentLanguage === 'ar' ? `مرحباً ${user?.name || ''}` : `Welcome ${user?.name || ''}`}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-green-100">
                {currentLanguage === 'ar' ? 'نظام الرعاية التمريضية' : 'Nursing Care System'}
              </p>
              <p className="text-xs text-green-200">
                {currentLanguage === 'ar' ? 'الجودة والسلامة أولاً' : 'Quality & Safety First'}
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
                    ? 'border-green-500 text-green-600'
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
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">
              {currentLanguage === 'ar' ? 'جاري التحميل...' : 'Loading...'}
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Patient List Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                {currentLanguage === 'ar' ? 'مرضى تحت الرعاية' : 'Patients Under Care'}
              </h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {patientList.map((patient) => (
                  <div
                    key={patient.id}
                    onClick={() => selectPatientForCare(patient.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedPatient?.id === patient.id
                        ? 'bg-green-50 border-2 border-green-200'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <p className="font-medium text-gray-900">
                      {patient.displayName || patient.name?.[0]?.family || 'Unknown'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {currentLanguage === 'ar' ? 'غرفة: ' : 'Room: '}101A
                    </p>
                    <div className="flex items-center mt-2">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      <span className="text-xs text-gray-500">
                        {currentLanguage === 'ar' ? 'مستقر' : 'Stable'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            {!selectedPatient ? (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-4xl text-gray-400">👥</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {currentLanguage === 'ar' ? 'اختر مريضاً' : 'Select a Patient'}
                </h3>
                <p className="text-gray-600">
                  {currentLanguage === 'ar' 
                    ? 'اختر مريضاً من القائمة لبدء الرعاية' 
                    : 'Choose a patient from the list to start providing care'}
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Patient Header */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">
                        {selectedPatient.displayName}
                      </h2>
                      <p className="text-gray-600">
                        {currentLanguage === 'ar' ? 'رقم المريض: ' : 'Patient ID: '}{selectedPatient.id}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">
                        {currentLanguage === 'ar' ? 'آخر تحديث: ' : 'Last Updated: '}
                        {new Date().toLocaleString()}
                      </p>
                      <div className="flex items-center mt-1">
                        <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                        <span className="text-sm text-green-600">
                          {currentLanguage === 'ar' ? 'تحت الرعاية' : 'Under Care'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Vital Signs Tab */}
                {activeTab === 'vital-signs' && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-6">
                      {currentLanguage === 'ar' ? 'العلامات الحيوية' : 'Vital Signs'}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'درجة الحرارة (°C)' : 'Temperature (°C)'}
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          value={vitals.temperature}
                          onChange={(e) => setVitals({...vitals, temperature: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'ضغط الدم' : 'Blood Pressure (mmHg)'}
                        </label>
                        <input
                          type="text"
                          value={vitals.bloodPressure}
                          onChange={(e) => setVitals({...vitals, bloodPressure: e.target.value})}
                          placeholder="120/80"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'معدل القلب' : 'Heart Rate (bpm)'}
                        </label>
                        <input
                          type="number"
                          value={vitals.heartRate}
                          onChange={(e) => setVitals({...vitals, heartRate: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'معدل التنفس' : 'Respiratory Rate (/min)'}
                        </label>
                        <input
                          type="number"
                          value={vitals.respiratoryRate}
                          onChange={(e) => setVitals({...vitals, respiratoryRate: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'تشبع الأكسجين (%)' : 'Oxygen Saturation (%)'}
                        </label>
                        <input
                          type="number"
                          value={vitals.oxygenSaturation}
                          onChange={(e) => setVitals({...vitals, oxygenSaturation: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'مستوى الألم (1-10)' : 'Pain Level (1-10)'}
                        </label>
                        <select
                          value={vitals.painLevel}
                          onChange={(e) => setVitals({...vitals, painLevel: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        >
                          <option value="">اختر / Select</option>
                          {[1,2,3,4,5,6,7,8,9,10].map(level => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <button
                      onClick={recordVitalSigns}
                      disabled={isLoading}
                      className="w-full md:w-auto px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      {currentLanguage === 'ar' ? 'تسجيل العلامات الحيوية' : 'Record Vital Signs'}
                    </button>
                  </div>
                )}

                {/* Nursing Notes Tab */}
                {activeTab === 'nursing-notes' && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">
                      {currentLanguage === 'ar' ? 'إنشاء ملاحظة تمريضية' : 'Create Nursing Note'}
                    </h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {currentLanguage === 'ar' ? 'الملاحظة التمريضية' : 'Nursing Note'}
                        </label>
                        <textarea
                          value={nursingNotes}
                          onChange={(e) => setNursingNotes(e.target.value)}
                          rows={6}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                          placeholder={currentLanguage === 'ar' 
                            ? 'سجل ملاحظاتك حول حالة المريض والرعاية المقدمة...' 
                            : 'Record your observations about patient condition and care provided...'}
                        />
                      </div>

                      <div className="flex items-center space-x-4">
                        <button
                          onClick={createNursingNote}
                          disabled={!nursingNotes.trim() || isLoading}
                          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                        >
                          {currentLanguage === 'ar' ? 'حفظ الملاحظة' : 'Save Note'}
                        </button>
                        
                        <button
                          onClick={() => setNursingNotes('')}
                          className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                        >
                          {currentLanguage === 'ar' ? 'مسح' : 'Clear'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Patient Care Tab */}
                {activeTab === 'patient-care' && (
                  <div className="space-y-6">
                    {/* Current Status */}
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        {currentLanguage === 'ar' ? 'الحالة الحالية' : 'Current Status'}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">98%</div>
                          <div className="text-gray-600 text-sm">
                            {currentLanguage === 'ar' ? 'تشبع الأكسجين' : 'O2 Saturation'}
                          </div>
                        </div>
                        
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">120/80</div>
                          <div className="text-gray-600 text-sm">
                            {currentLanguage === 'ar' ? 'ضغط الدم' : 'Blood Pressure'}
                          </div>
                        </div>
                        
                        <div className="text-center p-4 bg-yellow-50 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-600">2/10</div>
                          <div className="text-gray-600 text-sm">
                            {currentLanguage === 'ar' ? 'مستوى الألم' : 'Pain Level'}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">
                        {currentLanguage === 'ar' ? 'إجراءات سريعة' : 'Quick Actions'}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <button
                          onClick={() => setActiveTab('vital-signs')}
                          className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors"
                        >
                          <div className="text-2xl mb-2">💓</div>
                          <div className="font-medium text-gray-800">
                            {currentLanguage === 'ar' ? 'تسجيل العلامات الحيوية' : 'Record Vitals'}
                          </div>
                        </button>
                        
                        <button
                          onClick={() => setActiveTab('medications')}
                          className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors"
                        >
                          <div className="text-2xl mb-2">💊</div>
                          <div className="font-medium text-gray-800">
                            {currentLanguage === 'ar' ? 'إدارة الأدوية' : 'Manage Medications'}
                          </div>
                        </button>
                        
                        <button
                          onClick={() => setActiveTab('nursing-notes')}
                          className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors"
                        >
                          <div className="text-2xl mb-2">📝</div>
                          <div className="font-medium text-gray-800">
                            {currentLanguage === 'ar' ? 'كتابة ملاحظة' : 'Write Note'}
                          </div>
                        </button>
                        
                        <button
                          onClick={() => setActiveTab('care-plans')}
                          className="p-4 bg-orange-50 hover:bg-orange-100 rounded-lg text-center transition-colors"
                        >
                          <div className="text-2xl mb-2">📋</div>
                          <div className="font-medium text-gray-800">
                            {currentLanguage === 'ar' ? 'خطة الرعاية' : 'Care Plan'}
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NursePortal;