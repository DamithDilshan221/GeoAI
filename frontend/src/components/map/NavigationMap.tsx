/**
 * NavigationMap — a dedicated navigation map component.
 *
 * Separate from MapView per §10.2's folder structure listing them as two distinct
 * components. Reuses mapMarkerFactory icons and MapView's fitBounds approach.
 *
 * Renders:
 *  - Teal dashed Polyline for the walking path (prototype style: color #3FCBBE,
 *    weight 5, opacity 0.95, dashArray "1 10")
 *  - Destination facility marker via buildFacilityDivIcon
 *  - Live user-position marker via buildUserLocationDivIcon
 *  - Fits view to path bounds whenever path changes
 */

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Tooltip, ZoomControl, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { buildFacilityDivIcon, buildUserLocationDivIcon } from './mapMarkerFactory';
import { useMapTheme } from '../../hooks/useMapTheme';
import { MapThemeSwitcher } from './MapThemeSwitcher';

export interface NavigationMapProps {
  path: [number, number][];
  userPosition: { lat: number; lon: number } | null;
  destination: {
    lat: number;
    lon: number;
    name: string;
    category?: string;
  };
  showThemeSwitcher?: boolean;
}

function FitRoute({ path }: { path: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (path.length === 0) return;
    map.fitBounds(L.latLngBounds(path), { padding: [40, 40], maxZoom: 18 });
  }, [path, map]);
  return null;
}

export function NavigationMap({
  path,
  userPosition,
  destination,
  showThemeSwitcher = true,
}: NavigationMapProps) {
  const { themeId, activeTheme, setTheme, availableThemes } = useMapTheme();
  // Default center to destination while route loads
  const center: [number, number] = [destination.lat, destination.lon];

  return (
    <div className="w-full h-full relative" data-testid="navigation-map-wrapper">
      {showThemeSwitcher && (
        <MapThemeSwitcher
          currentThemeId={themeId}
          availableThemes={availableThemes}
          onSelectTheme={setTheme}
        />
      )}
      <MapContainer
        center={center}
        zoom={16}
        zoomControl={false}
        className="h-full w-full"
      >
        <ZoomControl position="bottomleft" />
        <TileLayer
          key={activeTheme.id}
          url={activeTheme.url}
          attribution={activeTheme.attribution}
          subdomains={activeTheme.subdomains || 'abc'}
          maxZoom={activeTheme.maxZoom || 19}
        />
        <FitRoute path={path} />

        {/* Walking route polyline — teal dashed, matching prototype */}
        {path.length > 1 && (
          <Polyline
            positions={path}
            pathOptions={{
              color: '#3FCBBE',
              weight: 5,
              opacity: 0.95,
              dashArray: '1 10',
            }}
          />
        )}

        {/* Destination marker */}
        <Marker
          position={[destination.lat, destination.lon]}
          icon={buildFacilityDivIcon(destination.category)}
        >
          <Tooltip direction="top" offset={[0, -26]}>
            {destination.name}
          </Tooltip>
        </Marker>

        {/* Live user position */}
        {userPosition && (
          <Marker
            position={[userPosition.lat, userPosition.lon]}
            icon={buildUserLocationDivIcon()}
          >
            <Tooltip permanent direction="top" offset={[0, -6]} className="you-label">
              You
            </Tooltip>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
