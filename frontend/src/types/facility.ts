export interface Washroom {
  id: number;
  name: string;
  location_name: string;
  category: string;
  audience: 'VISITOR' | 'STAFF';
  status: 'OPEN' | 'CLOSED' | 'TEMPORARILY_UNAVAILABLE';
  status_updated_at: string;
  rating: number | null;
  fixtures: { attached?: number; normal?: number; shower?: number; sink?: number; mirror?: number };
  total_stalls: number;
  data_source: 'REAL' | 'PUBLIC' | 'SYNTHETIC';
  latitude: number;
  longitude: number;
}

export interface FacilityListResponse {
  items: Washroom[];
  limit: number;
  offset: number;
  total: number;
}

export interface NearbyWashroom {
  id: number;
  name: string;
  category: string;
  audience: 'VISITOR' | 'STAFF';
  status: Washroom['status'];
  rating: number | null;
  fixtures: Washroom['fixtures'];
  distance_m: number;
  latitude: number;
  longitude: number;
}
