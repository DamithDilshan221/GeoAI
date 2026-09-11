import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useRecommendation } from './useRecommendation';
import { getRecommendations } from '../api/recommendations';
import React from 'react';

vi.mock('../api/recommendations', () => ({
  getRecommendations: vi.fn(),
}));

const makeClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const wrapper =
  (client: QueryClient) =>
  ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );

describe('useRecommendation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('does not call getRecommendations when params are null', () => {
    const client = makeClient();
    renderHook(() => useRecommendation(null), { wrapper: wrapper(client) });
    expect(getRecommendations).not.toHaveBeenCalled();
  });

  it('calls getRecommendations with correct args when params are provided', async () => {
    const client = makeClient();
    vi.mocked(getRecommendations).mockResolvedValueOnce({
      recommended_facility: null,
      ranked_facilities: [],
      explanation: null,
      message: 'No suitable facilities were found within the current search radius.',
    });

    const params = { lat: 6.9, lon: 79.8, category: 'male', radius_m: 1000, selectedAudience: null };
    const { result } = renderHook(() => useRecommendation(params), {
      wrapper: wrapper(client),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getRecommendations).toHaveBeenCalledTimes(1);
    expect(getRecommendations).toHaveBeenCalledWith({
      lat: 6.9,
      lon: 79.8,
      category: 'male',
      radius_m: 1000,
      secondary_preference: undefined,
    });
  });

  it('maps selectedAudience=STAFF to secondary_preference="staff_preferred"', async () => {
    const client = makeClient();
    vi.mocked(getRecommendations).mockResolvedValueOnce({
      recommended_facility: null,
      ranked_facilities: [],
      explanation: null,
      message: null,
    });

    const params = { lat: 6.9, lon: 79.8, category: 'male', radius_m: 1000, selectedAudience: 'STAFF' as const };
    const { result } = renderHook(() => useRecommendation(params), {
      wrapper: wrapper(client),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getRecommendations).toHaveBeenCalledWith(
      expect.objectContaining({ secondary_preference: 'staff_preferred' }),
    );
  });

  it('does NOT pass secondary_preference when selectedAudience=null', async () => {
    const client = makeClient();
    vi.mocked(getRecommendations).mockResolvedValueOnce({
      recommended_facility: null,
      ranked_facilities: [],
      explanation: null,
      message: null,
    });

    const params = { lat: 6.9, lon: 79.8, category: 'male', radius_m: 1000, selectedAudience: null };
    const { result } = renderHook(() => useRecommendation(params), {
      wrapper: wrapper(client),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    const callArgs = vi.mocked(getRecommendations).mock.calls[0][0];
    expect(callArgs.secondary_preference).toBeUndefined();
  });
});
