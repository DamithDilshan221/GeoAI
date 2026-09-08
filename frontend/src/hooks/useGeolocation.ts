import { useState, useCallback } from 'react';

export const GEOLOCATION_MESSAGES = {
  denied: 'Unable to access your location. Please enable location permissions and try again.',
  unavailable: 'Your location could not be determined. Please try again.',
} as const;

type GeolocationStatus = 'idle' | 'requesting' | 'granted' | 'denied' | 'unavailable';

export function useGeolocation() {
  const [status, setStatus] = useState<GeolocationStatus>('idle');
  const [location, setLocation] = useState<{lat: number; lon: number; accuracy: number} | null>(null);

  const request = useCallback(() => {
    setStatus('requesting');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude, accuracy: pos.coords.accuracy });
        setStatus('granted');
      },
      (err) => {
        setStatus(err.code === 1 ? 'denied' : 'unavailable');
      },
      { timeout: 10000 }
    );
  }, []);

  const errorMessage = status === 'denied' ? GEOLOCATION_MESSAGES.denied
    : status === 'unavailable' ? GEOLOCATION_MESSAGES.unavailable
    : null;

  return { status, location, errorMessage, request };
}
