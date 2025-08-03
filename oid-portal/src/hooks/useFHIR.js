import { useState, useCallback, useEffect } from 'react';
import { useUnifiedHealthcare } from '../contexts/UnifiedHealthcareContext';

/**
 * Unified FHIR Integration Hook
 * Integrates FHIR R4 healthcare data with React components
 * Enhanced with Ultrathink Method for optimal performance
 */
export const useFHIR = () => {
  const { getCurrentUserRole, trackHealthcareActivity } = useUnifiedHealthcare();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fhirData, setFhirData] = useState({});

  // FHIR Service Configuration
  const FHIR_CONFIG = {
    baseUrl: process.env.VITE_FHIR_BASE_URL || 'https://api.brainsait.com/fhir',
    apiKey: localStorage.getItem('brainsait_api_key'),
    version: 'R4'
  };

  /**
   * Get authentication headers based on user role
   */
  const getAuthHeaders = useCallback(async () => {
    const userRole = await getCurrentUserRole();
    const apiKey = FHIR_CONFIG.apiKey;
    
    return {
      'Content-Type': 'application/fhir+json',
      'Accept': 'application/fhir+json',
      'Authorization': `Bearer ${apiKey}`,
      'X-User-Role': userRole,
      'X-FHIR-Version': FHIR_CONFIG.version
    };
  }, [getCurrentUserRole]);

  /**
   * Generic FHIR resource fetcher
   */
  const fetchFHIRResource = useCallback(async (resourceType, resourceId = null, params = {}) => {
    setIsLoading(true);
    setError(null);

    try {
      const headers = await getAuthHeaders();
      let url = `${FHIR_CONFIG.baseUrl}/${resourceType}`;
      
      if (resourceId) {
        url += `/${resourceId}`;
      }

      // Add query parameters
      const queryParams = new URLSearchParams(params);
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers
      });

      if (!response.ok) {
        throw new Error(`FHIR Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      
      // Track healthcare activity
      await trackHealthcareActivity('fhir_resource_access', {
        resourceType,
        resourceId,
        timestamp: new Date().toISOString()
      });

      // Cache the data
      setFhirData(prev => ({
        ...prev,
        [`${resourceType}_${resourceId || 'bundle'}`]: data
      }));

      return data;
    } catch (err) {
      console.error('FHIR fetch error:', err);
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [getAuthHeaders, trackHealthcareActivity]);

  /**
   * Create FHIR resource
   */
  const createFHIRResource = useCallback(async (resourceType, resourceData) => {
    setIsLoading(true);
    setError(null);

    try {
      const headers = await getAuthHeaders();
      const url = `${FHIR_CONFIG.baseUrl}/${resourceType}`;

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(resourceData)
      });

      if (!response.ok) {
        throw new Error(`FHIR Create Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      
      // Track creation activity
      await trackHealthcareActivity('fhir_resource_create', {
        resourceType,
        resourceId: data.id,
        timestamp: new Date().toISOString()
      });

      return data;
    } catch (err) {
      console.error('FHIR create error:', err);
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [getAuthHeaders, trackHealthcareActivity]);

  /**
   * Update FHIR resource
   */
  const updateFHIRResource = useCallback(async (resourceType, resourceId, resourceData) => {
    setIsLoading(true);
    setError(null);

    try {
      const headers = await getAuthHeaders();
      const url = `${FHIR_CONFIG.baseUrl}/${resourceType}/${resourceId}`;

      const response = await fetch(url, {
        method: 'PUT',
        headers,
        body: JSON.stringify(resourceData)
      });

      if (!response.ok) {
        throw new Error(`FHIR Update Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      
      // Update cache
      setFhirData(prev => ({
        ...prev,
        [`${resourceType}_${resourceId}`]: data
      }));

      // Track update activity
      await trackHealthcareActivity('fhir_resource_update', {
        resourceType,
        resourceId,
        timestamp: new Date().toISOString()
      });

      return data;
    } catch (err) {
      console.error('FHIR update error:', err);
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [getAuthHeaders, trackHealthcareActivity]);

  // Specialized FHIR operations for healthcare workflows

  /**
   * Get Patient by ID with localization
   */
  const getPatient = useCallback(async (patientId) => {
    const patient = await fetchFHIRResource('Patient', patientId);
    if (patient) {
      // Add Arabic name support and localization
      return {
        ...patient,
        displayName: patient.name?.[0]?.family || 'Unknown Patient',
        displayNameAr: patient.name?.find(n => n.use === 'official')?.family || null,
        localizedAddress: patient.address?.[0] || null
      };
    }
    return null;
  }, [fetchFHIRResource]);

  /**
   * Create SOAP Note (Doctor workflow)
   */
  const createSOAPNote = useCallback(async (patientId, soapData, voiceTranscript = null) => {
    const observation = {
      resourceType: "Observation",
      status: "final",
      category: [{
        coding: [{
          system: "http://terminology.hl7.org/CodeSystem/observation-category",
          code: "survey",
          display: "SOAP Note"
        }]
      }],
      subject: {
        reference: `Patient/${patientId}`
      },
      effectiveDateTime: new Date().toISOString(),
      component: [
        {
          code: { coding: [{ system: "http://brainsait.com/codes", code: "SOAP-S" }] },
          valueString: soapData.subjective
        },
        {
          code: { coding: [{ system: "http://brainsait.com/codes", code: "SOAP-O" }] },
          valueString: soapData.objective
        },
        {
          code: { coding: [{ system: "http://brainsait.com/codes", code: "SOAP-A" }] },
          valueString: soapData.assessment
        },
        {
          code: { coding: [{ system: "http://brainsait.com/codes", code: "SOAP-P" }] },
          valueString: soapData.plan
        }
      ]
    };

    if (voiceTranscript) {
      observation.component.push({
        code: { coding: [{ system: "http://brainsait.com/codes", code: "VOICE-TRANSCRIPT" }] },
        valueString: voiceTranscript
      });
    }

    return await createFHIRResource('Observation', observation);
  }, [createFHIRResource]);

  /**
   * Get patient appointments (Nurse workflow)
   */
  const getPatientAppointments = useCallback(async (patientId, dateRange = {}) => {
    const params = {
      patient: patientId,
      status: 'booked,arrived,fulfilled'
    };

    if (dateRange.start) {
      params.date = `ge${dateRange.start}`;
    }
    if (dateRange.end) {
      params.date = `${params.date || ''}le${dateRange.end}`;
    }

    return await fetchFHIRResource('Appointment', null, params);
  }, [fetchFHIRResource]);

  /**
   * Search patients (General workflow)
   */
  const searchPatients = useCallback(async (searchQuery, limit = 10) => {
    const params = {
      name: searchQuery,
      _count: limit,
      _sort: 'family'
    };

    return await fetchFHIRResource('Patient', null, params);
  }, [fetchFHIRResource]);

  /**
   * Get healthcare provider information
   */
  const getHealthcareProvider = useCallback(async (providerId) => {
    return await fetchFHIRResource('Practitioner', providerId);
  }, [fetchFHIRResource]);

  /**
   * Create healthcare encounter
   */
  const createEncounter = useCallback(async (patientId, encounterData) => {
    const encounter = {
      resourceType: "Encounter",
      status: encounterData.status || "in-progress",
      class: {
        system: "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        code: encounterData.class || "AMB",
        display: encounterData.classDisplay || "Ambulatory"
      },
      subject: {
        reference: `Patient/${patientId}`
      },
      period: {
        start: encounterData.startTime || new Date().toISOString()
      },
      reasonCode: encounterData.reasonCode || [],
      ...encounterData
    };

    return await createFHIRResource('Encounter', encounter);
  }, [createFHIRResource]);

  return {
    // State
    isLoading,
    error,
    fhirData,

    // Generic FHIR operations
    fetchFHIRResource,
    createFHIRResource,
    updateFHIRResource,

    // Specialized healthcare operations
    getPatient,
    createSOAPNote,
    getPatientAppointments,
    searchPatients,
    getHealthcareProvider,
    createEncounter,

    // Utility functions
    clearError: () => setError(null),
    clearCache: () => setFhirData({})
  };
};

export default useFHIR;