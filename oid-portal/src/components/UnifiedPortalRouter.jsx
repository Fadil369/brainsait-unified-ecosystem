import { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, HEALTHCARE_ROLES } from '../hooks/useAuth';
import { useFHIR } from '../hooks/useFHIR';
import { useLanguage } from '../hooks/useLanguage';

// Portal Components
import DoctorPortal from './portals/DoctorPortal';
import NursePortal from './portals/NursePortal';
import PatientPortal from './portals/PatientPortal';
import AdminPortal from './portals/AdminPortal';
import LoadingSpinner from './shared/LoadingSpinner';
import ErrorBoundary from './shared/ErrorBoundary';

/**
 * Unified Portal Router Component
 * Replaces separate HTML portals with integrated React routing
 * Enhanced with Ultrathink Method for seamless role-based access
 */
const UnifiedPortalRouter = () => {
  const { user, isAuthenticated, hasRole, isLoading: authLoading } = useAuth();
  const { error: fhirError, clearError } = useFHIR();
  const { language: currentLanguage, isRTL, t } = useLanguage();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!authLoading) {
      setIsInitialized(true);
    }
  }, [authLoading]);

  // Show loading while initializing
  if (!isInitialized || authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <LoadingSpinner message={currentLanguage === 'ar' ? 'جاري التحميل...' : 'Loading...'} />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Error display component
  const ErrorDisplay = ({ error, onClear }) => (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-4 mb-4 ${isRTL ? 'text-right' : 'text-left'}`}>
      <div className="flex items-center justify-between">
        <div className="text-red-800">
          <h3 className="font-medium">
            {currentLanguage === 'ar' ? 'خطأ في النظام' : 'System Error'}
          </h3>
          <p className="text-sm mt-1">{error}</p>
        </div>
        <button
          onClick={onClear}
          className="text-red-600 hover:text-red-800 font-medium text-sm"
        >
          {currentLanguage === 'ar' ? 'إغلاق' : 'Dismiss'}
        </button>
      </div>
    </div>
  );

  // Protected Route Component
  const ProtectedRoute = ({ children, requiredRoles, fallback = null }) => {
    const hasRequiredRole = requiredRoles ? hasRole(requiredRoles) : true;
    
    if (!hasRequiredRole) {
      return fallback || (
        <div className="text-center py-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            {currentLanguage === 'ar' ? 'وصول غير مسموح' : 'Access Denied'}
          </h2>
          <p className="text-gray-600">
            {currentLanguage === 'ar' 
              ? 'ليس لديك صلاحية للوصول إلى هذه الصفحة' 
              : 'You do not have permission to access this page'}
          </p>
        </div>
      );
    }
    
    return children;
  };

  return (
    <ErrorBoundary>
      <div className={`min-h-screen bg-gray-50 ${isRTL ? 'rtl' : 'ltr'}`}>
        {/* Global Error Display */}
        {fhirError && (
          <div className="fixed top-4 left-4 right-4 z-50">
            <ErrorDisplay error={fhirError} onClear={clearError} />
          </div>
        )}

        {/* User Info Bar */}
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className={`flex items-center space-x-4 ${isRTL ? 'space-x-reverse' : ''}`}>
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <span className="text-indigo-600 font-semibold text-sm">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {user?.name || user?.email}
                </p>
                <p className="text-xs text-gray-500">
                  {currentLanguage === 'ar' ? 'الدور:' : 'Role:'} {user?.role}
                </p>
              </div>
            </div>
            <div className="text-xs text-gray-500">
              {currentLanguage === 'ar' ? 'منصة برين سايت الموحدة' : 'BrainSAIT Unified Platform'}
            </div>
          </div>
        </div>

        {/* Main Router Content */}
        <div className="container mx-auto px-4 py-6">
          <Routes>
            {/* Doctor Portal Routes */}
            <Route 
              path="/doctor-portal/*" 
              element={
                <ProtectedRoute requiredRoles={[HEALTHCARE_ROLES.DOCTOR]}>
                  <DoctorPortal />
                </ProtectedRoute>
              } 
            />

            {/* Nurse Portal Routes */}
            <Route 
              path="/nurse-portal/*" 
              element={
                <ProtectedRoute requiredRoles={[HEALTHCARE_ROLES.NURSE]}>
                  <NursePortal />
                </ProtectedRoute>
              } 
            />

            {/* Patient Portal Routes */}
            <Route 
              path="/patient-portal/*" 
              element={
                <ProtectedRoute requiredRoles={[HEALTHCARE_ROLES.PATIENT]}>
                  <PatientPortal />
                </ProtectedRoute>
              } 
            />

            {/* Admin Portal Routes */}
            <Route 
              path="/admin-dashboard/*" 
              element={
                <ProtectedRoute requiredRoles={[HEALTHCARE_ROLES.ADMIN]}>
                  <AdminPortal />
                </ProtectedRoute>
              } 
            />

            {/* Default redirect based on user role */}
            <Route 
              path="/" 
              element={
                <Navigate 
                  to={
                    user?.role === HEALTHCARE_ROLES.DOCTOR ? '/doctor-portal' :
                    user?.role === HEALTHCARE_ROLES.NURSE ? '/nurse-portal' :
                    user?.role === HEALTHCARE_ROLES.PATIENT ? '/patient-portal' :
                    user?.role === HEALTHCARE_ROLES.ADMIN ? '/admin-dashboard' :
                    '/dashboard'
                  } 
                  replace 
                />
              } 
            />

            {/* Enhanced Fallback route */}
            <Route 
              path="*" 
              element={
                <div className={`text-center py-12 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
                  <div className="max-w-md mx-auto">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl text-gray-400">📄</span>
                    </div>
                    <h1 className="text-2xl font-bold text-gray-800 mb-4">
                      {t('pageNotFound') || (isRTL ? 'الصفحة غير موجودة' : 'Page Not Found')}
                    </h1>
                    <p className="text-gray-600 mb-6">
                      {t('pageNotFoundMessage') || (isRTL 
                        ? 'الصفحة التي تبحث عنها غير موجودة في نظام برين سايت' 
                        : 'The healthcare page you are looking for does not exist in BrainSAIT system'
                      )}
                    </p>
                    <p className="text-sm text-gray-500 mb-6">
                      {t('redirectingToDashboard') || (isRTL ? 'جاري التوجيه إلى لوحة التحكم...' : 'Redirecting to dashboard...')}
                    </p>
                    <Navigate to="/" replace />
                  </div>
                </div>
              } 
            />
          </Routes>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default UnifiedPortalRouter;