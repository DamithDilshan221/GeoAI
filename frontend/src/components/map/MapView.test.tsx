/* eslint-disable @typescript-eslint/no-explicit-any */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MapView } from './MapView';
import { mockInstances, setupLeafletMock, resetLeafletMock } from '../../test-utils/leafletMock';
import { buildFacilityDivIcon, buildUserLocationDivIcon } from './mapMarkerFactory';

vi.mock('react-leaflet', () => import('../../test-utils/leafletMock'));

describe('MapView', () => {
  const mockMarkers = [
    { id: 1, lat: 40.7128, lon: -74.006, title: 'Facility 1', category: 'male' },
    { id: 2, lat: 40.7129, lon: -74.007, title: 'Facility 2', category: 'female' },
  ];
  const mockUserLoc = { lat: 40.7125, lon: -74.005 };

  beforeEach(() => {
    setupLeafletMock();
    vi.clearAllMocks();
  });

  afterEach(() => {
    resetLeafletMock();
  });

  it('renders a map container with TileLayer including required OSM attribution', () => {
    render(<MapView markers={[]} userLocation={null} />);
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();

    const tileLayer = screen.getByTestId('tile-layer');
    expect(tileLayer).toBeInTheDocument();
    expect(tileLayer.getAttribute('data-url')).toContain('tile.openstreetmap.org');
    
    const attribution = tileLayer.getAttribute('data-attribution');
    expect(attribution).toContain('OpenStreetMap');
    expect(attribution).toContain('contributors');
  });

  it('renders correct number of markers including user location', () => {
    render(<MapView markers={mockMarkers} userLocation={mockUserLoc} />);
    // 2 facility markers + 1 user location marker
    expect(mockInstances.markers).toHaveLength(3);
    
    // User location marker should be rendered
    const userMarkerRender = mockInstances.markers.find(m => 
      m.position[0] === mockUserLoc.lat && m.position[1] === mockUserLoc.lon
    );
    expect(userMarkerRender).toBeDefined();
    expect(userMarkerRender?.icon).toEqual(buildUserLocationDivIcon());
  });

  it('facility markers use correct icons from factory', () => {
    render(<MapView markers={mockMarkers} userLocation={null} />);
    expect(mockInstances.markers).toHaveLength(2);

    expect(mockInstances.markers[0].icon).toEqual(buildFacilityDivIcon('male'));
    expect(mockInstances.markers[1].icon).toEqual(buildFacilityDivIcon('female'));
  });

  it('invoking a marker click event calls onMarkerClick', () => {
    const onMarkerClick = vi.fn();
    render(<MapView markers={mockMarkers} userLocation={null} onMarkerClick={onMarkerClick} />);
    
    // Trigger click on the first marker
    mockInstances.markers[0].eventHandlers.click();
    expect(onMarkerClick).toHaveBeenCalledWith(1);
    expect(onMarkerClick).toHaveBeenCalledTimes(1);
  });

  it('calls fitBounds with { maxZoom: 18 } when markers are present', () => {
    render(<MapView markers={[mockMarkers[0]]} userLocation={null} />);
    const map = mockInstances.maps[0];
    
    expect(map.fitBounds).toHaveBeenCalled();
    const boundsCallArgs = map.fitBounds.mock.calls[0];
    expect(boundsCallArgs[1]).toMatchObject({ maxZoom: 18 });
  });

  it('does not call fitBounds when no markers and no userLocation exist', () => {
    render(<MapView markers={[]} userLocation={null} />);
    const map = mockInstances.maps[0];
    expect(map.fitBounds).not.toHaveBeenCalled();
  });
});
