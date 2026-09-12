import { useQuery } from '@tanstack/react-query';
import { getRecommendations } from '../api/recommendations';

interface RecommendationParams {
  lat: number;
  lon: number;
  category: string;
  radius_m?: number;
  selectedAudience?: 'VISITOR' | 'STAFF' | null;
}

/**
 * Wraps the recommendations API call.
 */
export function useRecommendation(params: RecommendationParams | null) {
  return useQuery({
    queryKey: ['recommendation', params],
    queryFn: () =>
      getRecommendations({
        lat: params!.lat,
        lon: params!.lon,
        category: params!.category,
        radius_m: params!.radius_m ?? 1000,
        secondary_preference:
          params?.selectedAudience === 'STAFF' ? 'staff_preferred' : undefined,
      }),
    enabled: params !== null,
  });
}
