import { useQuery } from '@tanstack/react-query';
import { getWashroomById } from '../api/washrooms';

export function useFacility(id: number) {
  return useQuery({
    queryKey: ['facility', id],
    queryFn: () => getWashroomById(id),
    enabled: !!id,
  });
}
