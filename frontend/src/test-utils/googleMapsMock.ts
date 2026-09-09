/* eslint-disable @typescript-eslint/no-explicit-any */
import { vi } from 'vitest';

export const mockInstances = {
  maps: [] as any[],
  markers: [] as any[],
  bounds: [] as any[],
};

class FakeMap {
  options: google.maps.MapOptions;
  zoom: number;

  constructor(element: HTMLElement, options: google.maps.MapOptions) {
    this.options = options;
    this.zoom = options.zoom || 0;
    mockInstances.maps.push(this);
  }
  fitBounds = vi.fn();
  getZoom = vi.fn(() => this.zoom);
  setZoom = vi.fn((z) => {
    this.zoom = z;
  });
}

class FakeLatLngBounds {
  constructor() {
    mockInstances.bounds.push(this);
  }
  extend = vi.fn().mockReturnThis();
}

class FakeAdvancedMarkerElement {
  map: any;
  addEventListener = vi.fn();
  constructor(public options: any) {
    this.map = options.map;
    mockInstances.markers.push(this);
  }
}

class FakePinElement {
  constructor(public options: any) {}
  get element() { return document.createElement('div'); }
}

class FakeInfoWindow {
  open = vi.fn();
  setContent = vi.fn();
  close = vi.fn();
}

const fakeAddListenerOnce = vi.fn((instance, eventName, handler) => {
  if (eventName === 'idle') {
    handler();
  }
});

export const setupGoogleMapsMock = () => {
  mockInstances.maps = [];
  mockInstances.markers = [];
  mockInstances.bounds = [];

  global.google = {
    maps: {
      Map: FakeMap,
      LatLngBounds: FakeLatLngBounds,
      InfoWindow: FakeInfoWindow,
      event: {
        addListenerOnce: fakeAddListenerOnce,
      },
      marker: {
        AdvancedMarkerElement: FakeAdvancedMarkerElement,
        PinElement: FakePinElement,
      },
    } as any,
  };
};

export const resetGoogleMapsMock = () => {
  vi.restoreAllMocks();
  delete (global as any).google;
};
