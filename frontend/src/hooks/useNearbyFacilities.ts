import { useQuery } from '@tanstack/react-query';
import { getNearbyFacilities } from '../api/facilities';

interface NearbyParams {
  lat: number;
  lon: number;
  category: string;
  radius_m: number;
}

export function useNearbyFacilities(params: NearbyParams | null) {
  return useQuery({
    queryKey: ['nearby-facilities', params],
    queryFn: () => getNearbyFacilities(params!),
    enabled: params !== null,
  });
}
