import apiClient from './client';
import type { Route } from '../types/route';

export async function getRoute(params: {
  origin_lat: number; origin_lon: number; facility_id: number; accessible_only: boolean;
}): Promise<Route> {
  const { data } = await apiClient.get<Route>('/api/v1/routes', { params });
  return data;
}
