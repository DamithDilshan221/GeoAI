import apiClient from './client';
import { Facility, FacilityListResponse, NearbyFacility } from '../types/facility';

export async function getFacilityById(id: number): Promise<Facility> {
  const { data } = await apiClient.get<Facility>(`/api/v1/facilities/${id}`);
  return data;
}

export async function getFacilities(params?: Record<string, unknown>): Promise<FacilityListResponse> {
  const { data } = await apiClient.get<FacilityListResponse>('/api/v1/facilities', { params });
  return data;
}

export async function getNearbyFacilities(params: {
  lat: number; lon: number; category: string; radius_m?: number; limit?: number;
}): Promise<NearbyFacility[]> {
  const { data } = await apiClient.get<NearbyFacility[]>('/api/v1/facilities/nearby', { params });
  return data;
}
