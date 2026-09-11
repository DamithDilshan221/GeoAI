import apiClient from './client';
import type { Washroom, FacilityListResponse, NearbyWashroom } from '../types/facility';

export async function getWashroomById(id: number): Promise<Washroom> {
  const { data } = await apiClient.get<Washroom>(`/api/v1/facilities/${id}`);
  return data;
}

export async function getWashrooms(params?: Record<string, unknown>): Promise<FacilityListResponse> {
  const { data } = await apiClient.get<FacilityListResponse>('/api/v1/facilities', { params });
  return data;
}

export async function getNearbyWashrooms(params: {
  lat: number; lon: number; category: string;
  audience?: 'VISITOR' | 'STAFF'; radius_m: number;
}): Promise<NearbyWashroom[]> {
  const { data } = await apiClient.get<NearbyWashroom[]>('/api/v1/washrooms/nearby', {
    params: {
      lat: params.lat, lon: params.lon, category: params.category,
      radius_m: params.radius_m,
      ...(params.audience ? { audience: params.audience } : {}),
    },
  });
  return data;
}
