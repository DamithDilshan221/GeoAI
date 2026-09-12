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

let currentMapInstance: unknown = null;

export const MapContainer = vi.fn(({ children, center, zoom, className, ...props }) => {
  // Use useMemo so the mock instance is stable across renders
  const mapInstance = React.useMemo(() => {
    const inst = {
      fitBounds: vi.fn(),
      invalidateSize: vi.fn(),
    };
    mockInstances.maps.push(inst);
    return inst;
  }, []);

  currentMapInstance = mapInstance;

  const propRef = props.ref;
  React.useEffect(() => {
    if (propRef) {
      if (typeof propRef === 'function') {
        propRef(mapInstance);
      } else {
        propRef.current = mapInstance;
      }
    }
  }, [mapInstance, propRef]);

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

export const useMap = vi.fn(() => currentMapInstance || mockInstances.maps[mockInstances.maps.length - 1] || { fitBounds: vi.fn() });

export const Polyline = vi.fn(({ positions, pathOptions, children }) => (
  <div
    data-testid="polyline"
    data-positions={JSON.stringify(positions)}
    data-color={pathOptions?.color}
  >
    {children}
  </div>
));

