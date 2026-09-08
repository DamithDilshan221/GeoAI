import { useQuery } from '@tanstack/react-query';
import { getFacilityById } from '../api/facilities';

export function useFacility(id: number) {
  return useQuery({
    queryKey: ['facility', id],
    queryFn: () => getFacilityById(id),
    enabled: !!id,
  });
}
