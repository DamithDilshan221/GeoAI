/**
 * useLiveNavigation — watchPosition-driven step advancement.
 *
 * Owns stepIdx state and a navigator.geolocation.watchPosition subscription.
 * Advances stepIdx when within 15m of the current step's maneuver.location.
 * Clears the watch on unmount (mirrors prototype's closeNavigation pattern).
 */

import { useState, useEffect, useRef } from 'react';
import { haversineDistanceM } from '../utils/geo';
import type { OSRMStep } from '../routing/maneuvers';

export interface CurrentPosition {
  lat: number;
  lon: number;
}

export interface LiveNavigationState {
  stepIdx: number;
  currentPosition: CurrentPosition | null;
}

const ADVANCE_THRESHOLD_M = 15;

export function useLiveNavigation(steps: OSRMStep[]): LiveNavigationState {
  const [stepIdx, setStepIdx] = useState(0);
  const [currentPosition, setCurrentPosition] = useState<CurrentPosition | null>(null);
  const watchIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!navigator?.geolocation) return;

    watchIdRef.current = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude: lat, longitude: lon } = pos.coords;
        setCurrentPosition({ lat, lon });

        setStepIdx((prev) => {
          const currentStep = steps[prev];
          // Don't advance past last step or if no location on this step
          if (!currentStep || prev >= steps.length - 1) return prev;
          if (!currentStep.maneuver.location) return prev;

          // maneuver.location is [lon, lat] (GeoJSON convention)
          const [stepLon, stepLat] = currentStep.maneuver.location;
          const dist = haversineDistanceM(lat, lon, stepLat, stepLon);

          return dist < ADVANCE_THRESHOLD_M ? prev + 1 : prev;
        });
      },
      () => {
        // Silently ignore geolocation errors — navigation continues with last known position
      },
      { enableHighAccuracy: true, maximumAge: 0 },
    );

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
    };
  }, [steps]);

  return { stepIdx, currentPosition };
}
