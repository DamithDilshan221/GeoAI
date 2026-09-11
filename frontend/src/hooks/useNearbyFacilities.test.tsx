/* eslint-disable @typescript-eslint/no-explicit-any */
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useNearbyFacilities } from './useNearbyFacilities';
import { getNearbyWashrooms } from '../api/washrooms';
import React from 'react';

vi.mock('../api/washrooms', () => ({
  getNearbyWashrooms: vi.fn(),
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

  it('does not call getNearbyWashrooms when params are null', () => {
    renderHook(() => useNearbyFacilities(null), { wrapper });
    expect(getNearbyWashrooms).not.toHaveBeenCalled();
  });

  it('calls getNearbyWashrooms WITHOUT audience key when selectedAudience is null', async () => {
    vi.mocked(getNearbyWashrooms).mockResolvedValueOnce([]);

    const params = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000, audience: null };
    const { result } = renderHook(() => useNearbyFacilities(params), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getNearbyWashrooms).toHaveBeenCalledTimes(1);
    
    // Explicitly assert `audience` is NOT a key in the call arguments
    const callArgs = vi.mocked(getNearbyWashrooms).mock.calls[0][0];
    expect('audience' in callArgs).toBe(false);
  });

  it('calls getNearbyWashrooms with audience key when selectedAudience is STAFF', async () => {
    vi.mocked(getNearbyWashrooms).mockResolvedValueOnce([]);

    const params: any = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000, audience: 'STAFF' };
    const { result } = renderHook(() => useNearbyFacilities(params), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getNearbyWashrooms).toHaveBeenCalledTimes(1);
    
    const callArgs = vi.mocked(getNearbyWashrooms).mock.calls[0][0];
    expect(callArgs.audience).toBe('STAFF');
  });

  it('makes a second call when only selectedAudience changes', async () => {
    vi.mocked(getNearbyWashrooms).mockResolvedValue([]);

    const params1: any = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000, audience: null };
    const { result, rerender } = renderHook((props: { params: any } = { params: params1 }) => useNearbyFacilities(props.params), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(getNearbyWashrooms).toHaveBeenCalledTimes(1);

    const params2: any = { lat: 10, lon: 20, category: 'UNISEX', radius_m: 1000, audience: 'VISITOR' };
    rerender({ params: params2 });

    await waitFor(() => expect(getNearbyWashrooms).toHaveBeenCalledTimes(2));
    const callArgs = vi.mocked(getNearbyWashrooms).mock.calls[1][0];
    expect(callArgs.audience).toBe('VISITOR');
  });
});
