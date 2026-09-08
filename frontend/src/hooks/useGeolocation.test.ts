import { renderHook, act } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { useGeolocation, GEOLOCATION_MESSAGES } from './useGeolocation';

describe('useGeolocation', () => {
  let mockGetCurrentPosition: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockGetCurrentPosition = vi.fn();
    Object.defineProperty(global.navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('does not request location on mount', () => {
    renderHook(() => useGeolocation());
    expect(mockGetCurrentPosition).not.toHaveBeenCalled();
  });

  it('handles success correctly', () => {
    mockGetCurrentPosition.mockImplementationOnce((success) => {
      success({ coords: { latitude: 10, longitude: 20, accuracy: 5 } });
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.request();
    });

    expect(result.current.status).toBe('granted');
    expect(result.current.location).toEqual({ lat: 10, lon: 20, accuracy: 5 });
    expect(result.current.errorMessage).toBeNull();
  });

  it('handles PERMISSION_DENIED (code 1)', () => {
    mockGetCurrentPosition.mockImplementationOnce((_, error) => {
      error({ code: 1 });
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.request();
    });

    expect(result.current.status).toBe('denied');
    expect(result.current.errorMessage).toBe(GEOLOCATION_MESSAGES.denied);
  });

  it('handles POSITION_UNAVAILABLE (code 2)', () => {
    mockGetCurrentPosition.mockImplementationOnce((_, error) => {
      error({ code: 2 });
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.request();
    });

    expect(result.current.status).toBe('unavailable');
    expect(result.current.errorMessage).toBe(GEOLOCATION_MESSAGES.unavailable);
  });

  it('handles TIMEOUT (code 3) as unavailable', () => {
    mockGetCurrentPosition.mockImplementationOnce((_, error) => {
      error({ code: 3 });
    });

    const { result } = renderHook(() => useGeolocation());
    act(() => {
      result.current.request();
    });

    expect(result.current.status).toBe('unavailable');
    expect(result.current.errorMessage).toBe(GEOLOCATION_MESSAGES.unavailable);
  });
});
