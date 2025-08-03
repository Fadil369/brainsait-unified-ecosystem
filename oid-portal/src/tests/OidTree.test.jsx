/**
 * Frontend Tests for OidTree Communication Features
 * =================================================
 * 
 * Comprehensive test suite for OidTree communication integration including:
 * - Communication feature integration
 * - Arabic/English UI switching
 * - Real-time communication updates
 * - Communication action menus
 * - Error handling and loading states
 */

import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';

// Import components to test
import OidTree from '../pages/OidTree';

// Mock dependencies
vi.mock('../hooks/useLanguage', () => ({
  useLanguage: () => ({
    currentLanguage: 'en',
    isRTL: false,
    t: vi.fn((key) => key),
    switchLanguage: vi.fn()
  })
}));

vi.mock('../contexts/UnifiedHealthcareContext', () => ({
  useUnifiedHealthcare: () => ({
    getCurrentUserRole: vi.fn().mockResolvedValue('doctor'),
    trackHealthcareActivity: vi.fn().mockResolvedValue(true),
    checkHealthcarePermissions: vi.fn().mockReturnValue(true),
    sendPatientCommunication: vi.fn().mockResolvedValue({
      success: true,
      messageId: 'msg_123',
      deliveryStatus: 'sent'
    }),
    triggerWorkflow: vi.fn().mockResolvedValue({
      workflowId: 'wf_456',
      status: 'initiated'
    }),
    getPatientCommunicationHistory: vi.fn().mockResolvedValue([
      {
        id: 'comm_1',
        type: 'sms',
        content: 'Appointment reminder',
        timestamp: '2024-08-04T10:30:00Z',
        status: 'delivered'
      }
    ])
  })
}));

vi.mock('../hooks/useFHIR', () => ({
  useFHIR: () => ({
    isLoading: false,
    error: null,
    createFHIRResource: vi.fn(),
    getFHIRResource: vi.fn().mockResolvedValue({
      resourceType: 'Patient',
      id: 'patient_123',
      name: [{ given: ['Ahmed'], family: 'Mohammed' }]
    })
  })
}));

// Mock the communication service
const mockCommunicationService = {
  sendSMS: vi.fn().mockResolvedValue({
    messageId: 'sms_123',
    status: 'sent',
    deliveryTracking: true
  }),
  initiateVoiceCall: vi.fn().mockResolvedValue({
    callId: 'call_456',
    status: 'initiated',
    estimatedDuration: '60 seconds'
  }),
  triggerWorkflow: vi.fn().mockResolvedValue({
    workflowId: 'workflow_789',
    status: 'started',
    stepsScheduled: 4
  }),
  getCommunicationStatus: vi.fn().mockResolvedValue({
    messageId: 'msg_123',
    status: 'delivered',
    deliveredAt: '2024-08-04T10:35:00Z'
  }),
  sendEmergencyAlert: vi.fn().mockResolvedValue({
    alertId: 'alert_critical_123',
    broadcastSent: true,
    recipientsNotified: 15
  })
};

vi.mock('../services/api', () => ({
  communicationService: mockCommunicationService
}));

