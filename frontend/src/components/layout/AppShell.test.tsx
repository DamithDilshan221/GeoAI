import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AppShell } from './AppShell';
import apiClient from '../../api/client';
import React from 'react';

vi.mock('../../api/client', () => ({
  default: {
    get: vi.fn(),
  },
}));

describe('AppShell', () => {
  it('renders health check success', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { status: 'ok' } });

    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );

    expect(screen.getByText('Checking backend...')).toBeDefined();
    
    await waitFor(() => {
      expect(screen.getByText('Backend: connected')).toBeDefined();
    });
  });

  it('renders health check failure', async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('Network error'));

    render(
      <AppShell>
        <div>Content</div>
      </AppShell>
    );

    await waitFor(() => {
      expect(screen.getByText('Backend: unreachable')).toBeDefined();
    });
  });
});
