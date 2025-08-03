import { useState, useCallback, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Unified Authentication and Role-Based Access Control Hook
 * Integrates Doctor, Nurse, and Patient portals with React routing
 * Enhanced with Ultrathink Method for security and performance
 */

// Healthcare roles enum
export const HEALTHCARE_ROLES = {
  DOCTOR: 'doctor',
  NURSE: 'nurse',
  PATIENT: 'patient',
  ADMIN: 'admin',
  PHARMACIST: 'pharmacist',
  TECHNICIAN: 'technician',
  RESEARCHER: 'researcher'
};

// Enhanced Role permissions mapping with resource-level access
const ROLE_PERMISSIONS = {
  [HEALTHCARE_ROLES.DOCTOR]: [
    'read_patient_full',
    'write_patient_full',
    'create_prescription',
    'create_soap_note',
    'access_lab_results',
    'schedule_appointment',
    'access_imaging',
    'manage_care_team',
    'emergency_override',
    'access_patient_history',
    'create_discharge_summary'
  ],
  [HEALTHCARE_ROLES.NURSE]: [
    'read_patient_basic',
    'write_patient_vitals',
    'view_appointments',
    'update_patient_status',
    'access_medication_list',
    'create_nursing_note',
    'administer_medication',
    'update_care_plan',
    'access_shift_reports'
  ],
  [HEALTHCARE_ROLES.PATIENT]: [
    'read_own_data',
    'update_own_profile',
    'view_own_appointments',
    'access_own_results',
    'request_appointment',
    'family_access_delegate',
    'access_health_records',
    'request_prescription_refill',
    'access_billing_info'
  ],
  [HEALTHCARE_ROLES.ADMIN]: [
    'full_system_access',
    'manage_users',
    'system_configuration',
    'audit_logs',
    'financial_reports',
    'compliance_monitoring',
    'backup_restore',
    'integration_management'
  ],
  [HEALTHCARE_ROLES.PHARMACIST]: [
    'read_prescriptions',
    'update_medication_status',
    'access_drug_interactions',
    'create_pharmacy_note',
    'dispense_medication',
    'medication_counseling',
    'inventory_management',
    'pharmaceutical_care'
  ],
  [HEALTHCARE_ROLES.TECHNICIAN]: [
    'read_patient_basic',
    'update_test_results',
    'access_imaging_equipment',
    'create_technical_note',
    'equipment_maintenance',
    'quality_control',
    'sample_processing'
  ],
  [HEALTHCARE_ROLES.RESEARCHER]: [
    'read_anonymized_data',
    'export_research_data',
    'create_research_query',
    'statistical_analysis',
    'protocol_access',
    'irb_submission',
    'data_visualization'
  ]
};

// Time-based access control for healthcare shifts
const SHIFT_PERMISSIONS = {
  'day_shift': {
    hours: [6, 18], // 6 AM to 6 PM
    permissions: ['all_standard_permissions']
  },
  'night_shift': {
    hours: [18, 6], // 6 PM to 6 AM
    permissions: ['emergency_access', 'critical_care_access']
  },
  'emergency': {
    hours: [0, 24], // 24/7
    permissions: ['emergency_override', 'critical_override']
  }
};

// Multi-tenant organization access levels
const ORGANIZATION_ACCESS_LEVELS = {
  'hospital_network': {
    scope: 'network',
    permissions: ['cross_facility_access', 'network_reports']
  },
  'single_facility': {
    scope: 'facility', 
    permissions: ['facility_specific_access']
  },
  'department': {
    scope: 'department',
    permissions: ['department_specific_access']
  },
  'unit': {
    scope: 'unit',
    permissions: ['unit_specific_access']
  }
};

// Default route mapping for each role
const ROLE_DEFAULT_ROUTES = {
  [HEALTHCARE_ROLES.DOCTOR]: '/doctor-portal',
  [HEALTHCARE_ROLES.NURSE]: '/nurse-portal', 
  [HEALTHCARE_ROLES.PATIENT]: '/patient-portal',
  [HEALTHCARE_ROLES.ADMIN]: '/admin-dashboard',
  [HEALTHCARE_ROLES.PHARMACIST]: '/pharmacy-portal',
  [HEALTHCARE_ROLES.TECHNICIAN]: '/tech-portal',
  [HEALTHCARE_ROLES.RESEARCHER]: '/research-portal'
};

export const useAuth = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Initialize authentication state from storage
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = localStorage.getItem('brainsait_user');
        const storedToken = localStorage.getItem('brainsait_token');
        
        if (storedUser && storedToken) {
          const userData = JSON.parse(storedUser);
          
          // Verify token is still valid
          const isValid = await verifyToken(storedToken);
          if (isValid) {
            setUser(userData);
            setIsAuthenticated(true);
          } else {
            // Token expired, clear storage
            logout();
          }
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Verify JWT token validity
   */
  const verifyToken = useCallback(async (token) => {
    try {
      const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.ok;
    } catch (error) {
      console.error('Token verification failed:', error);
      return false;
    }
  }, []);

  /**
   * Login with credentials
   */
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const { user: userData, token, expiresIn } = await response.json();

      // Store auth data
      localStorage.setItem('brainsait_user', JSON.stringify(userData));
      localStorage.setItem('brainsait_token', token);
      localStorage.setItem('brainsait_token_expires', (Date.now() + expiresIn * 1000).toString());

      setUser(userData);
      setIsAuthenticated(true);

      // Log successful login
      await logSecurityEvent('user_login', {
        userId: userData.id,
        role: userData.role,
        organizationId: userData.organizationId,
        loginMethod: 'credentials'
      });

      // Navigate to role-appropriate route
      const defaultRoute = ROLE_DEFAULT_ROUTES[userData.role] || '/dashboard';
      navigate(defaultRoute);

      return { success: true, user: userData };
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      // Log logout event before clearing user data
      if (user) {
        await logSecurityEvent('user_logout', {
          userId: user.id,
          role: user.role,
          organizationId: user.organizationId,
          logoutType: 'manual'
        });
      }

      // Call logout endpoint to invalidate server session
      const token = localStorage.getItem('brainsait_token');
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      localStorage.removeItem('brainsait_user');
      localStorage.removeItem('brainsait_token');
      localStorage.removeItem('brainsait_token_expires');
      localStorage.removeItem('brainsait_api_key');
      localStorage.removeItem('brainsait_session_id');

      setUser(null);
      setIsAuthenticated(false);
      setError(null);

      navigate('/login');
    }
  }, [navigate, user, logSecurityEvent]);

  /**
   * Enhanced permission check with time-based and organizational constraints
   */
  const hasPermission = useCallback((permission, options = {}) => {
    if (!user || !user.role) return false;
    
    const rolePermissions = ROLE_PERMISSIONS[user.role] || [];
    const hasBasicPermission = rolePermissions.includes(permission) || rolePermissions.includes('full_system_access');
    
    if (!hasBasicPermission) return false;
    
    // Check time-based constraints (shift permissions)
    if (options.requireShiftAccess) {
      const currentHour = new Date().getHours();
      const userShift = user.shift || 'day_shift';
      const shiftConfig = SHIFT_PERMISSIONS[userShift];
      
      if (shiftConfig) {
        const [startHour, endHour] = shiftConfig.hours;
        const isWithinShift = startHour <= endHour 
          ? (currentHour >= startHour && currentHour < endHour)
          : (currentHour >= startHour || currentHour < endHour);
          
        if (!isWithinShift && !shiftConfig.permissions.includes('emergency_override')) {
          return false;
        }
      }
    }
    
    // Check organizational constraints
    if (options.organizationId && user.organizationId !== options.organizationId) {
      const userOrgLevel = user.organizationLevel || 'single_facility';
      const orgConfig = ORGANIZATION_ACCESS_LEVELS[userOrgLevel];
      
      if (!orgConfig.permissions.includes('cross_facility_access')) {
        return false;
      }
    }
    
    // Check resource-level access (patient assignment, department access)
    if (options.resourceId && user.assignedResources) {
      if (!user.assignedResources.includes(options.resourceId)) {
        return false;
      }
    }
    
    return true;
  }, [user]);
  
  /**
   * Check shift-based access
   */
  const hasShiftAccess = useCallback((permission) => {
    if (!user || !user.shift) return hasPermission(permission);
    
    const currentHour = new Date().getHours();
    const shiftConfig = SHIFT_PERMISSIONS[user.shift];
    
    if (!shiftConfig) return hasPermission(permission);
    
    const [startHour, endHour] = shiftConfig.hours;
    const isWithinShift = startHour <= endHour 
      ? (currentHour >= startHour && currentHour < endHour)
      : (currentHour >= startHour || currentHour < endHour);
    
    if (isWithinShift || shiftConfig.permissions.includes('emergency_override')) {
      return hasPermission(permission);
    }
    
    return false;
  }, [user, hasPermission]);
  
  /**
   * Check organization-level access
   */
  const hasOrganizationAccess = useCallback((targetOrgId, permission) => {
    if (!user || !user.organizationId) return false;
    
    // Same organization access
    if (user.organizationId === targetOrgId) {
      return hasPermission(permission);
    }
    
    // Cross-organization access
    const userOrgLevel = user.organizationLevel || 'single_facility';
    const orgConfig = ORGANIZATION_ACCESS_LEVELS[userOrgLevel];
    
    if (orgConfig.permissions.includes('cross_facility_access')) {
      return hasPermission(permission);
    }
    
    return false;
  }, [user, hasPermission]);
  
  /**
   * Log security event for audit trail
   */
  const logSecurityEvent = useCallback(async (event, details = {}) => {
    try {
      const auditData = {
        userId: user?.id,
        userRole: user?.role,
        organizationId: user?.organizationId,
        event,
        details,
        timestamp: new Date().toISOString(),
        ipAddress: await getClientIpAddress(),
        userAgent: navigator.userAgent,
        sessionId: localStorage.getItem('brainsait_session_id')
      };
      
      await fetch('/api/audit/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('brainsait_token')}`
        },
        body: JSON.stringify(auditData)
      });
    } catch (error) {
      console.error('Failed to log security event:', error);
    }
  }, [user]);
  
  /**
   * Get client IP address for audit logging
   */
  const getClientIpAddress = useCallback(async () => {
    try {
      const response = await fetch('/api/system/client-ip');
      const data = await response.json();
      return data.ip;
    } catch (error) {
      return 'unknown';
    }
  }, []);

  /**
   * Check if user has any of the specified roles
   */
  const hasRole = useCallback((roles) => {
    if (!user || !user.role) return false;
    
    const rolesArray = Array.isArray(roles) ? roles : [roles];
    return rolesArray.includes(user.role);
  }, [user]);

  /**
   * Get user permissions array
   */
  const getUserPermissions = useCallback(() => {
    if (!user || !user.role) return [];
    return ROLE_PERMISSIONS[user.role] || [];
  }, [user]);

  /**
   * Register new user (admin only)
   */
  const register = useCallback(async (userData) => {
    if (!hasPermission('manage_users')) {
      throw new Error('Insufficient permissions to register users');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('brainsait_token')}`
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const newUser = await response.json();
      return { success: true, user: newUser };
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [hasPermission]);

  /**
   * Update user profile
   */
  const updateProfile = useCallback(async (profileData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('brainsait_token')}`
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Profile update failed');
      }

      const updatedUser = await response.json();
      
      // Update local storage and state
      localStorage.setItem('brainsait_user', JSON.stringify(updatedUser));
      setUser(updatedUser);

      return { success: true, user: updatedUser };
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Change password
   */
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('brainsait_token')}`
        },
        body: JSON.stringify({
          currentPassword,
          newPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Password change failed');
      }

      return { success: true };
    } catch (err) {
      console.error('Password change error:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get role-based navigation items
   */
  const getNavigationItems = useCallback(() => {
    if (!user || !user.role) return [];

    const baseItems = [
      { path: '/dashboard', label: 'Dashboard', icon: '🏠' },
      { path: '/oid-tree', label: 'OID Tree', icon: '🌳' }
    ];

    const roleSpecificItems = {
      [HEALTHCARE_ROLES.DOCTOR]: [
        { path: '/doctor-portal', label: 'Doctor Portal', icon: '👨‍⚕️' },
        { path: '/patients', label: 'Patients', icon: '👥' },
        { path: '/appointments', label: 'Appointments', icon: '📅' },
        { path: '/prescriptions', label: 'Prescriptions', icon: '💊' }
      ],
      [HEALTHCARE_ROLES.NURSE]: [
        { path: '/nurse-portal', label: 'Nurse Portal', icon: '👩‍⚕️' },
        { path: '/patient-care', label: 'Patient Care', icon: '🏥' },
        { path: '/schedules', label: 'Schedules', icon: '📋' }
      ],
      [HEALTHCARE_ROLES.PATIENT]: [
        { path: '/patient-portal', label: 'Patient Portal', icon: '🏥' },
        { path: '/my-appointments', label: 'My Appointments', icon: '📅' },
        { path: '/my-results', label: 'My Results', icon: '📊' },
        { path: '/my-prescriptions', label: 'My Prescriptions', icon: '💊' }
      ],
      [HEALTHCARE_ROLES.ADMIN]: [
        { path: '/admin-dashboard', label: 'Admin Dashboard', icon: '⚙️' },
        { path: '/user-management', label: 'User Management', icon: '👥' },
        { path: '/system-config', label: 'System Config', icon: '🔧' },
        { path: '/audit-logs', label: 'Audit Logs', icon: '📝' }
      ]
    };

    return [...baseItems, ...(roleSpecificItems[user.role] || [])];
  }, [user]);

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,

    // Authentication methods
    login,
    logout,
    register,
    updateProfile,
    changePassword,

    // Enhanced Authorization methods
    hasPermission,
    hasRole,
    hasShiftAccess,
    hasOrganizationAccess,
    getUserPermissions,

    // Security & Audit methods
    logSecurityEvent,

    // Utility methods
    getNavigationItems,
    clearError: () => setError(null),

    // Constants
    HEALTHCARE_ROLES,
    ROLE_PERMISSIONS,
    SHIFT_PERMISSIONS,
    ORGANIZATION_ACCESS_LEVELS
  };
};

export default useAuth;