import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useLiveNavigation } from './useLiveNavigation';
import type { OSRMStep } from '../routing/maneuvers';

// Steps with known maneuver locations — [lon, lat] convention
const STEP_A_LOCATION: [number, number] = [80.5965, 7.2545]; // [lon, lat]
const STEP_B_LOCATION: [number, number] = [80.5980, 7.2560];

const STEPS: OSRMStep[] = [
  { maneuver: { type: 'depart', location: STEP_A_LOCATION }, distance: 200 },
  { maneuver: { type: 'turn', modifier: 'right', location: STEP_B_LOCATION }, distance: 100 },
  { maneuver: { type: 'arrive' }, distance: 0 },
];

describe('useLiveNavigation', () => {
  let mockWatchPosition: ReturnType<typeof vi.fn>;
  let mockClearWatch: ReturnType<typeof vi.fn>;
  let capturedSuccessCallback: ((pos: GeolocationPosition) => void) | null = null;

  beforeEach(() => {
    capturedSuccessCallback = null;
    mockWatchPosition = vi.fn((successCb) => {
      capturedSuccessCallback = successCb;
      return 42; // watchId
    });
    mockClearWatch = vi.fn();

    Object.defineProperty(global.navigator, 'geolocation', {
      value: { watchPosition: mockWatchPosition, clearWatch: mockClearWatch },
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const makePosition = (lat: number, lon: number): GeolocationPosition =>
    ({
      coords: { latitude: lat, longitude: lon, accuracy: 5 },
      timestamp: Date.now(),
    }) as unknown as GeolocationPosition;

  it('starts at stepIdx 0', () => {
    const { result } = renderHook(() => useLiveNavigation(STEPS));
    expect(result.current.stepIdx).toBe(0);
  });

  it('advances stepIdx when within 15m of maneuver location', () => {
    const { result } = renderHook(() => useLiveNavigation(STEPS));

    act(() => {
      // Move to exactly the maneuver.location of step 0 (converted from lon,lat)
      capturedSuccessCallback?.(makePosition(7.2545, 80.5965));
    });

    expect(result.current.stepIdx).toBe(1);
  });

  it('does not advance when far from maneuver location', () => {
    const { result } = renderHook(() => useLiveNavigation(STEPS));

    act(() => {
      // Far from step 0's location
      capturedSuccessCallback?.(makePosition(7.300, 80.700));
    });

    expect(result.current.stepIdx).toBe(0);
  });

  it('does not advance past the last step', () => {
    const { result } = renderHook(() => useLiveNavigation(STEPS));

    act(() => {
      // Advance to step 1
      capturedSuccessCallback?.(makePosition(7.2545, 80.5965));
    });
    act(() => {
      // Advance to step 2 (arrive)
      capturedSuccessCallback?.(makePosition(7.2560, 80.5980));
    });
    act(() => {
      // Try to advance beyond arrive — should stay at 2
      capturedSuccessCallback?.(makePosition(7.2560, 80.5980));
    });

    // 2 = index of 'arrive' step (last)
    expect(result.current.stepIdx).toBe(2);
  });

  it('calls clearWatch on unmount', () => {
    const { unmount } = renderHook(() => useLiveNavigation(STEPS));
    unmount();
    expect(mockClearWatch).toHaveBeenCalledWith(42);
  });

  it('updates currentPosition on each position event', () => {
    const { result } = renderHook(() => useLiveNavigation(STEPS));

    act(() => {
      capturedSuccessCallback?.(makePosition(7.300, 80.700));
    });

    expect(result.current.currentPosition).toEqual({ lat: 7.300, lon: 80.700 });
  });
});
