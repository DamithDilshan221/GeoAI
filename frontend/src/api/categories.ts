import apiClient from './client';
import { Category } from '../types/category';

export async function getCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Category[]>('/api/v1/categories');
  return data;
}
