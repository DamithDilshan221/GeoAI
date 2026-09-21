/**
 * Browser-side OSRM walking route client.
 *
 * Calls OSRM directly from the browser per §17.1 — no backend proxy.
 * Requests steps=true (unlike the backend client, which doesn't need them).
 * Falls back to a two-step synthetic route on any failure, matching
 * pera-rest-nav.html's own fallback branch exactly.
 */

import { OSRM_BASE_URL, PUBLIC_OSRM_FALLBACK_URLS } from '../constants/map';
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

async function tryFetchRoute(
  baseUrl: string,
  origin: { lat: number; lon: number },
  dest: { lat: number; lon: number },
): Promise<RouteFetchResult | null> {
  try {
    const url =
      `${baseUrl}/route/v1/foot/` +
      `${origin.lon},${origin.lat};${dest.lon},${dest.lat}` +
      `?overview=full&geometries=geojson&steps=true`;

    const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), 4000) : null;

    const res = await fetch(url, controller ? { signal: controller.signal } : undefined);
    if (timeoutId) clearTimeout(timeoutId);

    if (res.ok === false) return null;

    const data: {
      routes?: Array<{
        distance: number;
        geometry: { coordinates: [number, number][] };
        legs: Array<{ steps: OSRMStep[] }>;
      }>;
    } = await res.json();

    const route = data.routes?.[0];
    if (!route || !route.geometry?.coordinates?.length || !route.legs?.[0]?.steps) {
      return null;
    }

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
  const candidateUrls = [
    OSRM_BASE_URL,
    ...PUBLIC_OSRM_FALLBACK_URLS.filter((url) => url !== OSRM_BASE_URL),
  ];

  for (const url of candidateUrls) {
    const result = await tryFetchRoute(url, origin, dest);
    if (result) {
      return result;
    }
  }

  // OSRM-unavailable fallback — two synthetic steps, matching prototype §22.1
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

