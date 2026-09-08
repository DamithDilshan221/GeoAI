export interface Facility {
  id: number;
  name: string;
  category: string;
  status: 'OPEN' | 'CLOSED' | 'TEMPORARILY_UNAVAILABLE';
  status_updated_at: string;
  rating: number | null;
  capacity: number | null;
  accessibility: { wheelchair_friendly?: boolean; [key: string]: unknown } | null;
  data_source: 'REAL' | 'PUBLIC' | 'SYNTHETIC';
  latitude: number;
  longitude: number;
}
export interface FacilityListResponse {
  items: Facility[];
  limit: number;
  offset: number;
  total: number;
}
export interface NearbyFacility {
  id: number;
  name: string;
  category: string;
  status: Facility['status'];
  rating: number | null;
  distance_m: number;
  latitude: number;
  longitude: number;
}
