import { FacilityListItem } from '../components/facility/FacilityListItem';
import type { NearbyFacility } from '../types/facility';

export function SavedView() {
  // Mock saved facilities
  const savedFacilities: NearbyFacility[] = [
    {
      id: 1,
      name: 'Main Library Ground Floor',
      category: 'Gender-Neutral',
      status: 'OPEN',
      distance_m: 120,
      latitude: 0,
      longitude: 0,
      rating: 4.5,
    },
    {
      id: 2,
      name: 'Engineering Block A',
      category: 'Accessible',
      status: 'OPEN',
      distance_m: 350,
      latitude: 0,
      longitude: 0,
      rating: null,
    }
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 pt-4 pb-2 shrink-0">
        <h2 className="text-[22px] font-bold text-white m-0">Saved</h2>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 pb-8 -webkit-overflow-scrolling-touch">
        {savedFacilities.map(f => (
          <FacilityListItem key={f.id} facility={f} />
        ))}
      </div>
    </div>
  );
}
