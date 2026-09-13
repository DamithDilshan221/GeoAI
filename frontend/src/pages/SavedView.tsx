import { useSearchContext } from '../context/SearchContext';
import { FacilityListItem } from '../components/facility/FacilityListItem';
import { EmptyState } from '../components/status/EmptyState';
import type { Washroom } from '../types/facility';

export function SavedView() {
  const { state } = useSearchContext();
  const savedList = Object.values(state.savedFacilities || {});

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 pt-4 pb-2 shrink-0">
        <h2 className="text-[22px] font-extrabold text-ink m-0 tracking-tight">Saved Facilities</h2>
        <p className="text-[12px] text-muted-soft m-0 font-medium">Quick access bookmarks</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 pb-8 -webkit-overflow-scrolling-touch">
        {savedList.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <EmptyState message="No saved washrooms yet. Tap the bookmark icon on any washroom to save it for quick access." />
          </div>
        ) : (
          savedList.map((f) => (
            <FacilityListItem
              key={f.id}
              facility={{
                id: f.id,
                name: f.name,
                category: f.category,
                status: (f.status as Washroom['status']) || 'OPEN',
                distance_m: f.distance_m ?? 0,
                latitude: f.latitude ?? 0,
                longitude: f.longitude ?? 0,
                rating: f.rating,
                audience: (f.audience as 'VISITOR' | 'STAFF') || 'VISITOR',
                fixtures: {},
              }}
            />
          ))
        )}
      </div>
    </div>
  );
}
