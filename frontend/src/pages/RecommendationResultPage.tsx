import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { EmptyState } from '../components/status/EmptyState';
import { useRecommendation } from '../hooks/useRecommendation';
import { NavigationOverlay } from '../components/navigation/NavigationOverlay';
import { GEOLOCATION_MESSAGES } from '../hooks/useGeolocation';

function formatTime(seconds: number, isEstimate: boolean): string {
  const mins = Math.round(seconds / 60);
  const label = mins < 1 ? '<1 min' : `${mins} min`;
  return isEstimate ? `${label} (estimated)` : label;
}

function formatDistance(meters: number): string {
  return meters >= 1000
    ? `${(meters / 1000).toFixed(1)} km`
    : `${Math.round(meters)} m`;
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

  const { data, isLoading, isError, refetch } = useRecommendation(params);

  if (!selectedCategory || !location) {
    return <Navigate to="/" replace />;
  }

  if (isLoading) {
    return <LoadingState message="Generating optimal recommendation..." />;
  }

  if (isError) {
    return (
      <ErrorState
        message="Failed to fetch recommendations. Please try again."
        onRetry={refetch}
      />
    );
  }

  if (data?.message) {
    return (
      <div className="flex flex-col h-full overflow-hidden">
        <div className="px-5 pt-4 pb-2 shrink-0 flex items-center justify-between">
          <h2 className="text-[22px] font-bold text-white m-0">Recommended Route</h2>
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
        <h2 className="text-[22px] font-bold text-white m-0">Recommended Route</h2>
        <Link
          to="/nearby"
          className="text-[14px] text-teal hover:text-teal/80 font-bold no-underline active:scale-95 transition-transform"
        >
          Cancel
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 pb-8 -webkit-overflow-scrolling-touch">
        <p className="text-[13.5px] text-muted-soft mt-0 mb-6 max-w-[280px]">
          Based on your location, filters, and current washroom statuses.
        </p>

        {top && (
          <div className="relative rounded-[20px] bg-paper text-ink p-5 shadow-[0_8px_32px_rgba(63,203,190,0.2)] border border-teal/40 overflow-hidden mb-6">
            <div className="absolute top-0 right-0 w-32 h-32 bg-teal/10 blur-2xl rounded-full translate-x-10 -translate-y-10" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-indigo/10 blur-xl rounded-full -translate-x-5 translate-y-5" />

            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-full bg-teal/20 flex items-center justify-center text-teal">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-teal">Top Match</span>
              </div>

              <h3 className="text-xl font-bold text-white m-0 mb-1 leading-tight">{top.name}</h3>
              {top.rating != null && (
                <p className="text-[12px] text-muted m-0 mb-2">
                  ★ {top.rating.toFixed(1)} · {top.status}
                </p>
              )}
              {explanation && (
                <p className="text-[13.5px] text-muted m-0 mb-5 leading-relaxed">{explanation}</p>
              )}

              <div className="flex gap-4 mb-6">
                <div className="flex flex-col">
                  <span className="text-[11px] text-muted-soft uppercase font-bold tracking-wide mb-0.5">Est. Time</span>
                  <span className="text-lg font-bold text-white">
                    {formatTime(top.estimated_time_s, isEstimate)}
                  </span>
                </div>
                <div className="w-px bg-pill-border" />
                <div className="flex flex-col">
                  <span className="text-[11px] text-muted-soft uppercase font-bold tracking-wide mb-0.5">Distance</span>
                  <span className="text-lg font-bold text-white">{formatDistance(top.distance_m)}</span>
                </div>
                <div className="w-px bg-pill-border" />
                <div className="flex flex-col">
                  <span className="text-[11px] text-muted-soft uppercase font-bold tracking-wide mb-0.5">Crowd</span>
                  <span className="text-lg font-bold text-white">{top.crowd_level}</span>
                </div>
              </div>

              {navError && (
                <p className="text-[12px] text-red-400 mb-3 m-0" data-testid="rec-nav-error">{navError}</p>
              )}

              <button
                id="start-navigation-btn"
                onClick={handleStartNavigation}
                className="w-full bg-teal text-[#06302D] border-none rounded-xl py-3.5 font-bold text-[14.5px] cursor-pointer shadow-soft font-display active:scale-[0.98] transition-transform flex items-center justify-center gap-2"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="3 11 22 2 13 21 11 13 3 11"/>
                </svg>
                Start Navigation
              </button>
            </div>
          </div>
        )}

        {/* Alternative picks */}
        {ranked.length > 1 && (
          <div className="mb-4">
            <p className="text-[11px] text-muted-soft uppercase font-bold tracking-wider mb-3">Alternatives</p>
            <div className="flex flex-col gap-2">
              {ranked.slice(1).map((item) => (
                <div
                  key={item.id}
                  className="rounded-[14px] border border-pill-border bg-pill-bg/30 p-4 flex items-center justify-between"
                >
                  <div>
                    <p className="text-[14px] font-semibold text-white m-0 mb-0.5">{item.name}</p>
                    <p className="text-[12px] text-muted m-0">
                      {formatDistance(item.distance_m)} · {formatTime(item.estimated_time_s, item.travel_source === 'straight_line_estimate')}
                    </p>
                  </div>
                  <span className="text-[11px] font-bold text-muted-soft">#{item.rank_position}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