// Mock Zustand store with communication features
vi.mock('../stores/oid-tree-store', () => ({
  useOidTreeStore: vi.fn(() => ({
    treeData: {
      id: 'root',
      name: 'Healthcare OID Root',
      oid: '1.2.840.114350.1.13.297.3.7.1.1.1',
      description: 'BrainSAIT Healthcare OID Tree',
      healthcareCategory: 'medical',
      communicationEnabled: true,
      children: [
        {
          id: 'patient_node_1',
          name: 'Patient: Ahmed Mohammed',
          oid: '1.2.840.114350.1.13.297.3.7.1.1.1.1',
          healthcareCategory: 'patient',
          patientId: 'patient_123',
          communicationPreferences: {
            sms: true,
            voice: true,
            email: false,
            language: 'ar'
          },
          lastCommunication: '2024-08-04T09:15:00Z',
          communicationHistory: [
            {
              id: 'comm_1',
              type: 'sms',
              content: 'Appointment reminder',
              timestamp: '2024-08-04T09:15:00Z',
              status: 'delivered'
            }
          ]
        },
        {
          id: 'provider_node_1',
          name: 'Provider: Dr. Sarah Ahmed',
          oid: '1.2.840.114350.1.13.297.3.7.1.1.1.2',
          healthcareCategory: 'provider',
          providerId: 'provider_456',
          communicationCapabilities: ['emergency_alerts', 'patient_communications'],
          onCallStatus: true
        }
      ]
    },
    selectedNode: null,
    searchQuery: '',
    healthcareFilter: 'all',
    isLoading: false,
    error: null,
    expandedNodes: {},
    communicationPanel: {
      isOpen: false,
      selectedPatient: null,
      activeWorkflows: []
    },
    setTreeData: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    selectNode: vi.fn(),
    toggleNode: vi.fn(),
    setSearchQuery: vi.fn(),
    setHealthcareFilter: vi.fn(),
    openCommunicationPanel: vi.fn(),
    closeCommunicationPanel: vi.fn(),
    updateCommunicationHistory: vi.fn(),
    trackCommunicationActivity: vi.fn()
  })),
  HEALTHCARE_FILTERS: [
    { value: 'all', label: { en: 'All', ar: 'الكل' } },
    { value: 'patient', label: { en: 'Patients', ar: 'المرضى' } },
    { value: 'provider', label: { en: 'Providers', ar: 'مقدمو الخدمة' } }
  ]
}));

// Test wrapper component
const TestWrapper = ({ children, initialRoute = '/' }) => (
  <MemoryRouter initialEntries={[initialRoute]}>
    {children}
  </MemoryRouter>
);

