import { useQuery } from '@tanstack/react-query';
import { getNearbyWashrooms } from '../api/washrooms';

interface NearbyParams {
  lat: number;
  lon: number;
  category: string;
  audience: 'VISITOR' | 'STAFF' | null;
  radius_m: number;
}

export function useNearbyFacilities(params: NearbyParams | null) {
  return useQuery({
    queryKey: ['nearby-washrooms', params],
    queryFn: () => getNearbyWashrooms({
      lat: params!.lat,
      lon: params!.lon,
      category: params!.category,
      radius_m: params!.radius_m,
      ...(params!.audience ? { audience: params!.audience } : {}),
    }),
    enabled: params !== null,
  });
}
