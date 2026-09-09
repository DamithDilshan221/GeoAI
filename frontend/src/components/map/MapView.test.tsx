/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MapView } from './MapView';
import { setupGoogleMapsMock, resetGoogleMapsMock, mockInstances } from '../../test-utils/googleMapsMock';

vi.mock('../../lib/googleMapsLoader', () => ({
  loadMapsLibrary: vi.fn(),
  loadMarkerLibrary: vi.fn(),
}));

import * as loaderModule from '../../lib/googleMapsLoader';

describe('MapView', () => {
  beforeEach(() => {
    setupGoogleMapsMock();
    vi.mocked(loaderModule.loadMapsLibrary).mockResolvedValue(global.google.maps as any);
    vi.mocked(loaderModule.loadMarkerLibrary).mockResolvedValue(global.google.maps.marker as any);
  });

  afterEach(() => {
    resetGoogleMapsMock();
    vi.clearAllMocks();
  });

  const mockMarkers = [
    { id: 1, lat: 10, lon: 20, title: 'Facility 1' },
    { id: 2, lat: 30, lon: 40, title: 'Facility 2' },
  ];

  it('renders Map with DEMO_MAP_ID and creates markers', async () => {
    render(<MapView markers={mockMarkers} userLocation={{ lat: 0, lon: 0 }} />);

    await waitFor(() => {
      expect(mockInstances.maps.length).toBe(1);
    });

    const mapInstance = mockInstances.maps[0];
    expect(mapInstance.options.mapId).toBe('DEMO_MAP_ID');

    expect(mockInstances.markers.length).toBe(3);
  });

  it('handles zoom cap after fitBounds for single marker', async () => {
    render(<MapView markers={[mockMarkers[0]]} userLocation={null} />);

    await waitFor(() => {
      expect(mockInstances.maps.length).toBe(1);
      const mapInstance = mockInstances.maps[0];
      expect(mapInstance.fitBounds).toHaveBeenCalled();
    });
  });

  it('calls onMarkerClick when a facility marker is clicked', async () => {
    const onMarkerClick = vi.fn();
    render(<MapView markers={[mockMarkers[0]]} userLocation={null} onMarkerClick={onMarkerClick} />);

    await waitFor(() => {
      expect(mockInstances.markers.length).toBe(1);
    });

    const marker = mockInstances.markers[0];
    expect(marker.addEventListener).toHaveBeenCalledWith('gmp-click', expect.any(Function));

    const clickHandler = marker.addEventListener.mock.calls.find((call: any) => call[0] === 'gmp-click')[1];
    clickHandler();
  });

  it('re-renders clear previous markers before creating new ones', async () => {
    const { rerender } = render(<MapView markers={mockMarkers} userLocation={null} />);

    await waitFor(() => {
      expect(mockInstances.markers.length).toBe(2);
    });

    const initialMarkers = [...mockInstances.markers];

    rerender(<MapView markers={[]} userLocation={null} />);

    initialMarkers.forEach((m) => {
      expect(m.map).toBeNull();
    });
  });

  it('clears markers on unmount', async () => {
    const { unmount } = render(<MapView markers={mockMarkers} userLocation={null} />);

    await waitFor(() => {
      expect(mockInstances.markers.length).toBe(2);
    });

    const initialMarkers = [...mockInstances.markers];
    unmount();

    initialMarkers.forEach((m) => {
      expect(m.map).toBeNull();
    });
  });

  it('renders ErrorState when map loader fails', async () => {
    vi.mocked(loaderModule.loadMapsLibrary).mockRejectedValueOnce(new Error('Network error'));
    
    render(<MapView markers={mockMarkers} userLocation={null} />);
    
    await waitFor(() => {
      expect(screen.getByText('Map unavailable — showing list only')).toBeInTheDocument();
    });
  });
});
