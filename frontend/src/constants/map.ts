export interface MapThemeOption {
  id: string;
  name: string;
  category: 'street' | 'dark' | 'light' | 'satellite' | 'terrain';
  url: string;
  attribution: string;
  subdomains?: string[];
  maxZoom?: number;
  previewColor: string;
  description: string;
}

export const OSM_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
export const OSM_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

export const MAP_THEMES: Record<string, MapThemeOption> = {
  osm: {
    id: 'osm',
    name: 'OpenStreetMap Standard',
    category: 'street',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    previewColor: '#79c47e',
    description: 'Detailed OpenStreetMap street map with campus building footprints and roads',
  },
  satellite: {
    id: 'satellite',
    name: 'Satellite Aerial',
    category: 'satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution:
      'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP',
    maxZoom: 18,
    previewColor: '#364935',
    description: 'High-resolution aerial satellite imagery of Peradeniya campus and surroundings',
  },
  humanitarian: {
    id: 'humanitarian',
    name: 'Humanitarian HOT',
    category: 'street',
    url: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles by HOT',
    maxZoom: 19,
    previewColor: '#d66a6a',
    description: 'Accessibility-focused OpenStreetMap style highlighting paths and amenities',
  },
  'esri-dark': {
    id: 'esri-dark',
    name: 'Night Dark Canvas',
    category: 'dark',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16,
    previewColor: '#1a1f2c',
    description: 'Clean high-contrast dark basemap tailored for night navigation and marker pop',
  },
  'esri-light': {
    id: 'esri-light',
    name: 'Clean Light Canvas',
    category: 'light',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16,
    previewColor: '#e9edf0',
    description: 'Minimalist neutral light map with crisp roads and un-cluttered labels',
  },
  'esri-street': {
    id: 'esri-street',
    name: 'World Street Map',
    category: 'street',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS',
    maxZoom: 19,
    previewColor: '#5eb3d6',
    description: 'Rich topographic street map with detailed campus geography',
  },
  topo: {
    id: 'topo',
    name: 'OpenTopo Terrain',
    category: 'terrain',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution:
      'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
    maxZoom: 17,
    previewColor: '#c8ba95',
    description: 'Topographic contour lines, elevation shading, and hillside trails',
  },
};

export const DEFAULT_MAP_THEME_ID = 'osm';

// Public OSRM demo endpoint (MVP). Replace with self-hosted URL in production (§14.3 / Phase 19).
export const OSRM_BASE_URL = 'https://router.project-osrm.org';

