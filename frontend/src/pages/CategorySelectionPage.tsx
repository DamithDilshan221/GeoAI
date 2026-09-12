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
  const { status: geoStatus, location, errorMessage, request: requestLocation } = useGeolocation();
  const { dispatch } = useSearchContext();

  useEffect(() => {
    if (geoStatus === 'granted' && location) {
      dispatch({ type: 'SET_LOCATION', payload: { location, status: 'granted' } });
      
      const pendingRoute = sessionStorage.getItem('pending_route');
      if (pendingRoute) {
        sessionStorage.removeItem('pending_route');
        navigate(pendingRoute);
      } else {
        navigate('/nearby');
      }
    }
  }, [geoStatus, location, dispatch, navigate]);

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

  const handleCategoryClick = (code: string, audience?: 'VISITOR' | 'STAFF' | null) => {
    dispatch({ type: 'SET_CATEGORY', payload: code });
    if (audience) {
      dispatch({ type: 'SET_AUDIENCE', payload: audience });
    }
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
          id="find-washroom"
          name="find-washroom"
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
            onClick={(audience?: 'VISITOR' | 'STAFF' | null) => handleCategoryClick(cat.code, audience)}
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

        <div
          onClick={() => {
            if (categories && categories.length > 0) {
              dispatch({ type: 'SET_CATEGORY', payload: categories[0].code });
            }
            sessionStorage.setItem('pending_route', '/recommend');
            requestLocation();
          }}
          className="relative rounded-[40px] p-[2px] bg-gradient-to-r from-[#A855F7] via-[#8B5CF6] to-[#60A5FA] shadow-[0_8px_30px_-6px_rgba(168,85,247,0.4)] cursor-pointer hover:shadow-[0_12px_40px_-6px_rgba(168,85,247,0.5)] transition-all active:scale-[0.98] mb-3.5 group"
        >
          <div className="flex items-center gap-4 bg-white rounded-[38px] p-2 pr-6 h-full w-full">
            <div className="w-[68px] h-[68px] rounded-full flex items-center justify-center shrink-0 bg-[#F3E8FF] relative shadow-inner overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-white/60 to-transparent"></div>
              <svg width="34" height="34" viewBox="0 0 24 24" fill="currentColor" className="text-[#4F46E5] relative z-10">
                <path d="M10 2L11.8 7.8L17.5 9.5L11.8 11.2L10 17L8.2 11.2L2.5 9.5L8.2 7.8L10 2Z" />
                <path d="M19.5 13.5L20.3 16.2L23 17L20.3 17.8L19.5 20.5L18.7 17.8L16 17L18.7 16.2L19.5 13.5Z" />
                <path d="M18.5 2.5L19 4L20.5 4.5L19 5L18.5 6.5L18 5L16.5 4.5L18 4L18.5 2.5Z" />
              </svg>
            </div>
            
            <div className="flex-1 min-w-0 py-2">
              <h2 className="m-0 mb-1 text-[22px] font-extrabold text-[#111827] tracking-tight">AI Recommendation</h2>
              <p className="text-[14px] text-[#6B7280] font-medium m-0 truncate">Get the best facility for your needs</p>
            </div>

            <div className="shrink-0 flex items-center justify-center text-[#4F46E5] group-hover:translate-x-1.5 transition-transform duration-300">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
