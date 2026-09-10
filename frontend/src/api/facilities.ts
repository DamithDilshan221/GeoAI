import apiClient from './client';
import type { Washroom, FacilityListResponse, NearbyWashroom } from '../types/facility';

export async function getFacilityById(id: number): Promise<Washroom> {
  const { data } = await apiClient.get<Washroom>(`/api/v1/facilities/${id}`);
  return data;
}

export async function getFacilities(params?: Record<string, unknown>): Promise<FacilityListResponse> {
  const { data } = await apiClient.get<FacilityListResponse>('/api/v1/facilities', { params });
  return data;
}

export async function getNearbyFacilities(params: {
  lat: number; lon: number; category: string; radius_m?: number; limit?: number; audience?: string;
}): Promise<NearbyWashroom[]> {
  const { data } = await apiClient.get<NearbyWashroom[]>('/api/v1/facilities/nearby', { params });
  return data;
}
