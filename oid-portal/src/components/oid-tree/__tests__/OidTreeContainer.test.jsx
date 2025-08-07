/**
 * OidTreeContainer Tests
 * Comprehensive tests for the refactored OID tree component
 */

// React import removed
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import OidTreeContainer from '../OidTreeContainer';

// Mock dependencies
vi.mock('../../../hooks/useLanguage', () => ({
  useLanguage: () => ({
    currentLanguage: 'en',
    isRTL: false,
    t: (key) => key
  })
}));

vi.mock('../../../contexts/UnifiedHealthcareContext', () => ({
  useUnifiedHealthcare: () => ({
    getCurrentUserRole: vi.fn().mockResolvedValue('admin'),
    trackHealthcareActivity: vi.fn().mockResolvedValue(true),
    checkHealthcarePermissions: vi.fn().mockReturnValue(true)
  })
}));

vi.mock('../../../hooks/useFHIR', () => ({
  useFHIR: () => ({
    isLoading: false,
    error: null,
    createFHIRResource: vi.fn()
  })
}));

// Mock Zustand store
vi.mock('../../../stores/oid-tree-store', () => ({
  useOidTreeStore: () => ({
    treeData: {
      id: 'root',
      name: 'OID Root',
      oid: '1',
      description: 'Root of the Object Identifier tree',
      children: []
    },
    selectedNode: null,
    searchQuery: '',
    healthcareFilter: 'all',
    isLoading: false,
    error: null,
    expandedNodes: {},
    setTreeData: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    selectNode: vi.fn(),
    trackHealthcareActivity: vi.fn(),
    toggleNode: vi.fn(),
    setSearchQuery: vi.fn(),
    setHealthcareFilter: vi.fn(),
    expandAll: vi.fn(),
    collapseAll: vi.fn()
  }),
  HEALTHCARE_FILTERS: [
    { value: 'all', label: { en: 'All', ar: 'الكل' } },
    { value: 'medical', label: { en: 'Medical', ar: 'طبي' } }
  ]
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('OidTreeContainer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the OID tree header correctly', () => {
    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    expect(screen.getByText('Unified Healthcare OID Tree')).toBeInTheDocument();
    expect(screen.getByText(/Enterprise Number 61026/)).toBeInTheDocument();
  });

  it('displays FHIR integration status', () => {
    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    expect(screen.getByText('FHIR R4 Integrated')).toBeInTheDocument();
  });

  it('shows loading state initially', async () => {
    const mockStore = {
      treeData: null,
      isLoading: true,
      error: null,
      selectedNode: null,
      searchQuery: '',
      healthcareFilter: 'all',
      expandedNodes: {},
      setTreeData: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      selectNode: vi.fn(),
      trackHealthcareActivity: vi.fn()
    };

    vi.mocked(require('../../../stores/oid-tree-store').useOidTreeStore).mockReturnValue(mockStore);

    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    expect(screen.getByText('Loading OID Tree...')).toBeInTheDocument();
  });

  it('handles error state correctly', () => {
    const mockStore = {
      treeData: null,
      isLoading: false,
      error: 'Failed to load tree data',
      selectedNode: null,
      searchQuery: '',
      healthcareFilter: 'all',
      expandedNodes: {},
      setTreeData: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      selectNode: vi.fn(),
      trackHealthcareActivity: vi.fn()
    };

    vi.mocked(require('../../../stores/oid-tree-store').useOidTreeStore).mockReturnValue(mockStore);

    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    expect(screen.getByText('OID Tree Loading Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to load tree data')).toBeInTheDocument();
  });

  it('renders tree components when data is loaded', async () => {
    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    // Wait for lazy components to load
    await waitFor(() => {
      expect(screen.getByText('OID Hierarchy')).toBeInTheDocument();
      expect(screen.getByText('Node Details')).toBeInTheDocument();
    });
  });

  it('tracks healthcare activity on initialization', async () => {
    const mockTrackActivity = vi.fn().mockResolvedValue(true);
    
    vi.mocked(require('../../../contexts/UnifiedHealthcareContext').useUnifiedHealthcare).mockReturnValue({
      getCurrentUserRole: vi.fn().mockResolvedValue('admin'),
      trackHealthcareActivity: mockTrackActivity,
      checkHealthcarePermissions: vi.fn().mockReturnValue(true)
    });

    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(mockTrackActivity).toHaveBeenCalledWith('oid_tree_accessed', {
        userRole: 'admin',
        language: 'en',
        timestamp: expect.any(String)
      });
    });
  });
});

describe('OidTreeContainer Performance', () => {
  it('should handle large datasets efficiently', async () => {
    const largeTreeData = {
      id: 'root',
      name: 'OID Root',
      oid: '1',
      children: Array.from({ length: 1000 }, (_, i) => ({
        id: `node-${i}`,
        name: `Node ${i}`,
        oid: `1.${i}`,
        healthcareCategory: 'medical'
      }))
    };

    const mockStore = {
      treeData: largeTreeData,
      isLoading: false,
      error: null,
      selectedNode: null,
      searchQuery: '',
      healthcareFilter: 'all',
      expandedNodes: {},
      setTreeData: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      selectNode: vi.fn(),
      trackHealthcareActivity: vi.fn()
    };

    vi.mocked(require('../../../stores/oid-tree-store').useOidTreeStore).mockReturnValue(mockStore);

    const startTime = performance.now();
    
    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Render should complete within reasonable time even with large dataset
    expect(renderTime).toBeLessThan(1000); // Less than 1 second
  });
});

describe('OidTreeContainer RTL Support', () => {
  it('applies RTL styles correctly for Arabic language', () => {
    vi.mocked(require('../../../hooks/useLanguage').useLanguage).mockReturnValue({
      currentLanguage: 'ar',
      isRTL: true,
      t: (key) => key
    });

    render(
      <TestWrapper>
        <OidTreeContainer />
      </TestWrapper>
    );

    const container = screen.getByText('شجرة OID الصحية الموحدة').closest('div');
    expect(container).toHaveClass('rtl');
    expect(container).toHaveAttribute('dir', 'rtl');
  });
});