describe('OidTree Communication Features', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('Communication Panel Integration', () => {
    it('should display communication panel when patient node is selected', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'patient_node_1',
          name: 'Patient: Ahmed Mohammed',
          healthcareCategory: 'patient',
          patientId: 'patient_123',
          communicationPreferences: {
            sms: true,
            voice: true,
            language: 'ar'
          }
        },
        communicationPanel: {
          isOpen: true,
          selectedPatient: 'patient_123'
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Communication Panel')).toBeInTheDocument();
        expect(screen.getByText('Patient: Ahmed Mohammed')).toBeInTheDocument();
      });
    });

    it('should show communication preferences for selected patient', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'patient_node_1',
          healthcareCategory: 'patient',
          patientId: 'patient_123',
          communicationPreferences: {
            sms: true,
            voice: true,
            email: false,
            language: 'ar'
          }
        },
        communicationPanel: { isOpen: true }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('SMS: Enabled')).toBeInTheDocument();
        expect(screen.getByText('Voice: Enabled')).toBeInTheDocument();
        expect(screen.getByText('Email: Disabled')).toBeInTheDocument();
        expect(screen.getByText('Preferred Language: Arabic')).toBeInTheDocument();
      });
    });

    it('should display communication history for patient', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'patient_node_1',
          healthcareCategory: 'patient',
          communicationHistory: [
            {
              id: 'comm_1',
              type: 'sms',
              content: 'Appointment reminder',
              timestamp: '2024-08-04T09:15:00Z',
              status: 'delivered'
            },
            {
              id: 'comm_2',
              type: 'voice',
              content: 'Lab results notification',
              timestamp: '2024-08-04T10:30:00Z',
              status: 'completed'
            }
          ]
        },
        communicationPanel: { isOpen: true }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Communication History')).toBeInTheDocument();
        expect(screen.getByText('Appointment reminder')).toBeInTheDocument();
        expect(screen.getByText('Lab results notification')).toBeInTheDocument();
        expect(screen.getByText('SMS • Delivered')).toBeInTheDocument();
        expect(screen.getByText('Voice • Completed')).toBeInTheDocument();
      });
    });
  });

  describe('Communication Action Menus', () => {
    it('should show SMS send option for SMS-enabled patients', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'patient_node_1',
          healthcareCategory: 'patient',
          communicationPreferences: { sms: true, language: 'ar' }
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const communicationButton = screen.getByRole('button', { name: /communication actions/i });
      await userEvent.click(communicationButton);

      await waitFor(() => {
        expect(screen.getByText('Send SMS')).toBeInTheDocument();
      });
    });

    it('should show voice call option for voice-enabled patients', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'patient_node_1',
          healthcareCategory: 'patient',
          communicationPreferences: { voice: true, language: 'en' }
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const communicationButton = screen.getByRole('button', { name: /communication actions/i });
      await userEvent.click(communicationButton);

      await waitFor(() => {
        expect(screen.getByText('Initiate Voice Call')).toBeInTheDocument();
      });
    });

    it('should show workflow trigger options', async () => {
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const workflowButton = screen.getByRole('button', { name: /trigger workflow/i });
      await userEvent.click(workflowButton);

      await waitFor(() => {
        expect(screen.getByText('Pre-Visit Workflow')).toBeInTheDocument();
        expect(screen.getByText('Post-Visit Workflow')).toBeInTheDocument();
        expect(screen.getByText('Clinical Results Workflow')).toBeInTheDocument();
        expect(screen.getByText('Emergency Workflow')).toBeInTheDocument();
      });
    });

    it('should show emergency alert option for providers', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'provider_node_1',
          healthcareCategory: 'provider',
          communicationCapabilities: ['emergency_alerts']
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const emergencyButton = screen.getByRole('button', { name: /emergency alert/i });
      expect(emergencyButton).toBeInTheDocument();
    });
  });

  describe('SMS Communication Integration', () => {
    it('should send SMS with correct parameters', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      // Open SMS dialog
      const smsButton = screen.getByRole('button', { name: /send sms/i });
      await user.click(smsButton);

      // Fill SMS form
      const messageInput = screen.getByLabelText(/message content/i);
      await user.type(messageInput, 'Your appointment is confirmed');

      const languageSelect = screen.getByLabelText(/language/i);
      await user.selectOptions(languageSelect, 'en');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await user.click(sendButton);

      await waitFor(() => {
        expect(mockCommunicationService.sendSMS).toHaveBeenCalledWith({
          to: expect.any(String),
          message: 'Your appointment is confirmed',
          patientId: expect.any(String),
          language: 'en',
          messageType: 'manual',
          encrypt: true
        });
      });
    });

    it('should handle Arabic SMS sending', async () => {
      const user = userEvent.setup();
      
      // Mock Arabic language context
      vi.mocked(require('../hooks/useLanguage').useLanguage).mockReturnValue({
        currentLanguage: 'ar',
        isRTL: true,
        t: vi.fn((key) => key),
        switchLanguage: vi.fn()
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const smsButton = screen.getByRole('button', { name: /send sms/i });
      await user.click(smsButton);

      const messageInput = screen.getByLabelText(/message content/i);
      await user.type(messageInput, 'موعدك مؤكد غداً الساعة 2 ظهراً');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await user.click(sendButton);

      await waitFor(() => {
        expect(mockCommunicationService.sendSMS).toHaveBeenCalledWith({
          to: expect.any(String),
          message: 'موعدك مؤكد غداً الساعة 2 ظهراً',
          patientId: expect.any(String),
          language: 'ar',
          messageType: 'manual',
          encrypt: true,
          rtlSupport: true
        });
      });
    });

    it('should show SMS delivery status updates', async () => {
      // Mock successful SMS send
      mockCommunicationService.sendSMS.mockResolvedValueOnce({
        messageId: 'sms_success_123',
        status: 'sent',
        deliveryTracking: true
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const smsButton = screen.getByRole('button', { name: /send sms/i });
      await user.click(smsButton);

      const messageInput = screen.getByLabelText(/message content/i);
      await user.type(messageInput, 'Test message');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('SMS sent successfully')).toBeInTheDocument();
        expect(screen.getByText('Message ID: sms_success_123')).toBeInTheDocument();
      });
    });
  });

  describe('Voice Communication Integration', () => {
    it('should initiate voice call with correct parameters', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const voiceButton = screen.getByRole('button', { name: /initiate voice call/i });
      await user.click(voiceButton);

      // Select call type
      const callTypeSelect = screen.getByLabelText(/call type/i);
      await user.selectOptions(callTypeSelect, 'appointment_reminder');

      // Select language
      const languageSelect = screen.getByLabelText(/language/i);
      await user.selectOptions(languageSelect, 'ar');

      const callButton = screen.getByRole('button', { name: /start call/i });
      await user.click(callButton);

      await waitFor(() => {
        expect(mockCommunicationService.initiateVoiceCall).toHaveBeenCalledWith({
          to: expect.any(String),
          scriptType: 'appointment_reminder',
          patientId: expect.any(String),
          language: 'ar',
          voiceGender: 'female',
          recordCall: true,
          encryptRecording: true
        });
      });
    });

    it('should display voice call status', async () => {
      mockCommunicationService.initiateVoiceCall.mockResolvedValueOnce({
        callId: 'call_success_456',
        status: 'initiated',
        estimatedDuration: '60 seconds'
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const voiceButton = screen.getByRole('button', { name: /initiate voice call/i });
      await user.click(voiceButton);

      const callButton = screen.getByRole('button', { name: /start call/i });
      await user.click(callButton);

      await waitFor(() => {
        expect(screen.getByText('Voice call initiated')).toBeInTheDocument();
        expect(screen.getByText('Call ID: call_success_456')).toBeInTheDocument();
        expect(screen.getByText('Estimated duration: 60 seconds')).toBeInTheDocument();
      });
    });
  });

  describe('Workflow Integration', () => {
    it('should trigger pre-visit workflow', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const workflowButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(workflowButton);

      const preVisitButton = screen.getByText('Pre-Visit Workflow');
      await user.click(preVisitButton);

      // Fill workflow parameters
      const appointmentDateInput = screen.getByLabelText(/appointment date/i);
      await user.type(appointmentDateInput, '2024-08-05T14:00:00');

      const triggerButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(triggerButton);

      await waitFor(() => {
        expect(mockCommunicationService.triggerWorkflow).toHaveBeenCalledWith({
          patientId: expect.any(String),
          workflowType: 'pre_visit',
          appointmentId: expect.any(String),
          triggerTime: 'immediate',
          customParameters: expect.objectContaining({
            appointmentDate: '2024-08-05T14:00:00'
          })
        });
      });
    });

    it('should display workflow execution status', async () => {
      mockCommunicationService.triggerWorkflow.mockResolvedValueOnce({
        workflowId: 'workflow_success_789',
        status: 'started',
        stepsScheduled: 4,
        estimatedCompletion: '5 minutes'
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const workflowButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(workflowButton);

      const emergencyButton = screen.getByText('Emergency Workflow');
      await user.click(emergencyButton);

      const triggerButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(triggerButton);

      await waitFor(() => {
        expect(screen.getByText('Workflow started successfully')).toBeInTheDocument();
        expect(screen.getByText('Workflow ID: workflow_success_789')).toBeInTheDocument();
        expect(screen.getByText('Steps scheduled: 4')).toBeInTheDocument();
      });
    });
  });

  describe('Emergency Alert Integration', () => {
    it('should send emergency alert for providers', async () => {
      const user = userEvent.setup();
      
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        selectedNode: {
          id: 'provider_node_1',
          healthcareCategory: 'provider',
          communicationCapabilities: ['emergency_alerts']
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const emergencyButton = screen.getByRole('button', { name: /emergency alert/i });
      await user.click(emergencyButton);

      // Fill emergency form
      const alertTypeSelect = screen.getByLabelText(/alert type/i);
      await user.selectOptions(alertTypeSelect, 'code_blue');

      const locationInput = screen.getByLabelText(/location/i);
      await user.type(locationInput, 'ICU Room 205');

      const severitySelect = screen.getByLabelText(/severity/i);
      await user.selectOptions(severitySelect, 'critical');

      const sendAlertButton = screen.getByRole('button', { name: /send alert/i });
      await user.click(sendAlertButton);

      await waitFor(() => {
        expect(mockCommunicationService.sendEmergencyAlert).toHaveBeenCalledWith({
          alertType: 'code_blue',
          location: 'ICU Room 205',
          severity: 'critical',
          responseTeams: expect.any(Array),
          patientId: expect.any(String)
        });
      });
    });

    it('should display emergency alert broadcast status', async () => {
      mockCommunicationService.sendEmergencyAlert.mockResolvedValueOnce({
        alertId: 'alert_critical_success_123',
        broadcastSent: true,
        recipientsNotified: 15,
        responseConfirmations: 3
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const emergencyButton = screen.getByRole('button', { name: /emergency alert/i });
      await user.click(emergencyButton);

      const sendAlertButton = screen.getByRole('button', { name: /send alert/i });
      await user.click(sendAlertButton);

      await waitFor(() => {
        expect(screen.getByText('Emergency alert broadcast successfully')).toBeInTheDocument();
        expect(screen.getByText('Recipients notified: 15')).toBeInTheDocument();
        expect(screen.getByText('Response confirmations: 3')).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Communication Updates', () => {
    it('should update communication status in real-time', async () => {
      vi.useFakeTimers();
      
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      const mockUpdateHistory = vi.fn();
      
      mockStore.mockReturnValue({
        ...mockStore(),
        updateCommunicationHistory: mockUpdateHistory,
        communicationPanel: { isOpen: true }
      });

      // Mock WebSocket or polling updates
      mockCommunicationService.getCommunicationStatus.mockResolvedValue({
        messageId: 'msg_123',
        status: 'delivered',
        deliveredAt: '2024-08-04T10:35:00Z'
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      // Simulate real-time update
      act(() => {
        vi.advanceTimersByTime(5000); // 5 seconds
      });

      await waitFor(() => {
        expect(mockCommunicationService.getCommunicationStatus).toHaveBeenCalled();
        expect(mockUpdateHistory).toHaveBeenCalledWith(
          expect.objectContaining({
            status: 'delivered',
            deliveredAt: '2024-08-04T10:35:00Z'
          })
        );
      });

      vi.useRealTimers();
    });

    it('should show live workflow execution progress', async () => {
      vi.useFakeTimers();
      
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        communicationPanel: {
          isOpen: true,
          activeWorkflows: [
            {
              workflowId: 'wf_active_123',
              type: 'pre_visit',
              status: 'in_progress',
              currentStep: 2,
              totalSteps: 4,
              estimatedCompletion: '3 minutes'
            }
          ]
        }
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Active Workflows')).toBeInTheDocument();
        expect(screen.getByText('Pre-Visit Workflow')).toBeInTheDocument();
        expect(screen.getByText('Step 2 of 4')).toBeInTheDocument();
        expect(screen.getByText('ETA: 3 minutes')).toBeInTheDocument();
      });

      vi.useRealTimers();
    });
  });

  describe('Error Handling and Loading States', () => {
    it('should show loading state during SMS sending', async () => {
      // Mock delayed SMS sending
      let resolvePromise;
      const delayedPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      
      mockCommunicationService.sendSMS.mockReturnValueOnce(delayedPromise);

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const smsButton = screen.getByRole('button', { name: /send sms/i });
      await user.click(smsButton);

      const messageInput = screen.getByLabelText(/message content/i);
      await user.type(messageInput, 'Test message');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await user.click(sendButton);

      // Should show loading state
      expect(screen.getByText('Sending SMS...')).toBeInTheDocument();
      expect(sendButton).toBeDisabled();

      // Resolve the promise
      resolvePromise({
        messageId: 'msg_delayed_123',
        status: 'sent'
      });

      await waitFor(() => {
        expect(screen.getByText('SMS sent successfully')).toBeInTheDocument();
        expect(sendButton).not.toBeDisabled();
      });
    });

    it('should handle SMS sending errors gracefully', async () => {
      mockCommunicationService.sendSMS.mockRejectedValueOnce(
        new Error('Network error: Unable to connect to Twilio')
      );

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const smsButton = screen.getByRole('button', { name: /send sms/i });
      await user.click(smsButton);

      const messageInput = screen.getByLabelText(/message content/i);
      await user.type(messageInput, 'Test message');

      const sendButton = screen.getByRole('button', { name: /send message/i });
      await user.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to send SMS')).toBeInTheDocument();
        expect(screen.getByText('Network error: Unable to connect to Twilio')).toBeInTheDocument();
      });
    });

    it('should handle workflow trigger errors', async () => {
      mockCommunicationService.triggerWorkflow.mockRejectedValueOnce(
        new Error('Workflow validation failed: Missing appointment ID')
      );

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const workflowButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(workflowButton);

      const preVisitButton = screen.getByText('Pre-Visit Workflow');
      await user.click(preVisitButton);

      const triggerButton = screen.getByRole('button', { name: /trigger workflow/i });
      await user.click(triggerButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to trigger workflow')).toBeInTheDocument();
        expect(screen.getByText('Workflow validation failed: Missing appointment ID')).toBeInTheDocument();
      });
    });

    it('should show communication service unavailable state', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      mockStore.mockReturnValue({
        ...mockStore(),
        error: 'Communication service is temporarily unavailable',
        isLoading: false
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Communication Service Unavailable')).toBeInTheDocument();
        expect(screen.getByText('Communication service is temporarily unavailable')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
      });
    });
  });

  describe('Arabic/English UI Switching', () => {
    it('should switch to Arabic UI when language is changed', async () => {
      const mockSwitchLanguage = vi.fn();
      
      vi.mocked(require('../hooks/useLanguage').useLanguage).mockReturnValue({
        currentLanguage: 'en',
        isRTL: false,
        t: vi.fn((key) => key),
        switchLanguage: mockSwitchLanguage
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      const languageToggle = screen.getByRole('button', { name: /switch to arabic/i });
      await user.click(languageToggle);

      expect(mockSwitchLanguage).toHaveBeenCalledWith('ar');
    });

    it('should display Arabic UI correctly with RTL layout', async () => {
      vi.mocked(require('../hooks/useLanguage').useLanguage).mockReturnValue({
        currentLanguage: 'ar',
        isRTL: true,
        t: vi.fn((key) => {
          const arabicTranslations = {
            'communication_panel': 'لوحة التواصل',
            'send_sms': 'إرسال رسالة نصية',
            'voice_call': 'مكالمة صوتية',
            'emergency_alert': 'تنبيه طارئ'
          };
          return arabicTranslations[key] || key;
        }),
        switchLanguage: vi.fn()
      });

      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('لوحة التواصل')).toBeInTheDocument();
        expect(screen.getByText('إرسال رسالة نصية')).toBeInTheDocument();
        expect(screen.getByText('مكالمة صوتية')).toBeInTheDocument();
        expect(screen.getByText('تنبيه طارئ')).toBeInTheDocument();
      });

      // Check RTL layout
      const communicationPanel = screen.getByText('لوحة التواصل').closest('div');
      expect(communicationPanel).toHaveAttribute('dir', 'rtl');
      expect(communicationPanel).toHaveClass('rtl');
    });

    it('should maintain communication state when switching languages', async () => {
      const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
      const mockTrackActivity = vi.fn();
      
      mockStore.mockReturnValue({
        ...mockStore(),
        trackCommunicationActivity: mockTrackActivity,
        communicationPanel: {
          isOpen: true,
          selectedPatient: 'patient_123'
        }
      });

      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      // Switch language
      const languageToggle = screen.getByRole('button', { name: /switch to arabic/i });
      await user.click(languageToggle);

      // Communication panel should remain open
      await waitFor(() => {
        expect(mockTrackActivity).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'language_switched',
            from: 'en',
            to: 'ar',
            communicationPanelOpen: true
          })
        );
      });
    });
  });

  describe('Accessibility and User Experience', () => {
    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      // Tab through communication controls
      await user.tab();
      expect(screen.getByRole('button', { name: /send sms/i })).toHaveFocus();

      await user.tab();
      expect(screen.getByRole('button', { name: /initiate voice call/i })).toHaveFocus();

      await user.tab();
      expect(screen.getByRole('button', { name: /trigger workflow/i })).toHaveFocus();
    });

    it('should have proper ARIA labels for communication actions', () => {
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      expect(screen.getByRole('button', { name: /send sms/i })).toHaveAttribute(
        'aria-label',
        'Send SMS message to patient'
      );

      expect(screen.getByRole('button', { name: /initiate voice call/i })).toHaveAttribute(
        'aria-label',
        'Initiate voice call to patient'
      );

      expect(screen.getByRole('button', { name: /emergency alert/i })).toHaveAttribute(
        'aria-label',
        'Send emergency alert to response teams'
      );
    });

    it('should announce communication status changes to screen readers', async () => {
      render(
        <TestWrapper>
          <OidTree />
        </TestWrapper>
      );

      // Mock status change
      const statusAnnouncement = screen.getByRole('status', { name: /communication status/i });
      
      // Simulate SMS sent successfully
      act(() => {
        statusAnnouncement.textContent = 'SMS sent successfully to patient Ahmed Mohammed';
      });

      expect(statusAnnouncement).toHaveTextContent('SMS sent successfully to patient Ahmed Mohammed');
    });
  });
});

