import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { EmptyState } from '../components/status/EmptyState';
import { useRecommendation } from '../hooks/useRecommendation';
import { NavigationOverlay } from '../components/navigation/NavigationOverlay';
import { GEOLOCATION_MESSAGES } from '../hooks/useGeolocation';
import { SERVICE_UNAVAILABLE_MESSAGE } from '../constants/search';

function formatTime(seconds: number, isEstimate: boolean): string {
  const mins = Math.round(seconds / 60);
  const label = mins < 1 ? '<1 min' : `${mins} min`;
  return isEstimate ? `${label} (estimated)` : label;
}

function formatDistance(meters: number): string {
  return meters >= 1000
    ? `${Number((meters / 1000).toFixed(2))} km`
    : `${Number(meters.toFixed(2))} m`;
}

export function RecommendationResultPage() {
  const { state } = useSearchContext();
  const { selectedCategory, location, selectedAudience } = state;

  const [showNavigation, setShowNavigation] = useState(false);
  const [navOrigin, setNavOrigin] = useState<{ lat: number; lon: number } | null>(null);
  const [navError, setNavError] = useState<string | null>(null);

  const params =
    selectedCategory && location
      ? {
          lat: location.lat,
          lon: location.lon,
          category: selectedCategory,
          radius_m: 1000,
          selectedAudience,
        }
      : null;

  const { data, isLoading, isError, error, refetch } = useRecommendation(params);

  if (!selectedCategory || !location) {
    return <Navigate to="/" replace />;
  }

  if (isLoading) {
    return <LoadingState message="Generating optimal recommendation..." />;
  }

  if (isError) {
    // §22.1: distinguish a backend-unavailable 503 from a generic error so the
    // user sees the same consistent message as NearbyFacilitiesPage does.
    const is503 = (error as { response?: { status?: number } })?.response?.status === 503;
    return (
      <ErrorState
        message={is503 ? SERVICE_UNAVAILABLE_MESSAGE : 'Failed to fetch recommendations. Please try again.'}
        onRetry={refetch}
      />
    );
  }

  if (data?.message) {
    return (
      <div className="flex flex-col h-full overflow-hidden">
        <div className="px-5 pt-4 pb-2 shrink-0 flex items-center justify-between">
          <h2 className="text-[22px] font-bold text-ink m-0">Recommended Route</h2>
          <Link
            to="/nearby"
            className="text-[14px] text-teal hover:text-teal/80 font-bold no-underline active:scale-95 transition-transform"
          >
            Cancel
          </Link>
        </div>
        <div className="flex-1 flex items-center justify-center px-5">
          <EmptyState message={data.message} />
        </div>
      </div>
    );
  }

  const top = data?.recommended_facility;
  const ranked = data?.ranked_facilities ?? [];
  const explanation = data?.explanation;
  const isEstimate = top?.travel_source === 'straight_line_estimate';

  /**
   * Start Navigation handler — requests a FRESH GPS fix (maximumAge:0) per §14.2.
   * Uses the top recommendation's lat/lon as the destination.
   */
  const handleStartNavigation = () => {
    if (!top) return;
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

  return (
    <div className="flex flex-col h-full overflow-hidden relative">
      {/* Navigation overlay — rendered over everything when active */}
      {showNavigation && navOrigin && top && (
        <NavigationOverlay
          origin={navOrigin}
          destination={{
            lat: top.latitude,
            lon: top.longitude,
            name: top.name,
            category: top.category,
          }}
          onClose={() => setShowNavigation(false)}
        />
      )}

      <div className="px-5 pt-4 pb-2 shrink-0 flex items-center justify-between">
        <div>
          <h2 className="text-[22px] font-extrabold text-ink m-0 tracking-tight">AI Recommendation</h2>
          <p className="text-[12px] text-muted-soft m-0 font-medium">Smart route matched to your preferences</p>
        </div>
        <Link
          to="/nearby"
          className="text-[13px] glass-pill px-3 py-1.5 rounded-full text-sky-500 dark:text-sky-400 hover:text-ink font-bold no-underline active:scale-95 transition-transform"
        >
          Cancel
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 pb-8 -webkit-overflow-scrolling-touch">
        {top && (
          <div className="relative rounded-3xl p-[1.5px] bg-gradient-to-br from-indigo-500/80 via-purple-500/50 to-pink-500/80 shadow-[0_0_40px_rgba(139,92,246,0.35)] overflow-hidden mb-6">
            <div className="glass-panel rounded-[22px] p-5 text-ink relative overflow-hidden backdrop-blur-3xl">
              <div className="absolute top-0 right-0 w-40 h-40 bg-indigo-500/15 blur-3xl rounded-full translate-x-12 -translate-y-12 pointer-events-none" />
              <div className="absolute bottom-0 left-0 w-32 h-32 bg-fuchsia-500/15 blur-3xl rounded-full -translate-x-8 translate-y-8 pointer-events-none" />

              <div className="relative z-10">
                <div className="flex items-center justify-between gap-2 mb-3.5">
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full glass-pill text-indigo-600 dark:text-purple-300 border border-purple-400/30">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                    <span className="text-[11px] font-extrabold uppercase tracking-wider">Top Match</span>
                  </div>

                  {top.rating != null && (
                    <span className="text-[12px] font-bold text-amber-500 dark:text-amber-400 glass-pill px-2.5 py-0.5 rounded-full flex items-center gap-1">
                      ★ {top.rating.toFixed(1)}
                    </span>
                  )}
                </div>

                <h3 className="text-[21px] font-extrabold text-ink m-0 mb-1.5 leading-tight tracking-tight">{top.name}</h3>
                
                {explanation && (
                  <p className="text-[13px] text-muted m-0 mb-5 leading-relaxed font-normal">{explanation}</p>
                )}

                {/* Glass Stats Matrix */}
                <div className="grid grid-cols-3 gap-2 mb-6">
                  <div className="glass-pill rounded-2xl p-2.5 text-center">
                    <span className="block text-[10px] text-muted uppercase font-bold tracking-wider mb-0.5">Est. Time</span>
                    <span className="text-[15px] font-extrabold text-ink">
                      {formatTime(top.estimated_time_s, isEstimate)}
                    </span>
                  </div>
                  <div className="glass-pill rounded-2xl p-2.5 text-center">
                    <span className="block text-[10px] text-muted uppercase font-bold tracking-wider mb-0.5">Distance</span>
                    <span className="text-[15px] font-extrabold text-ink">{formatDistance(top.distance_m)}</span>
                  </div>
                  <div className="glass-pill rounded-2xl p-2.5 text-center">
                    <span className="block text-[10px] text-muted uppercase font-bold tracking-wider mb-0.5">Crowd</span>
                    <span className="text-[15px] font-extrabold text-ink">{top.crowd_level}</span>
                  </div>
                </div>

                {navError && (
                  <p className="text-[12px] text-red-500 mb-3 m-0" data-testid="rec-nav-error">{navError}</p>
                )}

                <button
                  id="start-navigation-btn"
                  onClick={handleStartNavigation}
                  className="w-full glass-button-glow text-white rounded-2xl py-3.5 font-extrabold text-[15px] cursor-pointer shadow-glow-primary active:scale-[0.98] transition-transform flex items-center justify-center gap-2 tracking-wide"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="3 11 22 2 13 21 11 13 3 11"/>
                  </svg>
                  Start Navigation
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Alternative picks */}
        {ranked.length > 1 && (
          <div className="mb-4">
            <p className="text-[11px] text-muted-soft uppercase font-bold tracking-wider mb-3 px-1">Alternative Options</p>
            <div className="flex flex-col gap-2.5">
              {ranked.slice(1).map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl glass-panel p-3.5 flex items-center justify-between hover:scale-[1.01] transition-transform"
                >
                  <div>
                    <p className="text-[14.5px] font-bold text-ink m-0 mb-0.5">{item.name}</p>
                    <p className="text-[12px] text-muted m-0">
                      {formatDistance(item.distance_m)} · {formatTime(item.estimated_time_s, item.travel_source === 'straight_line_estimate')}
                    </p>
                  </div>
                  <span className="text-[11px] font-extrabold text-indigo-600 dark:text-purple-300 glass-pill px-2.5 py-1 rounded-full">
                    #{item.rank_position}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
