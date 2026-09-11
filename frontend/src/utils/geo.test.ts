import { describe, it, expect } from 'vitest';
import { haversineDistanceM } from './geo';

describe('haversineDistanceM', () => {
  it('returns 0 for identical points', () => {
    expect(haversineDistanceM(7.2545, 80.5965, 7.2545, 80.5965)).toBe(0);
  });

  it('returns ~111 km for 1 degree latitude difference at equator', () => {
    const dist = haversineDistanceM(0, 0, 1, 0);
    expect(dist).toBeCloseTo(111_195, -2); // within 100 m
  });

  it('returns same result regardless of direction (symmetry)', () => {
    const a = haversineDistanceM(7.2545, 80.5965, 7.260, 80.600);
    const b = haversineDistanceM(7.260, 80.600, 7.2545, 80.5965);
    expect(a).toBeCloseTo(b, 5);
  });

  it('returns a positive number for two distinct campus points', () => {
    const dist = haversineDistanceM(7.2545, 80.5965, 7.260, 80.600);
    expect(dist).toBeGreaterThan(0);
    expect(dist).toBeLessThan(2000); // within campus scale
  });
});
