import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NavigationMap } from './NavigationMap';
import { mockInstances, setupLeafletMock, resetLeafletMock } from '../../test-utils/leafletMock';
import { buildFacilityDivIcon, buildUserLocationDivIcon } from './mapMarkerFactory';

vi.mock('react-leaflet', () => import('../../test-utils/leafletMock'));

const DEST = { lat: 7.260, lon: 80.600, name: 'North Wing WC', category: 'male' };
const PATH: [number, number][] = [
  [7.2545, 80.5965],
  [7.2560, 80.5980],
  [7.2600, 80.6000],
];
const USER_POS = { lat: 7.2545, lon: 80.5965 };

describe('NavigationMap', () => {
  beforeEach(() => {
    setupLeafletMock();
    vi.clearAllMocks();
  });

  afterEach(() => {
    resetLeafletMock();
  });

  it('renders map container', () => {
    render(<NavigationMap path={PATH} userPosition={null} destination={DEST} />);
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });

  it('renders OSM tile layer', () => {
    render(<NavigationMap path={PATH} userPosition={null} destination={DEST} />);
    const tile = screen.getByTestId('tile-layer');
    expect(tile.getAttribute('data-url')).toContain('tile.openstreetmap.org');
  });

  it('renders a Polyline when path has multiple points', () => {
    render(<NavigationMap path={PATH} userPosition={null} destination={DEST} />);
    expect(screen.getByTestId('polyline')).toBeInTheDocument();
  });

  it('does not render Polyline when path has fewer than 2 points', () => {
    render(<NavigationMap path={[[7.2545, 80.5965]]} userPosition={null} destination={DEST} />);
    expect(screen.queryByTestId('polyline')).not.toBeInTheDocument();
  });

  it('renders destination marker with correct icon', () => {
    render(<NavigationMap path={PATH} userPosition={null} destination={DEST} />);
    const destMarker = mockInstances.markers.find(
      (m: unknown) => (m as { position: number[] }).position[0] === DEST.lat &&
        (m as { position: number[] }).position[1] === DEST.lon,
    );
    expect(destMarker).toBeDefined();
    expect((destMarker as { icon: unknown }).icon).toEqual(buildFacilityDivIcon(DEST.category));
  });

  it('renders user position marker when provided', () => {
    render(<NavigationMap path={PATH} userPosition={USER_POS} destination={DEST} />);
    const userMarker = mockInstances.markers.find(
      (m: unknown) => (m as { position: number[] }).position[0] === USER_POS.lat &&
        (m as { position: number[] }).position[1] === USER_POS.lon,
    );
    expect(userMarker).toBeDefined();
    expect((userMarker as { icon: unknown }).icon).toEqual(buildUserLocationDivIcon());
  });

  it('does not render user marker when userPosition is null', () => {
    render(<NavigationMap path={PATH} userPosition={null} destination={DEST} />);
    // Only destination marker should exist
    expect(mockInstances.markers).toHaveLength(1);
  });
});
