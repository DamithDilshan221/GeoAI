/**
 * Haversine great-circle distance between two lat/lon points, in metres.
 *
 * Ported verbatim from pera-rest-nav.html's `distanceMeters` function.
 * Earth radius: 6 371 000 m (matches the backend's own estimate_distance_m).
 *
 * Frontend usage: OSRM-unavailable fallback only. Never use this for anything
 * the backend already authoritatively computes (§13.4).
 */
export function haversineDistanceM(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 6_371_000;
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}
