/* eslint-disable @typescript-eslint/no-explicit-any */
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useNearbyFacilities } from './useNearbyFacilities';
import { getNearbyFacilities } from '../api/facilities';
import React from 'react';

vi.mock('../api/facilities', () => ({
  getNearbyFacilities: vi.fn(),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('useNearbyFacilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it('does not call getNearbyFacilities when params are null', () => {
    renderHook(() => useNearbyFacilities(null), { wrapper });
    expect(getNearbyFacilities).not.toHaveBeenCalled();
  });

  it('calls getNearbyFacilities with exact params, including radius_m, and no accessible_only', async () => {
    vi.mocked(getNearbyFacilities).mockResolvedValueOnce([]);

    const params = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000 };
    const { result } = renderHook(() => useNearbyFacilities(params), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getNearbyFacilities).toHaveBeenCalledTimes(1);
    expect(getNearbyFacilities).toHaveBeenCalledWith(params);
    
    // Explicitly assert `accessible_only` is NOT a key in the call arguments
    const callArgs = vi.mocked(getNearbyFacilities).mock.calls[0][0];
    expect('accessible_only' in callArgs).toBe(false);
  });

  it('makes a second call when radius_m changes', async () => {
    vi.mocked(getNearbyFacilities).mockResolvedValue([]);

    const params1 = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000 };
    const { result, rerender } = renderHook((props: { params: any } = { params: params1 }) => useNearbyFacilities(props.params), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(getNearbyFacilities).toHaveBeenCalledTimes(1);

    const params2 = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 2000 };
    rerender({ params: params2 });

    await waitFor(() => expect(getNearbyFacilities).toHaveBeenCalledTimes(2));
    expect(getNearbyFacilities).toHaveBeenLastCalledWith(params2);
  });
});