describe('OidTree Performance with Communication Features', () => {
  it('should handle large communication history efficiently', async () => {
    const largeCommHistory = Array.from({ length: 1000 }, (_, i) => ({
      id: `comm_${i}`,
      type: i % 2 === 0 ? 'sms' : 'voice',
      content: `Communication ${i}`,
      timestamp: new Date(Date.now() - i * 60000).toISOString(),
      status: 'delivered'
    }));

    const mockStore = require('../stores/oid-tree-store').useOidTreeStore;
    mockStore.mockReturnValue({
      ...mockStore(),
      selectedNode: {
        id: 'patient_with_history',
        healthcareCategory: 'patient',
        communicationHistory: largeCommHistory
      },
      communicationPanel: { isOpen: true }
    });

    const startTime = performance.now();
    
    render(
      <TestWrapper>
        <OidTree />
      </TestWrapper>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render large history within reasonable time
    expect(renderTime).toBeLessThan(1000);
    
    await waitFor(() => {
      expect(screen.getByText('Communication History')).toBeInTheDocument();
      // Should virtualize or paginate large lists
      expect(screen.getByText('Showing 1-50 of 1000 communications')).toBeInTheDocument();
    });
  });

  it('should debounce rapid communication actions', async () => {
    vi.useFakeTimers();
    
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    
    render(
      <TestWrapper>
        <OidTree />
      </TestWrapper>
    );

    const smsButton = screen.getByRole('button', { name: /send sms/i });
    
    // Rapid clicks should be debounced
    await user.click(smsButton);
    await user.click(smsButton);
    await user.click(smsButton);

    // Only one dialog should open
    expect(screen.getAllByText('Send SMS Message')).toHaveLength(1);

    vi.useRealTimers();
  });
});

export default {
  displayName: 'OidTree Communication Tests',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/tests/setup.js']
};