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
  const { state: searchState, dispatch } = useSearchContext();
  const audience = searchState.selectedAudience || 'VISITOR';

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

  const handleAudienceToggle = (targetAudience: 'VISITOR' | 'STAFF') => {
    dispatch({ type: 'SET_AUDIENCE', payload: targetAudience });
    if (categories && categories.length > 0 && !searchState.selectedCategory) {
      dispatch({ type: 'SET_CATEGORY', payload: categories[0].code });
    }
    requestLocation();
  };

  const handleCategoryClick = (code: string) => {
    dispatch({ type: 'SET_CATEGORY', payload: code });
    dispatch({ type: 'SET_AUDIENCE', payload: audience });
    requestLocation();
  };

  const handleNearbyClick = () => {
    if (categories && categories.length > 0) {
      dispatch({ type: 'SET_CATEGORY', payload: categories[0].code });
    }
    requestLocation();
  };

  return (
    <div className="pt-2 px-5 pb-8 space-y-4">
      {/* Location & Search Composite Panel */}
      <div className="rounded-3xl p-4 shadow-card location-panel">
        {/* Top Location Row */}
        <div className="flex items-center justify-between mb-3 cursor-pointer select-none" onClick={() => requestLocation()}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center location-pin-box shrink-0 shadow-inner">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
              </svg>
            </div>
            <div>
              <span className="block text-[9.5px] font-extrabold uppercase tracking-widest location-header-text">
                YOUR LOCATION
              </span>
              <span className="text-[14.5px] font-extrabold text-ink tracking-tight">
                University of Peradeniya
              </span>
            </div>
          </div>
          <div className="text-muted-soft">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </div>

        {/* Search Bar Input */}
        <div
          className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-2xl cursor-pointer transition-all hover:bg-white/10 active:scale-[0.99] group shadow-inner search-bar-box"
          onClick={() => navigate('/nearby')}
        >
          <svg className="shrink-0 text-muted-soft group-hover:text-sky-400 transition-colors" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input 
            id="find-washroom"
            name="find-washroom"
            type="text" 
            placeholder="Search campus building or washroom..." 
            className="border-none bg-transparent outline-none text-ink font-sans text-[13.5px] w-full placeholder:text-muted cursor-pointer font-medium"
            readOnly
          />
          <button 
            type="button"
            className="w-7 h-7 rounded-lg glass-pill flex items-center justify-center text-muted-soft hover:text-sky-400 shrink-0 cursor-pointer border border-white/10"
            title="Locate me"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="7" />
              <line x1="12" y1="2" x2="12" y2="5" />
              <line x1="12" y1="19" x2="12" y2="22" />
              <line x1="2" y1="12" x2="5" y2="12" />
              <line x1="19" y1="12" x2="22" y2="12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Visitor / Staff Segmented Toggle */}
      <div className="p-1 rounded-2xl flex gap-1.5 shadow-card segmented-toggle-panel">
        <button
          type="button"
          onClick={() => handleAudienceToggle('VISITOR')}
          className={`flex-1 py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 font-extrabold text-[13.5px] cursor-pointer transition-all active:scale-95 ${
            audience === 'VISITOR'
              ? 'bg-gradient-to-r from-indigo-500 via-purple-600 to-fuchsia-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.5)] border border-white/25'
              : 'text-muted-soft hover:text-ink'
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <span>Visitor</span>
        </button>
        <button
          type="button"
          onClick={() => handleAudienceToggle('STAFF')}
          className={`flex-1 py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 font-extrabold text-[13.5px] cursor-pointer transition-all active:scale-95 ${
            audience === 'STAFF'
              ? 'bg-gradient-to-r from-indigo-500 via-purple-600 to-fuchsia-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.5)] border border-white/25'
              : 'text-muted-soft hover:text-ink'
          }`}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="16" rx="2" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <circle cx="12" cy="11" r="2.5" />
            <path d="M8 17a4 4 0 0 1 8 0" />
          </svg>
          <span>Staff</span>
        </button>
      </div>

      {/* Category List */}
      <div className="flex flex-col">
        {categories?.map((cat) => (
          <CategoryButton
            key={cat.id}
            label={cat.label}
            code={cat.code}
            onClick={() => handleCategoryClick(cat.code)}
          />
        ))}

        {/* Nearby Quick Access */}
        <div
          onClick={handleNearbyClick}
          className="flex items-center gap-4 text-ink rounded-2xl p-4 mb-3.5 shadow-card cursor-pointer transition-all duration-200 hover:scale-[1.01] active:scale-[0.985] group relative overflow-hidden backdrop-blur-xl card-nearby"
        >
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-inner group-hover:scale-105 transition-transform icon-box-nearby">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="m-0 mb-1 text-[18px] font-extrabold tracking-tight text-ink">Nearby</h2>
            <p className="text-[12.5px] text-muted font-medium m-0">Washrooms closest to you right now</p>
          </div>
          <div className="text-muted-soft group-hover:text-ink group-hover:translate-x-1 transition-all">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </div>

        {/* AI Recommendation / Best Match For You Card */}
        <div
          onClick={() => {
            if (categories && categories.length > 0) {
              dispatch({ type: 'SET_CATEGORY', payload: categories[0].code });
            }
            dispatch({ type: 'SET_AUDIENCE', payload: audience });
            sessionStorage.setItem('pending_route', '/recommend');
            requestLocation();
          }}
          className="flex items-center gap-4 text-ink rounded-2xl p-4 mb-3.5 shadow-card cursor-pointer transition-all duration-200 hover:scale-[1.01] active:scale-[0.985] group relative overflow-hidden backdrop-blur-xl card-recommend"
        >
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-md group-hover:scale-105 transition-transform bg-gradient-to-br from-indigo-500 via-purple-600 to-fuchsia-600 text-white border border-white/25">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L14.2 9.8L22 12L14.2 14.2L12 22L9.8 14.2L2 12L9.8 9.8L12 2Z" />
              <path d="M19 3L19.8 5.2L22 6L19.8 6.8L19 9L18.2 6.8L16 6L18.2 5.2L19 3Z" opacity="0.8" />
              <path d="M5 16L5.6 17.4L7 18L5.6 18.6L5 20L4.4 18.6L3 18L4.4 17.4L5 16Z" opacity="0.8" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[10px] font-extrabold uppercase tracking-widest text-indigo-400 mb-0.5">
              AI RECOMMENDATION
            </div>
            <h2 className="m-0 mb-1 text-[18px] font-extrabold tracking-tight text-ink">Best Match For You</h2>
            <p className="text-[12px] text-muted font-medium m-0">Distance • Availability • Rating</p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-600 to-fuchsia-600 text-white shadow-[0_0_18px_rgba(139,92,246,0.5)] flex items-center justify-center border border-white/25 group-hover:scale-105 active:scale-95 transition-all shrink-0">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

