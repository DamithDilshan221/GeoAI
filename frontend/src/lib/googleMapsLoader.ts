/* eslint-disable @typescript-eslint/no-explicit-any */
import { importLibrary } from '@googlemaps/js-api-loader';

const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

if (!apiKey) {
  console.warn('VITE_GOOGLE_MAPS_API_KEY is not set. Google Maps may not load correctly.');
}

const mapOptions = {
  key: apiKey || '',
  v: 'weekly',
};

let mapsLibraryPromise: Promise<google.maps.MapsLibrary> | null = null;
let markerLibraryPromise: Promise<google.maps.MarkerLibrary> | null = null;

export function loadMapsLibrary() {
  if (!mapsLibraryPromise) {
    // Inject key dynamically and import
    (window as any).__googleMapsLoaderOptions = mapOptions;
    mapsLibraryPromise = importLibrary('maps', mapOptions) as Promise<google.maps.MapsLibrary>;
  }
  return mapsLibraryPromise;
}

export function loadMarkerLibrary() {
  if (!markerLibraryPromise) {
    markerLibraryPromise = importLibrary('marker', mapOptions) as Promise<google.maps.MarkerLibrary>;
  }
  return markerLibraryPromise;
}
