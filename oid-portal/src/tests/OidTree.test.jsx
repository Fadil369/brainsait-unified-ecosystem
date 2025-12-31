import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import OidTree from '../pages/OidTree';

// OidTree uses `useLanguage` for RTL + copy.
vi.mock('../hooks/useLanguage', () => ({
  useLanguage: () => ({
    isRTL: false,
    currentLanguage: 'en',
    t: (k) => k
  })
}));

describe('OidTree page', () => {
  it('renders the OID Tree page header', () => {
    render(
      <MemoryRouter>
        <OidTree />
      </MemoryRouter>
    );

    expect(
      screen.getByRole('heading', { name: /intelligent healthcare oid tree/i })
    ).toBeInTheDocument();
  });

  it('shows details after selecting a node', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <OidTree />
      </MemoryRouter>
    );

    // Select the root node (card title text)
    await user.click(screen.getByText('Saudi Healthcare System'));

    // The details panel should now show the node identifier
    expect(screen.getAllByText('1.2.840.114494.100.1').length).toBeGreaterThan(0);
  });
});

