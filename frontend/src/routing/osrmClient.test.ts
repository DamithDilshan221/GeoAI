import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchWalkingRoute } from './osrmClient';

const ORIGIN = { lat: 7.2545, lon: 80.5965 };
const DEST = { lat: 7.260, lon: 80.600 };

const MOCK_OSRM_RESPONSE = {
  routes: [
    {
      distance: 650.0,
      geometry: {
        coordinates: [
          [80.5965, 7.2545], // [lon, lat]
          [80.5980, 7.2560],
          [80.6000, 7.2600],
        ],
      },
      legs: [
        {
          steps: [
            { maneuver: { type: 'depart', modifier: undefined }, distance: 300 },
            { maneuver: { type: 'turn', modifier: 'right' }, distance: 350 },
            { maneuver: { type: 'arrive', modifier: undefined }, distance: 0 },
          ],
        },
      ],
    },
  ],
};

describe('fetchWalkingRoute — success', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      json: vi.fn().mockResolvedValue(MOCK_OSRM_RESPONSE),
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns source=network on success', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.source).toBe('network');
  });

  it('returns correct distanceM from OSRM', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.distanceM).toBe(650.0);
  });

  it('swaps [lon,lat] coordinates to [lat,lon]', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    // First coord in GeoJSON was [80.5965, 7.2545] → should become [7.2545, 80.5965]
    expect(result.path[0]).toEqual([7.2545, 80.5965]);
    expect(result.path[1]).toEqual([7.2560, 80.5980]);
    expect(result.path[2]).toEqual([7.2600, 80.6000]);
  });

  it('returns steps from the OSRM legs array', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.steps).toHaveLength(3);
    expect(result.steps[0].maneuver.type).toBe('depart');
  });
});

describe('fetchWalkingRoute — fallback', () => {
  beforeEach(() => {
    // Simulate network failure
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns source=straight_line_estimate on failure', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.source).toBe('straight_line_estimate');
  });

  it('returns exactly two steps: depart then arrive (prototype shape)', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.steps).toHaveLength(2);
    expect(result.steps[0].maneuver.type).toBe('depart');
    expect(result.steps[1].maneuver.type).toBe('arrive');
  });

  it('fallback path has two points — origin and dest', async () => {
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.path).toHaveLength(2);
    expect(result.path[0]).toEqual([ORIGIN.lat, ORIGIN.lon]);
    expect(result.path[1]).toEqual([DEST.lat, DEST.lon]);
  });

  it('also falls back when OSRM returns empty routes array', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      json: vi.fn().mockResolvedValue({ routes: [] }),
    }));
    const result = await fetchWalkingRoute(ORIGIN, DEST);
    expect(result.source).toBe('straight_line_estimate');
  });
});
