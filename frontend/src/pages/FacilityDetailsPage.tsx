import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useFacility } from '../hooks/useFacility';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { MapView } from '../components/map/MapView';
import { NavigationOverlay } from '../components/navigation/NavigationOverlay';
import { GEOLOCATION_MESSAGES } from '../hooks/useGeolocation';
import { SERVICE_UNAVAILABLE_MESSAGE } from '../constants/search';

export function FacilityDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const facilityId = parseInt(id || '', 10);
  const navigate = useNavigate();
  const { state: searchState, dispatch } = useSearchContext();
  
  const { data: facility, isLoading, error, refetch } = useFacility(facilityId);
  const saved = Boolean(searchState.savedFacilities?.[facilityId]);
  const [showNavigation, setShowNavigation] = useState(false);
  const [navOrigin, setNavOrigin] = useState<{ lat: number; lon: number } | null>(null);
  const [navError, setNavError] = useState<string | null>(null);

  if (isLoading) return <LoadingState message="Loading washroom details..." />;

  if (error) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const is404 = (error as any).response?.status === 404;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const is503 = (error as any).response?.status === 503;

    if (is404) {
      return (
        <div className="text-center p-8 text-ink h-full flex flex-col justify-center">
          <h2 className="text-2xl font-bold mb-4 text-ink">Washroom Not Found</h2>
          <p className="text-muted-soft mb-6">The washroom you're looking for doesn't exist or has been removed.</p>
          <Link to="/" className="text-teal font-bold underline">Return to Search</Link>
        </div>
      );
    }
    // §22.1: distinguish a backend-unavailable 503 from a generic error.
    return (
      <ErrorState
        message={is503 ? SERVICE_UNAVAILABLE_MESSAGE : 'Failed to load washroom details.'}
        onRetry={refetch}
      />
    );
  }

  if (!facility) return null;

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

  const mapMarkers = [{
    id: facility.id,
    lat: facility.latitude,
    lon: facility.longitude,
    title: facility.name,
    category: facility.category
  }];

  /**
   * Navigate button handler — requests a FRESH GPS fix (maximumAge: 0 per §14.2/
   * resolved decision #9). Never trusts SearchContext.location — this page may be
   * reached via deep link without going through the search flow.
   */
  const handleNavigate = () => {
    setNavError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setNavOrigin({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setShowNavigation(true);
      },
      (err) => {
        setNavError(
          err.code === 1
            ? GEOLOCATION_MESSAGES.denied
            : GEOLOCATION_MESSAGES.unavailable,
        );
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
    );
  };

  /**
   * External maps deep-link per §14.5 — convenience only, secondary to the in-app overlay.
   */
  const handleExternalMaps = () => {
    if (!navOrigin) {
      // If we don't have a fresh fix yet, just open with destination only
      window.open(
        `https://www.google.com/maps/dir/?api=1&destination=${facility.latitude},${facility.longitude}&travelmode=walking`,
        '_blank',
      );
      return;
    }
    window.open(
      `https://www.google.com/maps/dir/?api=1&origin=${navOrigin.lat},${navOrigin.lon}&destination=${facility.latitude},${facility.longitude}&travelmode=walking`,
      '_blank',
    );
  };

  return (
    <div className="relative w-full h-full flex flex-col overflow-hidden">
      {/* Navigation overlay — rendered over everything when active */}
      {showNavigation && navOrigin && (
        <NavigationOverlay
          origin={navOrigin}
          destination={{
            lat: facility.latitude,
            lon: facility.longitude,
            name: facility.name,
            category: facility.category,
          }}
          onClose={() => setShowNavigation(false)}
        />
      )}

      {/* Background Map */}
      <div className="absolute inset-0 z-0">
        <MapView 
          className="w-full h-full"
          markers={mapMarkers} 
          userLocation={null}
        />
        <button 
          onClick={() => navigate(-1)}
          className="absolute top-5 left-4 w-11 h-11 bg-paper/90 backdrop-blur-md rounded-full flex items-center justify-center border-none shadow-soft text-ink cursor-pointer z-10"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
      </div>

      {/* Bottom Sheet */}
      <div className="absolute bottom-0 left-0 right-0 glass-panel rounded-t-[32px] shadow-[0_-8px_32px_rgba(0,0,0,0.4)] flex flex-col z-20 max-h-[85vh] backdrop-blur-3xl border-t border-x border-white/20">
        <div className="w-full flex justify-center py-3 pb-1 cursor-grab active:cursor-grabbing">
          <div className="w-12 h-1.5 bg-white/30 rounded-full"></div>
        </div>
        
        <div className="px-5 pt-3 pb-4 border-b border-hairline shrink-0">
          <div className="flex justify-between items-start mb-2 gap-3">
            <h2 className="m-0 text-[22px] font-extrabold text-ink tracking-tight leading-tight">{facility.name}</h2>
          </div>
          
          <div className="flex items-center gap-3 mb-4 text-[13px] text-muted">
            <span className="flex items-center gap-1.5 text-ink font-semibold">
              <span className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ background: theme.color }}></span>
              {theme.label}
            </span>
            {facility.rating !== null && (
              <span className="flex items-center gap-[3px] text-amber-500 dark:text-amber-400 font-bold">
                ★ {facility.rating.toFixed(1)}
              </span>
            )}
            <span className="text-indigo-600 dark:text-purple-300 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full glass-pill border border-purple-400/30">
              {facility.data_source || 'Verified'}
            </span>
          </div>

          {/* Navigation error message */}
          {navError && (
            <p className="text-[12px] text-red-500 mb-3 m-0" data-testid="nav-error">{navError}</p>
          )}
          
          <div className="flex gap-2.5">
            <button 
              id="navigate-btn"
              onClick={handleNavigate}
              className="flex-[2] glass-button-glow text-white rounded-2xl py-3.5 font-extrabold text-[15px] cursor-pointer shadow-glow-primary active:scale-[0.98] transition-transform flex items-center justify-center gap-2"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="3 11 22 2 13 21 11 13 3 11"/>
              </svg>
              Navigate
            </button>
            <button
              onClick={handleExternalMaps}
              className="flex-1 glass-pill text-ink rounded-2xl flex items-center justify-center cursor-pointer active:scale-[0.98] transition-transform hover:bg-white/15"
              aria-label="Open in Google Maps"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13"/></svg>
            </button>
            <button 
              onClick={() => {
                dispatch({
                  type: 'TOGGLE_SAVED',
                  payload: {
                    id: facility.id,
                    name: facility.name,
                    category: facility.category,
                    status: facility.status,
                    rating: facility.rating,
                    latitude: facility.latitude,
                    longitude: facility.longitude,
                    audience: facility.audience,
                  },
                });
              }}
              className="flex-1 glass-pill text-ink rounded-2xl flex items-center justify-center cursor-pointer active:scale-[0.98] transition-transform hover:bg-white/15"
              aria-label="Save"
            >
              {saved ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
              )}
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto px-5 py-5 -webkit-overflow-scrolling-touch">
          <div className="mb-6">
            <h3 className="m-0 mb-3 text-[15px] font-extrabold text-ink">Features & Accessibility</h3>
            <ul className="list-none p-0 m-0 space-y-3">
              {Object.keys(facility.fixtures || {}).length > 0 ? (
                <li className="text-[14px] text-ink w-full">
                  <div className="grid grid-cols-2 gap-2.5 mt-2">
                    {Object.entries(facility.fixtures || {}).map(([key, count]) => (
                      <div key={key} className="flex items-center justify-between p-3 rounded-2xl glass-pill">
                        <span className="capitalize font-semibold text-ink text-[13px]">{key.replace('_', ' ')}</span>
                        <span className="font-extrabold text-sky-500 dark:text-sky-400 text-[15px]">{count as number}</span>
                      </div>
                    ))}
                  </div>
                </li>
              ) : (
                <li className="text-[14px] text-muted italic">
                  No fixture details available
                </li>
              )}
              <li className="flex items-center gap-3 text-[14px] text-ink">
                <div className="w-8 h-8 rounded-full glass-pill flex items-center justify-center text-sky-500 dark:text-sky-400">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </div>
                Free campus amenity
              </li>
            </ul>
          </div>
          
          <div className="mb-6">
            <h3 className="m-0 mb-3 text-[15px] font-extrabold text-ink">Current Status</h3>
            <div className={`p-4 rounded-2xl border flex items-center gap-3 glass-pill ${
              facility.status === 'OPEN'
                ? 'border-emerald-400/30 text-emerald-300'
                : facility.status === 'CLOSED'
                  ? 'border-rose-400/30 text-rose-300'
                  : 'border-amber-400/30 text-amber-300'
            }`}>
              <div className="w-2.5 h-2.5 rounded-full bg-current animate-pulse"></div>
              <span className="font-bold text-[14.5px]">Currently {facility.status.replace('_', ' ')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
