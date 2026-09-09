import React, { useEffect, useRef, useState } from 'react';
import { loadMapsLibrary, loadMarkerLibrary } from '../../lib/googleMapsLoader';
import { LoadingState } from '../status/LoadingState';
import { ErrorState } from '../status/ErrorState';
import {
  buildFacilityPin,
  buildUserLocationPin,
  buildFacilityInfoWindowContent,
} from './mapMarkerFactory';

interface MapMarkerData {
  id: number;
  lat: number;
  lon: number;
  title: string;
  category?: string;
}

interface MapViewProps {
  markers: MapMarkerData[];
  userLocation: { lat: number; lon: number } | null;
  onMarkerClick?: (facilityId: number) => void;
  onMapReady?: (map: google.maps.Map) => void;
  className?: string;
}

export function MapView({
  markers,
  userLocation,
  onMarkerClick,
  onMapReady,
  className = '',
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  // Effect A: Load Map
  useEffect(() => {
    let isMounted = true;

    async function initMap() {
      try {
        const [mapsLib] = await Promise.all([
          loadMapsLibrary(),
          loadMarkerLibrary(),
        ]);

        if (!isMounted) return;
        if (!containerRef.current) return;

        const map = new mapsLib.Map(containerRef.current, {
          mapId: 'DEMO_MAP_ID',
          center: { lat: 0, lng: 0 },
          zoom: 2,
        });

        mapRef.current = map;
        infoWindowRef.current = new mapsLib.InfoWindow();
        setStatus('ready');
        onMapReady?.(map);
      } catch (err) {
        console.error('Failed to load Google Maps:', err);
        if (isMounted) setStatus('error');
      }
    }

    initMap();

    return () => {
      isMounted = false;
      // Cleanup all markers on unmount
      markersRef.current.forEach((m) => {
        m.map = null;
      });
      markersRef.current = [];
    };
  }, [onMapReady]);

  // Effect B: Sync Data
  useEffect(() => {
    if (status !== 'ready' || !mapRef.current) return;

    const map = mapRef.current;

    // Clear old markers
    markersRef.current.forEach((m) => {
      m.map = null;
    });
    markersRef.current = [];

    const bounds = new google.maps.LatLngBounds();
    let hasPoints = false;

    // Add user location marker
    if (userLocation) {
      const pin = buildUserLocationPin(google.maps.marker.PinElement);
      const userMarker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: { lat: userLocation.lat, lng: userLocation.lon },
        content: pin.element,
        title: 'Your Location',
      });
      markersRef.current.push(userMarker);
      bounds.extend({ lat: userLocation.lat, lng: userLocation.lon });
      hasPoints = true;
    }

    // Add facility markers
    markers.forEach((markerData) => {
      const pin = buildFacilityPin(google.maps.marker.PinElement, markerData.category);
      const facilityMarker = new google.maps.marker.AdvancedMarkerElement({
        map,
        position: { lat: markerData.lat, lng: markerData.lon },
        content: pin.element,
        title: markerData.title,
        gmpClickable: true,
      });

      facilityMarker.addEventListener('gmp-click', () => {
        if (infoWindowRef.current) {
          const content = buildFacilityInfoWindowContent(markerData.title, () => {
            onMarkerClick?.(markerData.id);
          });
          infoWindowRef.current.setContent(content);
          infoWindowRef.current.open({
            anchor: facilityMarker,
            map,
          });
        }
      });

      markersRef.current.push(facilityMarker);
      bounds.extend({ lat: markerData.lat, lng: markerData.lon });
      hasPoints = true;
    });

    if (hasPoints) {
      map.fitBounds(bounds);
      google.maps.event.addListenerOnce(map, 'idle', () => {
        if (map.getZoom()! > 18) {
          map.setZoom(18);
        }
      });
    }
  }, [status, markers, userLocation, onMarkerClick]);

  if (status === 'error') {
    return <ErrorState message="Map unavailable — showing list only" />;
  }

  // MUST have a height to render map tiles. Using the passed className or a default.
  return (
    <div className={`relative ${className || 'h-64 w-full'}`}>
      {status === 'loading' && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-slate-900/50 rounded-lg">
          <LoadingState message="Loading map..." />
        </div>
      )}
      <div
        ref={containerRef}
        className="h-full w-full rounded-lg overflow-hidden bg-slate-800"
      />
    </div>
  );
}
