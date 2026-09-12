import { vi } from 'vitest';

export const mockInstances = {
  maps: [] as unknown[],
  markers: [] as unknown[],
};

export function setupLeafletMock() {
  mockInstances.maps = [];
  mockInstances.markers = [];
}

export function resetLeafletMock() {
  mockInstances.maps = [];
  mockInstances.markers = [];
}

import React from 'react';

export const MapContainer = vi.fn(({ children, center, zoom, className, ...props }) => {
  // Use useMemo so the mock instance is stable across renders
  const mapInstance = React.useMemo(() => ({
    fitBounds: vi.fn(),
    invalidateSize: vi.fn(),
  }), []);

  React.useEffect(() => {
    mockInstances.maps.push(mapInstance);
    if (props.ref) {
      if (typeof props.ref === 'function') {
        props.ref(mapInstance);
      } else {
        props.ref.current = mapInstance;
      }
    }
  }, [mapInstance, props.ref]);

  return (
    <div data-testid="map-container" className={className} data-center={JSON.stringify(center)} data-zoom={zoom}>
      {children}
    </div>
  );
});

export const TileLayer = vi.fn(({ url, attribution }) => (
  <div data-testid="tile-layer" data-url={url} data-attribution={attribution} />
));

export const Marker = vi.fn(({ position, icon, eventHandlers, children }) => {
  mockInstances.markers.push({ position, icon, eventHandlers });
  return (
    <div data-testid="marker" data-position={JSON.stringify(position)}>
      {children}
    </div>
  );
});

export const Tooltip = vi.fn(({ className, children }) => (
  <div data-testid="tooltip" className={className}>
    {children}
  </div>
));

export const ZoomControl = vi.fn(({ position }) => (
  <div data-testid="zoom-control" data-position={position} />
));

export const useMap = vi.fn(() => mockInstances.maps[mockInstances.maps.length - 1] || { fitBounds: vi.fn() });

export const Polyline = vi.fn(({ positions, pathOptions, children }) => (
  <div
    data-testid="polyline"
    data-positions={JSON.stringify(positions)}
    data-color={pathOptions?.color}
  >
    {children}
  </div>
));

