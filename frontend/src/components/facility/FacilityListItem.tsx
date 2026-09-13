import { useNavigate } from 'react-router-dom';
import type { NearbyWashroom } from '../../types/facility';
import { useSearchContext } from '../../context/SearchContext';

interface FacilityListItemProps {
  facility: NearbyWashroom;
}

export function FacilityListItem({ facility }: FacilityListItemProps) {
  const navigate = useNavigate();
  const { state, dispatch } = useSearchContext();
  const saved = Boolean(state.savedFacilities?.[facility.id]);

  const getCategoryTheme = (cat: string) => {
    const c = cat.toLowerCase();
    if ((c.includes('men') || c.includes('male')) && !c.includes('women') && !c.includes('female')) {
      return { color: 'var(--men)', label: "Men's" };
    }
    if (c.includes('women') || c.includes('female')) {
      return { color: 'var(--women)', label: "Women's" };
    }
    return { color: 'var(--teal)', label: cat };
  };

  const theme = getCategoryTheme(facility.category);

  return (
    <div
      onClick={() => navigate(`/facilities/${facility.id}`)}
      className="flex items-center gap-3.5 glass-panel text-ink rounded-2xl p-3.5 mb-3 cursor-pointer shadow-card transition-all duration-200 hover:scale-[1.01] active:scale-[0.985] relative overflow-hidden group"
    >
      <div 
        className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 text-white shadow-sm border border-white/20"
        style={{ background: theme.color }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 21s-7-7.3-7-12a7 7 0 0 1 14 0c0 4.7-7 12-7 12z" />
          <circle cx="12" cy="9" r="2.3" />
        </svg>
      </div>

      <div className="flex-1 min-w-0 pr-2">
        <div className="flex items-center gap-1.5 mb-0.5">
          <h3 className="m-0 text-[15px] font-extrabold text-ink tracking-tight truncate group-hover:text-indigo-600 dark:group-hover:text-sky-300 transition-colors">
            {facility.name}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[12px] text-muted font-medium truncate">{facility.category}</span>
          {facility.rating !== null && (
            <span className="text-[11px] font-bold text-amber-500 dark:text-amber flex items-center gap-0.5">
              ★ {facility.rating.toFixed(1)}
            </span>
          )}
        </div>
      </div>

      <div className="shrink-0 flex items-center gap-2">
        <div className="text-right flex flex-col items-end gap-1">
          <span className="font-extrabold text-[13.5px] text-ink">
            {Number(facility.distance_m.toFixed(2))} m
          </span>
          <span
            className="text-[10px] font-bold py-0.5 px-2 rounded-full text-white tracking-wide uppercase border border-white/20 shadow-sm"
            style={{ background: theme.color }}
          >
            {theme.label}
          </span>
        </div>

        <button 
          className={`w-8 h-8 rounded-xl glass-pill flex items-center justify-center cursor-pointer transition-transform active:scale-90 ${saved ? 'text-amber-500 bg-amber-400/15 border-amber-400/40' : 'text-muted-soft hover:text-ink'}`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            dispatch({
              type: 'TOGGLE_SAVED',
              payload: {
                id: facility.id,
                name: facility.name,
                category: facility.category,
                status: facility.status,
                distance_m: facility.distance_m,
                rating: facility.rating,
                latitude: facility.latitude,
                longitude: facility.longitude,
                audience: facility.audience,
              },
            });
          }}
          aria-label="Save"
        >
          {saved ? (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
          ) : (
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
          )}
        </button>
      </div>
    </div>
  );
}
