import { createContext, useContext, useEffect, useState } from 'react';

const LanguageContext = createContext();

// Export the context for external use
export { LanguageContext };

// Enhanced translation data with healthcare terminology
const translations = {
  ar: {
    // Navigation
    dashboard: 'لوحة التحكم',
    healthcare: 'الرعاية الصحية',
    nphies: 'نفيس',
    rcm: 'إدارة دورة الإيرادات',
    aiAnalytics: 'تحليلات الذكاء الاصطناعي',
    oidTree: 'شجرة المعرفات',
    register: 'تسجيل',
    assistant: 'المساعد',
    
    // Portal specific
    doctorPortal: 'بوابة الطبيب',
    patientPortal: 'بوابة المريض',
    nursePortal: 'بوابة الممرض',
    adminPortal: 'بوابة المدير',
    
    // Overview and navigation
    overview: 'نظرة عامة',
    patients: 'المرضى',
    appointments: 'المواعيد',
    patientDetails: 'تفاصيل المريض',
    aiAssistant: 'المساعد الذكي',
    myAppointments: 'مواعيدي',
    medicalHistory: 'التاريخ الطبي',
    requestAppointment: 'طلب موعد',
    
    // Medical terminology
    medicalPlatform: 'منصة برين سايت الطبية',
    fhirCompliant: 'متوافق مع معايير FHIR R4',
    digitalPatientServices: 'خدمات المرضى الرقمية',
    yourCareMatters: 'رعايتك تهمنا',
    
    // Patient portal specific
    upcomingAppointments: 'المواعيد القادمة',
    activePrescriptions: 'الأدوية الحالية',
    visitsThisYear: 'الزيارات هذا العام',
    noAppointments: 'لا توجد مواعيد مجدولة',
    appointmentRequested: 'تم إرسال طلب الموعد بنجاح',
    
    // Doctor portal specific
    newPatients: 'المرضى الجدد',
    todaysStats: 'إحصائيات اليوم',
    todaysAppointments: 'مواعيد اليوم',
    quickActions: 'إجراءات سريعة',
    searchPatient: 'البحث عن مريض',
    
    // System status
    refresh: 'تحديث',
    systemOnline: 'النظام نشط',
    nphiesConnected: 'نفيس متصل',
    
    // Common actions (enhanced)
    save: 'حفظ',
    cancel: 'إلغاء',
    delete: 'حذف',
    edit: 'تعديل',
    view: 'عرض',
    search: 'بحث',
    filter: 'تصفية',
    export: 'تصدير',
    import: 'استيراد',
    loading: 'جاري التحميل...',
    error: 'خطأ',
    success: 'نجح',
    warning: 'تحذير',
    info: 'معلومات',
    close: 'إغلاق',
    submit: 'إرسال',
    clear: 'مسح',
    select: 'اختيار',
    confirm: 'تأكيد',
    retry: 'إعادة المحاولة',
    
    // Dashboard
    welcomeMessage: 'مرحباً بك في منصة برينسايت للرعاية الصحية الموحدة',
    totalIdentities: 'إجمالي الهويات',
    activeProviders: 'مقدمي الخدمة النشطين',
    nphiesClaims: 'مطالبات نفيس',
    aiAnalyses: 'تحليلات الذكاء الاصطناعي',
    
    // Healthcare
    patientManagement: 'إدارة المرضى',
    providerManagement: 'إدارة مقدمي الخدمة',
    organizationManagement: 'إدارة المؤسسات',
    identityRegistration: 'تسجيل الهوية',
    
    // NPHIES
    claimsSubmission: 'تقديم المطالبات',
    claimsTracking: 'تتبع المطالبات',
    eligibilityVerification: 'التحقق من الأهلية',
    preAuthorization: 'الترخيص المسبق',
    
    // RCM
    revenueAnalytics: 'تحليلات الإيرادات',
    denialManagement: 'إدارة الرفض',
    collectionMetrics: 'مقاييس التحصيل',
    duplicateDetection: 'كشف التكرار',
    
    // Forms
    name: 'الاسم',
    nameAr: 'الاسم بالعربية',
    role: 'الدور',
    accessLevel: 'مستوى الوصول',
    organization: 'المؤسسة',
    department: 'القسم',
    nationalId: 'رقم الهوية الوطنية',
    nphiesId: 'معرف نفيس',
    expirationDate: 'تاريخ الانتهاء',
    
    // Roles
    patient: 'مريض',
    physician: 'طبيب',
    nurse: 'ممرض/ممرضة',
    pharmacist: 'صيدلي',
    technician: 'فني',
    administrator: 'مدير',
    researcher: 'باحث',
    aiAnalyst: 'محلل ذكاء اصطناعي',
    
    // Access Levels
    low: 'منخفض',
    medium: 'متوسط',
    high: 'عالي',
    critical: 'حرج',
    
    // Entity Types
    provider: 'مقدم خدمة',
    device: 'جهاز',
    procedure: 'إجراء',
    medication: 'دواء',
    record: 'سجل',
    insurance: 'تأمين',
    appointment: 'موعد',
    aiService: 'خدمة ذكاء اصطناعي',
    
    // Compliance
    pdplCompliant: 'متوافق مع قانون حماية البيانات الشخصية',
    hipaaReady: 'جاهز لمعيار هيبا',
    nphiesIntegrated: 'متكامل مع نفيس',
    fhirR4Support: 'يدعم FHIR R4',
    
    // Analytics
    totalClaims: 'إجمالي المطالبات',
    approvedClaims: 'المطالبات المعتمدة',
    deniedClaims: 'المطالبات المرفوضة',
    pendingClaims: 'المطالبات المعلقة',
    collectionRate: 'معدل التحصيل',
    denialRate: 'معدل الرفض',
    avgCollectionDays: 'متوسط أيام التحصيل',
    costSavings: 'وفورات التكلفة',
  },
  en: {
    // Navigation
    dashboard: 'Dashboard',
    healthcare: 'Healthcare',
    nphies: 'NPHIES',
    rcm: 'Revenue Cycle Management',
    aiAnalytics: 'AI Analytics',
    oidTree: 'OID Tree',
    register: 'Register',
    assistant: 'Assistant',
    
    // Portal specific
    doctorPortal: 'Doctor Portal',
    patientPortal: 'Patient Portal',
    nursePortal: 'Nurse Portal',
    adminPortal: 'Admin Portal',
    
    // Overview and navigation
    overview: 'Overview',
    patients: 'Patients',
    appointments: 'Appointments',
    patientDetails: 'Patient Details',
    aiAssistant: 'AI Assistant',
    myAppointments: 'My Appointments',
    medicalHistory: 'Medical History',
    requestAppointment: 'Request Appointment',
    
    // Medical terminology
    medicalPlatform: 'BrainSAIT Medical Platform',
    fhirCompliant: 'FHIR R4 Compliant',
    digitalPatientServices: 'Digital Patient Services',
    yourCareMatters: 'Your Care Matters',
    
    // Patient portal specific
    upcomingAppointments: 'Upcoming Appointments',
    activePrescriptions: 'Active Prescriptions',
    visitsThisYear: 'Visits This Year',
    noAppointments: 'No appointments scheduled',
    appointmentRequested: 'Appointment request submitted successfully',
    
    // Doctor portal specific
    newPatients: 'New Patients',
    todaysStats: "Today's Stats",
    todaysAppointments: "Today's Appointments",
    quickActions: 'Quick Actions',
    searchPatient: 'Search Patient',
    
    // System status
    refresh: 'Refresh',
    systemOnline: 'System Online',
    nphiesConnected: 'NPHIES Connected',
    
    // Common actions (enhanced)
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    view: 'View',
    search: 'Search',
    filter: 'Filter',
    export: 'Export',
    import: 'Import',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    warning: 'Warning',
    info: 'Information',
    close: 'Close',
    submit: 'Submit',
    clear: 'Clear',
    select: 'Select',
    confirm: 'Confirm',
    retry: 'Retry',
    
    // Dashboard
    welcomeMessage: 'Welcome to BrainSAIT Healthcare Unification Platform',
    totalIdentities: 'Total Identities',
    activeProviders: 'Active Providers',
    nphiesClaims: 'NPHIES Claims',
    aiAnalyses: 'AI Analyses',
    
    // Healthcare
    patientManagement: 'Patient Management',
    providerManagement: 'Provider Management',
    organizationManagement: 'Organization Management',
    identityRegistration: 'Identity Registration',
    
    // NPHIES
    claimsSubmission: 'Claims Submission',
    claimsTracking: 'Claims Tracking',
    eligibilityVerification: 'Eligibility Verification',
    preAuthorization: 'Pre-Authorization',
    
    // RCM
    revenueAnalytics: 'Revenue Analytics',
    denialManagement: 'Denial Management',
    collectionMetrics: 'Collection Metrics',
    duplicateDetection: 'Duplicate Detection',
    
    // Forms
    name: 'Name',
    nameAr: 'Arabic Name',
    role: 'Role',
    accessLevel: 'Access Level',
    organization: 'Organization',
    department: 'Department',
    nationalId: 'National ID',
    nphiesId: 'NPHIES ID',
    expirationDate: 'Expiration Date',
    
    // Roles
    patient: 'Patient',
    physician: 'Physician',
    nurse: 'Nurse',
    pharmacist: 'Pharmacist',
    technician: 'Technician',
    administrator: 'Administrator',
    researcher: 'Researcher',
    aiAnalyst: 'AI Analyst',
    
    // Access Levels
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',
    
    // Entity Types
    provider: 'Provider',
    device: 'Device',
    procedure: 'Procedure',
    medication: 'Medication',
    record: 'Record',
    insurance: 'Insurance',
    appointment: 'Appointment',
    aiService: 'AI Service',
    
    // Compliance
    pdplCompliant: 'PDPL Compliant',
    hipaaReady: 'HIPAA Ready',
    nphiesIntegrated: 'NPHIES Integrated',
    fhirR4Support: 'FHIR R4 Support',
    
    // Analytics
    totalClaims: 'Total Claims',
    approvedClaims: 'Approved Claims',
    deniedClaims: 'Denied Claims',
    pendingClaims: 'Pending Claims',
    collectionRate: 'Collection Rate',
    denialRate: 'Denial Rate',
    avgCollectionDays: 'Avg Collection Days',
    costSavings: 'Cost Savings',
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    const savedLanguage = localStorage.getItem('brainsait-language');
    return savedLanguage === 'en' || savedLanguage === 'ar' ? savedLanguage : 'ar'; // Default to Arabic
  });

  const _isRTL = language === 'ar';

  // Enhanced translation function with fallback and namespace support
  const _t = (key, options = {}) => {
    const { defaultValue, namespace } = options;
    
    // Support namespace.key format
    const fullKey = namespace ? `${namespace}.${key}` : key;
    
    // Try to get translation
    const translation = translations[language]?.[fullKey] || translations[language]?.[key];
    
    // Return translation, defaultValue, or key as last resort
    return translation || defaultValue || key;
  };
  
  // Pluralization support (basic)
  const tp = (key, count = 1, options = {}) => {
    const singular = t(key, options);
    const plural = t(`${key}_plural`, { ...options, defaultValue: singular });
    return count === 1 ? singular : plural;
  };

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage);
    localStorage.setItem('brainsait-language', newLanguage);
    
    // Update document direction
    document.documentElement.dir = newLanguage === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLanguage;
  };

  const toggleLanguage = () => {
    const newLanguage = language === 'ar' ? 'en' : 'ar';
    changeLanguage(newLanguage);
  };

  useEffect(() => {
    // Set initial document direction and language
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language, isRTL]);

  // Direction utilities
  const dir = isRTL ? 'rtl' : 'ltr';
  const textAlign = isRTL ? 'text-right' : 'text-left';
  const marginStart = isRTL ? 'ml' : 'mr';
  const marginEnd = isRTL ? 'mr' : 'ml';
  const paddingStart = isRTL ? 'pl' : 'pr';
  const paddingEnd = isRTL ? 'pr' : 'pl';
  const roundedStart = isRTL ? 'rounded-r' : 'rounded-l';
  const roundedEnd = isRTL ? 'rounded-l' : 'rounded-r';
  
  // Format utilities for healthcare data
  const formatDate = (date, options = {}) => {
    if (!date) return '';
    const dateObj = new Date(date);
    return dateObj.toLocaleDateString(language === 'ar' ? 'ar-SA' : 'en-US', options);
  };
  
  const formatTime = (time, options = {}) => {
    if (!time) return '';
    const timeObj = new Date(time);
    return timeObj.toLocaleTimeString(language === 'ar' ? 'ar-SA' : 'en-US', options);
  };
  
  const formatNumber = (number, options = {}) => {
    if (number === null || number === undefined) return '';
    return number.toLocaleString(language === 'ar' ? 'ar-SA' : 'en-US', options);
  };

  const value = {
    language,
    isRTL,
    dir,
    t,
    tp,
    changeLanguage,
    toggleLanguage,
    translations: translations[language],
    
    // CSS utilities
    textAlign,
    marginStart,
    marginEnd,
    paddingStart,
    paddingEnd,
    roundedStart,
    roundedEnd,
    
    // Format utilities
    formatDate,
    formatTime,
    formatNumber,
    
    // Healthcare specific utilities
    getPatientName: (patient) => {
      if (!patient) return '';
      return isRTL ? (patient.nameAr || patient.name) : (patient.name || patient.nameAr);
    },
    
    getDoctorName: (doctor) => {
      if (!doctor) return '';
      const prefix = isRTL ? 'د. ' : 'Dr. ';
      const name = isRTL ? (doctor.nameAr || doctor.name) : (doctor.name || doctor.nameAr);
      return prefix + name;
    }
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
