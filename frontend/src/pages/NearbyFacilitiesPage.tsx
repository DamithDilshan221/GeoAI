import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { FacilityList } from '../components/facility/FacilityList';
import { NearbyFacility } from '../types/facility';

const MOCK_NEARBY_FACILITIES: NearbyFacility[] = [
  // Using some realistic sounding data with IDs that would exist in phase 3 dev seed
  { id: 1, name: 'Main Station Restroom', category: 'UNISEX', status: 'OPEN', rating: 4.5, distance_m: 120, latitude: 0, longitude: 0 },
  { id: 2, name: 'North Wing Washroom', category: 'UNISEX', status: 'TEMPORARILY_UNAVAILABLE', rating: 3.8, distance_m: 350, latitude: 0, longitude: 0 },
  { id: 3, name: 'Park Facility A', category: 'MALE', status: 'OPEN', rating: null, distance_m: 550, latitude: 0, longitude: 0 },
];

export function NearbyFacilitiesPage() {
  const { state } = useSearchContext();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data delay - to be replaced with useNearbyFacilities + getNearbyFacilities in Phase 8
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (!state.selectedCategory) {
    return <Navigate to="/" replace />;
  }

  if (isLoading) {
    return <LoadingState message="Finding facilities near you..." />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Nearby Facilities</h2>
        <p className="text-sm text-slate-400 mt-1">
          Showing results for: <span className="font-semibold text-slate-300">{state.selectedCategory}</span>
        </p>
      </div>

      {/* Mock data list */}
      <FacilityList facilities={MOCK_NEARBY_FACILITIES} />
    </div>
  );
}
