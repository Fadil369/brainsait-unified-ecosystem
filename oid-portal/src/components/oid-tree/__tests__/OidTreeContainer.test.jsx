import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import OidTreeContainer from '../OidTreeContainer';

vi.mock('../../../hooks/useLanguage', () => ({
  useLanguage: () => ({ currentLanguage: 'en', isRTL: false })
}));

vi.mock('../../../contexts/UnifiedHealthcareContext', () => ({
  useUnifiedHealthcare: () => ({
    getCurrentUserRole: vi.fn().mockResolvedValue('doctor'),
    trackHealthcareActivity: vi.fn().mockResolvedValue(true)
  })
}));

vi.mock('../../../hooks/useFHIR', () => ({
  useFHIR: () => ({ isLoading: false, error: null })
}));

// Avoid importing the TS constants module in tests.
vi.mock('../../../constants/healthcare-data', () => ({
  createHealthcareOidTreeData: () => ({
    id: 'root',
    oid: '1.3.6.1.4.1.61026',
    name: 'BrainSAIT',
    children: []
  })
}));

// Replace lazy-loaded children with trivial components.
vi.mock('../TreeControls', () => ({ default: () => <div>TreeControls</div> }));
vi.mock('../VirtualizedTreeNode', () => ({ default: () => <div>VirtualizedTree</div> }));
vi.mock('../NodeDetailsPanel', () => ({ default: () => <div>NodeDetails</div> }));

// Provide a stable store shape for the container.
vi.mock('../../../stores/oid-tree-store', () => ({
  HEALTHCARE_FILTERS: [{ value: 'all', label: { en: 'All', ar: 'الكل' } }],
  useOidTreeStore: () => ({
    treeData: null,
    selectedNode: null,
    searchQuery: '',
    healthcareFilter: 'all',
    isLoading: false,
    error: null,
    setTreeData: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    selectNode: vi.fn(),
    trackHealthcareActivity: vi.fn()
  })
}));

describe('OidTreeContainer', () => {
  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({})
    });
  });

  it('renders the header and subcomponents', async () => {
    render(
      <MemoryRouter>
        <OidTreeContainer />
      </MemoryRouter>
    );

    expect(
      screen.getByRole('heading', { name: /unified healthcare oid tree/i })
    ).toBeInTheDocument();

    // Lazy components resolve asynchronously
    expect(await screen.findByText('TreeControls')).toBeInTheDocument();
    expect(await screen.findByText('VirtualizedTree')).toBeInTheDocument();
    expect(await screen.findByText('NodeDetails')).toBeInTheDocument();
  });
});

