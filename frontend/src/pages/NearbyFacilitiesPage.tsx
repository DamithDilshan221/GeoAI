import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { EmptyState } from '../components/status/EmptyState';
import { FacilityList } from '../components/facility/FacilityList';
import { MapView } from '../components/map/MapView';
import { useNearbyFacilities } from '../hooks/useNearbyFacilities';
import { 
  DEFAULT_RADIUS_M, 
  MAX_RADIUS_M, 
  RADIUS_EXPAND_MULTIPLIER, 
  EMPTY_NEARBY_MESSAGE, 
  SERVICE_UNAVAILABLE_MESSAGE 
} from '../constants/search';

export function NearbyFacilitiesPage() {
  const { state } = useSearchContext();
  const [radiusM, setRadiusM] = useState(DEFAULT_RADIUS_M);
  const navigate = useNavigate();

  const { selectedCategory, location } = state;

  useEffect(() => {
    if (!selectedCategory || !location) {
      navigate('/', { replace: true });
    }
  }, [selectedCategory, location, navigate]);

  const { data, isLoading, isError, error, refetch } = useNearbyFacilities(
    selectedCategory && location
      ? { lat: location.lat, lon: location.lon, category: selectedCategory, radius_m: radiusM }
      : null
  );

  if (!selectedCategory || !location) {
    return null; // or <Navigate to="/" replace /> since useEffect handles it too
  }

  if (isLoading) {
    return <LoadingState message="Finding facilities near you..." />;
  }

  if (isError) {
    const is503 = (error as { response?: { status?: number } })?.response?.status === 503;
    const message = is503 
      ? SERVICE_UNAVAILABLE_MESSAGE 
      : 'An error occurred while fetching facilities.';
    return <ErrorState message={message} onRetry={refetch} />;
  }

  if (data && data.length === 0) {
    const atMaxRadius = radiusM >= MAX_RADIUS_M;
    return (
      <EmptyState message={EMPTY_NEARBY_MESSAGE}>
        <button
          disabled={atMaxRadius}
          onClick={() => setRadiusM(prev => Math.min(prev * RADIUS_EXPAND_MULTIPLIER, MAX_RADIUS_M))}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            atMaxRadius 
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-500'
          }`}
        >
          Search wider area
        </button>
      </EmptyState>
    );
  }

  const mapMarkers = (data || []).map(f => ({
    id: f.id,
    lat: f.latitude,
    lon: f.longitude,
    title: f.name
  }));

  const userLocation = { lat: location.lat, lon: location.lon };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Nearby Facilities</h2>
        <p className="text-sm text-slate-400 mt-1">
          Showing results for: <span className="font-semibold text-slate-300">{selectedCategory}</span>
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <MapView 
            markers={mapMarkers} 
            userLocation={userLocation} 
            onMarkerClick={(id) => navigate(`/facilities/${id}`)}
          />
        </div>
        <div>
          <FacilityList facilities={data || []} />
        </div>
      </div>
    </div>
  );
}
