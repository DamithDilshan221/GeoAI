import { FacilityListItem } from '../components/facility/FacilityListItem';
import type { NearbyWashroom } from '../types/facility';

export function SavedView() {
  // Mock saved facilities
  const savedFacilities: NearbyWashroom[] = [
    {
      id: 1,
      name: 'Main Library Ground Floor',
      category: 'UNISEX',
      status: 'OPEN',
      distance_m: 120,
      latitude: 6.9022,
      longitude: 79.8606,
      rating: 4.5,
      audience: 'VISITOR',
      fixtures: {},
    },
    {
      id: 2,
      name: 'Science Faculty Block A',
      category: 'FEMALE',
      status: 'OPEN',
      distance_m: 450,
      latitude: 6.9055,
      longitude: 79.8622,
      rating: null,
      audience: 'VISITOR',
      fixtures: {},
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
