import { useQuery } from '@tanstack/react-query';
import { getRecommendations } from '../api/recommendations';

interface RecommendationParams {
  lat: number;
  lon: number;
  category: string;
  radius_m: number;
  accessibleOnly: boolean;
}

/**
 * Wraps the recommendations API call.
 *
 * This is the single canonical place where the SearchContext's
 * `accessibleOnly` boolean is mapped to the backend's
 * `secondary_preference: "wheelchair_accessible"` string.
 */
export function useRecommendation(params: RecommendationParams | null) {
  return useQuery({
    queryKey: ['recommendation', params],
    queryFn: () =>
      getRecommendations({
        lat: params!.lat,
        lon: params!.lon,
        category: params!.category,
        radius_m: params!.radius_m,
        secondary_preference: params!.accessibleOnly
          ? 'wheelchair_accessible'
          : undefined,
      }),
    enabled: params !== null,
  });
}
