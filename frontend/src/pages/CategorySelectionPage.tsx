import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCategories } from '../hooks/useCategories';
import { useGeolocation } from '../hooks/useGeolocation';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { PermissionDeniedState } from '../components/status/PermissionDeniedState';
import { CategoryButton } from '../components/facility/CategoryButton';

export function CategorySelectionPage() {
  const navigate = useNavigate();
  const { data: categories, isLoading, error, refetch } = useCategories();
  const { status: geoStatus, errorMessage, request: requestLocation } = useGeolocation();
  const { state, dispatch } = useSearchContext();

  useEffect(() => {
    if (geoStatus === 'granted') {
      navigate('/nearby');
    }
  }, [geoStatus, navigate]);

  if (isLoading) return <LoadingState message="Loading categories..." />;
  if (error) return <ErrorState message="Failed to load categories." onRetry={refetch} />;

  if (geoStatus === 'requesting') {
    return <LoadingState message="Locating you..." />;
  }

  if (geoStatus === 'denied' || geoStatus === 'unavailable') {
    return (
      <PermissionDeniedState
        message={errorMessage || 'Location error'}
        onRetry={requestLocation}
      />
    );
  }

  const handleCategoryClick = (code: string) => {
    dispatch({ type: 'SET_CATEGORY', payload: code });
    requestLocation();
  };

  const handleNearbyClick = () => {
    // If we want to show all nearby, maybe we just clear category or use the first one.
    // For now, let's just pick the first category if none is selected, or keep the existing behavior.
    if (categories && categories.length > 0) {
      dispatch({ type: 'SET_CATEGORY', payload: categories[0].code });
    }
    requestLocation();
  };

  return (
    <div className="pt-[22px] px-5 pb-6">
      <div 
        className="flex items-center gap-2.5 px-[18px] py-[14px] rounded-full bg-pill-bg border border-pill-border cursor-text mb-[22px]"
        onClick={() => navigate('/nearby')}
      >
        <svg className="shrink-0 text-teal" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="11" cy="11" r="7" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input 
          type="text" 
          placeholder="Find a washroom..." 
          className="border-none bg-transparent outline-none text-inherit font-sans text-[14.5px] w-full placeholder:text-muted"
          readOnly
        />
      </div>

      <div className="flex flex-col">
        {categories?.map((cat) => (
          <CategoryButton
            key={cat.id}
            label={cat.label}
            code={cat.code}
            isSelected={state.selectedCategory === cat.code}
            onClick={() => handleCategoryClick(cat.code)}
          />
        ))}

        <div
          onClick={handleNearbyClick}
          className="flex items-center gap-4 bg-paper text-ink rounded-lg p-[18px] mb-3.5 shadow-card cursor-pointer transition-transform active:scale-[0.985]"
        >
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 bg-[rgba(63,203,190,0.16)] text-teal-dark">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="8" />
              <circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none" />
              <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="m-0 mb-2 text-[18.5px] font-bold">Nearby</h2>
            <p className="text-[12px] text-muted-soft font-medium m-0 mt-0.5">Washrooms closest to you right now</p>
          </div>
        </div>
      </div>

      {/* Accessible routes toggle restyled as pill toggle */}
      <div className="mt-2 flex items-center justify-end gap-2.5 text-[13px] font-semibold text-white">
        <span>Wheelchair-accessible routes</span>
        <div 
          className={`relative w-11 h-[26px] rounded-full border shrink-0 cursor-pointer transition-colors duration-200 ${state.accessibleOnly ? 'bg-teal border-teal' : 'bg-pill-bg border-pill-border'}`}
          onClick={() => dispatch({ type: 'SET_ACCESSIBLE_ONLY', payload: !state.accessibleOnly })}
        >
          <div className={`absolute top-[1.5px] left-[1.5px] w-5 h-5 rounded-full transition-all duration-200 ${state.accessibleOnly ? 'translate-x-[18px] bg-[#06302D]' : 'bg-muted'}`}></div>
        </div>
      </div>
    </div>
  );
}
