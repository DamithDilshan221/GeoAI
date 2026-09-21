/**
 * Browser-side OSRM walking route client.
 *
 * Calls OSRM directly from the browser per §17.1 — no backend proxy.
 * Requests steps=true (unlike the backend client, which doesn't need them).
 * Attempts the primary configured OSRM server first, falls back to the public
 * OSRM demo server if local is unreachable, and falls back to a two-step
 * synthetic route on total failure.
 */

import { OSRM_BASE_URL, PUBLIC_OSRM_BASE_URL } from '../constants/map';
import { haversineDistanceM } from '../utils/geo';
import type { OSRMStep } from './maneuvers';

export type { OSRMStep };

export interface RouteFetchResult {
  steps: OSRMStep[];
  /** (lat, lon) pairs in order — GeoJSON coordinates are swapped on parse */
  path: [number, number][];
  distanceM: number;
  source: 'network' | 'straight_line_estimate';
}

async function requestRoute(
  baseUrl: string,
  origin: { lat: number; lon: number },
  dest: { lat: number; lon: number },
): Promise<RouteFetchResult | null> {
  try {
    const url =
      `${baseUrl}/route/v1/foot/` +
      `${origin.lon},${origin.lat};${dest.lon},${dest.lat}` +
      `?overview=full&geometries=geojson&steps=true`;

    const res = await fetch(url);
    if (res.ok === false) return null;

    const data: {
      routes?: Array<{
        distance: number;
        geometry: { coordinates: [number, number][] };
        legs: Array<{ steps: OSRMStep[] }>;
      }>;
    } = await res.json();

    const route = data.routes?.[0];
    if (!route || !route.legs?.[0]?.steps) return null;

    return {
      steps: route.legs[0].steps,
      // Swap [lon, lat] → [lat, lon]
      path: route.geometry.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]),
      distanceM: route.distance,
      source: 'network',
    };
  } catch {
    return null;
  }
}

export async function fetchWalkingRoute(
  origin: { lat: number; lon: number },
  dest: { lat: number; lon: number },
): Promise<RouteFetchResult> {
  // 1. Try configured local OSRM endpoint
  const localResult = await requestRoute(OSRM_BASE_URL, origin, dest);
  if (localResult) return localResult;

  // 2. Fall back to public demo OSRM if local OSRM is unreachable
  if (PUBLIC_OSRM_BASE_URL && PUBLIC_OSRM_BASE_URL !== OSRM_BASE_URL) {
    const publicResult = await requestRoute(PUBLIC_OSRM_BASE_URL, origin, dest);
    if (publicResult) return publicResult;
  }

  // 3. Fall back to two-step synthetic route on total network failure
  const distanceM = haversineDistanceM(origin.lat, origin.lon, dest.lat, dest.lon);
  return {
    steps: [
      { maneuver: { type: 'depart' }, distance: distanceM },
      { maneuver: { type: 'arrive' }, distance: 0 },
    ],
    path: [
      [origin.lat, origin.lon],
      [dest.lat, dest.lon],
    ],
    distanceM,
    source: 'straight_line_estimate',
  };
}
