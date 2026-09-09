import apiClient from './client';
import type { RecommendationResponse } from '../types/recommendation';

interface RecommendationParams {
  lat: number;
  lon: number;
  category: string;
  radius_m: number;
  limit?: number;
  secondary_preference?: string;
}

export async function getRecommendations(
  params: RecommendationParams,
): Promise<RecommendationResponse> {
  const { data } = await apiClient.get<RecommendationResponse>(
    '/api/v1/recommendations',
    { params },
  );
  return data;
}
