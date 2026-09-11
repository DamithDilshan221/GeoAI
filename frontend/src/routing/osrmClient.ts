/**
 * Browser-side OSRM walking route client.
 *
 * Calls OSRM directly from the browser per §17.1 — no backend proxy.
 * Requests steps=true (unlike the backend client, which doesn't need them).
 * Falls back to a two-step synthetic route on any failure, matching
 * pera-rest-nav.html's own fallback branch exactly.
 */

import { OSRM_BASE_URL } from '../constants/map';
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

export async function fetchWalkingRoute(
  origin: { lat: number; lon: number },
  dest: { lat: number; lon: number },
): Promise<RouteFetchResult> {
  try {
    const url =
      `${OSRM_BASE_URL}/route/v1/foot/` +
      `${origin.lon},${origin.lat};${dest.lon},${dest.lat}` +
      `?overview=full&geometries=geojson&steps=true`;

    const res = await fetch(url);
    const data: {
      routes?: Array<{
        distance: number;
        geometry: { coordinates: [number, number][] };
        legs: Array<{ steps: OSRMStep[] }>;
      }>;
    } = await res.json();

    const route = data.routes?.[0];
    if (!route) throw new Error('no route');

    return {
      steps: route.legs[0].steps,
      // Swap [lon, lat] → [lat, lon]
      path: route.geometry.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]),
      distanceM: route.distance,
      source: 'network',
    };
  } catch {
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
}
