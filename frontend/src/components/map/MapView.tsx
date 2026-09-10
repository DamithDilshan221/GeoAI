import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Tooltip, ZoomControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { Map as LeafletMap } from 'leaflet';
import { buildFacilityDivIcon, buildUserLocationDivIcon } from './mapMarkerFactory';
import { OSM_TILE_URL, OSM_ATTRIBUTION } from '../../constants/map';

export interface MapMarkerData {
  id: number;
  lat: number;
  lon: number;
  title: string;
  category?: string;
}

export interface MapViewProps {
  markers: MapMarkerData[];
  userLocation: { lat: number; lon: number } | null;
  onMarkerClick?: (facilityId: number) => void;
  onMapReady?: (map: LeafletMap) => void;
  className?: string;
}

function FitBounds({ markers, userLocation }: Pick<MapViewProps, 'markers' | 'userLocation'>) {
  const map = useMap();
  useEffect(() => {
    const points: [number, number][] = markers.map((m) => [m.lat, m.lon]);
    if (userLocation) points.push([userLocation.lat, userLocation.lon]);
    if (points.length === 0) return;
    map.fitBounds(L.latLngBounds(points), { padding: [40, 40], maxZoom: 18 });
  }, [markers, userLocation, map]);
  return null;
}

export function MapView({ markers, userLocation, onMarkerClick, onMapReady, className = '' }: MapViewProps) {
  return (
    <div className={`relative ${className || 'h-64 w-full'}`}>
      <MapContainer
        center={[0, 0]}
        zoom={2}
        zoomControl={false}
        className="h-full w-full rounded-lg overflow-hidden"
        ref={onMapReady}
      >
        <ZoomControl position="bottomleft" />
        <TileLayer url={OSM_TILE_URL} attribution={OSM_ATTRIBUTION} />
        <FitBounds markers={markers} userLocation={userLocation} />
        {userLocation && (
          <Marker position={[userLocation.lat, userLocation.lon]} icon={buildUserLocationDivIcon()}>
            <Tooltip permanent direction="top" offset={[0, -6]} className="you-label">You</Tooltip>
          </Marker>
        )}
        {markers.map((m) => (
          <Marker
            key={m.id}
            position={[m.lat, m.lon]}
            icon={buildFacilityDivIcon(m.category)}
            eventHandlers={{ click: () => onMarkerClick?.(m.id) }}
          >
            <Tooltip direction="top" offset={[0, -26]}>{m.title}</Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
