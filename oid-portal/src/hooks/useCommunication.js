/**
 * Communication Hook for BrainSAIT Healthcare Platform
 * Provides communication capabilities integration with the OID Tree component
 * Supports SMS, Voice, Video, and Email communications with Arabic/English support
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useLanguage } from './useLanguage';
import { useOidTreeStore } from '../stores/oid-tree-store';

// Communication API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Communication status types
export const COMMUNICATION_STATUS = {
  IDLE: 'idle',
  CONNECTING: 'connecting',
  ACTIVE: 'active',
  ENDED: 'ended',
  FAILED: 'failed',
  SENDING: 'sending',
  DELIVERED: 'delivered',
  READ: 'read'
};

// Communication channels
export const COMMUNICATION_CHANNELS = {
  SMS: 'sms',
  VOICE: 'voice',
  VIDEO: 'video',
  EMAIL: 'email',
  WHATSAPP: 'whatsapp'
};

// Emergency levels
export const EMERGENCY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

/**
 * Main communication hook
 */
export const useCommunication = () => {
  const { currentLanguage } = useLanguage();
  const {
    communicationStatus,
    activeConnections,
    communicationPreferences,
    emergencyAlerts,
    isWebSocketConnected,
    updateCommunicationStatus,
    addActiveConnection,
    removeActiveConnection,
    updateCommunicationPreferences: updateStorePreferences,
    addEmergencyAlert,
    resolveEmergencyAlert,
    setWebSocketConnected
  } = useOidTreeStore();
  
  const [communicationHistory, setCommunicationHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const websocketRef = useRef(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/communication`;
        websocketRef.current = new WebSocket(wsUrl);

        websocketRef.current.onopen = () => {
          setWebSocketConnected(true);
          setError(null);
        };

        websocketRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };

        websocketRef.current.onclose = () => {
          setWebSocketConnected(false);
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        websocketRef.current.onerror = (error) => {
          setError('WebSocket connection error');
          setWebSocketConnected(false);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setError('Failed to establish real-time connection');
      }
    };

    connectWebSocket();

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'communication_status_update':
        updateCommunicationStatus(data.patient_id, data.channel, data.status);
        break;

      case 'active_connection_update':
        if (data.status === 'active') {
          addActiveConnection({
            id: data.connection_id,
            patientId: data.patient_id,
            channel: data.channel,
            startTime: new Date(data.timestamp),
            status: data.status,
            metadata: data.metadata
          });
        } else {
          removeActiveConnection(data.connection_id);
        }
        break;

      case 'emergency_alert':
        handleEmergencyAlert(data);
        break;

      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, [updateCommunicationStatus, addActiveConnection, removeActiveConnection]);

  // Handle emergency alerts
  const handleEmergencyAlert = useCallback((alertData) => {
    // Add to store
    addEmergencyAlert({
      id: alertData.event_id || `emergency_${Date.now()}`,
      patientId: alertData.patient_id,
      level: alertData.emergency_level || 'medium',
      type: alertData.emergency_type || 'medical',
      description: alertData.description,
      description_ar: alertData.description_ar,
      timestamp: new Date(alertData.timestamp),
      resolved: false
    });
    
    // Display emergency notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(
        currentLanguage === 'ar' ? 'تنبيه طوارئ طبية' : 'Medical Emergency Alert',
        {
          body: currentLanguage === 'ar' ? alertData.description_ar : alertData.description,
          icon: '/emergency-icon.png',
          requireInteraction: true
        }
      );
    }
  }, [currentLanguage, addEmergencyAlert]);

  // Send message function
  const sendMessage = useCallback(async (patientData, messageData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/communication/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
        },
        body: JSON.stringify({
          patient_id: patientData.patient_id,
          channel: messageData.channel,
          message: messageData.message,
          message_ar: messageData.message_ar,
          priority: messageData.priority || 'normal',
          language: currentLanguage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Update communication history
      setCommunicationHistory(prev => [...prev, {
        id: result.message_id,
        patientId: patientData.patient_id,
        channel: messageData.channel,
        message: messageData.message,
        timestamp: new Date(),
        status: COMMUNICATION_STATUS.DELIVERED,
        language: currentLanguage
      }]);

      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentLanguage]);

  // Initiate voice call
  const initiateVoiceCall = useCallback(async (patientData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/communication/voice-call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
        },
        body: JSON.stringify({
          patient_id: patientData.patient_id,
          phone_number: patientData.phone_number,
          language: currentLanguage,
          call_type: 'outbound'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Add to active connections
      addActiveConnection({
        id: result.call_id,
        patientId: patientData.patient_id,
        channel: COMMUNICATION_CHANNELS.VOICE,
        startTime: new Date(),
        status: COMMUNICATION_STATUS.CONNECTING
      });

      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentLanguage]);

  // Initiate video consultation
  const initiateVideoConsultation = useCallback(async (patientData, consultationData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/communication/video-consultation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
        },
        body: JSON.stringify({
          patient_id: patientData.patient_id,
          provider_id: consultationData.provider_id,
          consultation_type: consultationData.type,
          language: currentLanguage,
          duration_minutes: consultationData.duration || 30
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Add to active connections
      addActiveConnection({
        id: result.session_id,
        patientId: patientData.patient_id,
        channel: COMMUNICATION_CHANNELS.VIDEO,
        startTime: new Date(),
        status: COMMUNICATION_STATUS.CONNECTING,
        metadata: { meetingUrl: result.meeting_url }
      });

      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentLanguage]);

  // Get communication preferences
  const getCommunicationPreferences = useCallback(async (patientId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/communication/preferences/${patientId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      setError(error.message);
      throw error;
    }
  }, []);

  // Update communication preferences
  const updateCommunicationPreferences = useCallback(async (patientId, preferences) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/communication/preferences/${patientId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
          },
          body: JSON.stringify({
            ...preferences,
            language: currentLanguage
          })
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Update store
      updateStorePreferences(patientId, preferences);
      
      return result;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [currentLanguage, updateStorePreferences]);

  // Get communication history
  const getCommunicationHistory = useCallback(async (patientId, limit = 50) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/communication/history/${patientId}?limit=${limit}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const history = await response.json();
      setCommunicationHistory(history.communications || []);
      return history;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  }, []);

  // Trigger emergency communication
  const triggerEmergencyCommunication = useCallback(async (emergencyData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/communication/emergency-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
        },
        body: JSON.stringify({
          emergency_event: emergencyData.event,
          emergency_contacts: emergencyData.contacts,
          patient_data: emergencyData.patient_data,
          user_id: emergencyData.user_id
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // End active connection
  const endConnection = useCallback(async (connectionId) => {
    try {
      removeActiveConnection(connectionId);

      // Optionally call API to end connection on backend
      await fetch(`${API_BASE_URL}/api/v1/communication/end-connection/${connectionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('healthcare_token')}`
        }
      });
    } catch (error) {
      console.error('Failed to end connection:', error);
    }
  }, [removeActiveConnection]);

  return {
    // Connection state
    isConnected: isWebSocketConnected,
    activeConnections,
    connectionStatus: communicationStatus,
    communicationHistory,
    communicationPreferences,
    emergencyAlerts,
    isLoading,
    error,

    // Communication actions
    sendMessage,
    initiateVoiceCall,
    initiateVideoConsultation,
    triggerEmergencyCommunication,
    endConnection,

    // Preferences management
    getCommunicationPreferences,
    updateCommunicationPreferences,

    // History
    getCommunicationHistory,

    // Store actions
    resolveEmergencyAlert,
    
    // Constants
    COMMUNICATION_STATUS,
    COMMUNICATION_CHANNELS,
    EMERGENCY_LEVELS
  };
};

export default useCommunication;