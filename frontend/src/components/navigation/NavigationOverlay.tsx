/**
 * NavigationOverlay — full-screen turn-by-turn navigation experience.
 *
 * Props:
 *   origin     — fresh GPS fix (always a new fix, never SearchContext cache)
 *   destination — facility coords + name + optional category
 *   onClose    — called by both Stop (top bar) and End (bottom sheet) buttons
 *
 * On mount: calls fetchWalkingRoute, feeds steps to useLiveNavigation.
 * Renders: top bar, NavigationMap, TurnBanner, bottom sheet with remaining
 * time/distance and End button.
 *
 * Two dismiss points (Stop + End) both call onClose, which unmounts this
 * component, naturally tearing down useLiveNavigation's watchPosition.
 */

import { useState, useEffect } from 'react';
import { NavigationMap } from '../map/NavigationMap';
import { TurnBanner } from './TurnBanner';
import { RouteFallbackNotice } from './RouteFallbackNotice';
import { useLiveNavigation } from '../../hooks/useLiveNavigation';
import { fetchWalkingRoute } from '../../routing/osrmClient';
import { remainingSecondsToMinutes } from '../../routing/maneuvers';
import type { RouteFetchResult } from '../../routing/osrmClient';
import type { OSRMStep } from '../../routing/maneuvers';

export interface NavigationOverlayProps {
  origin: { lat: number; lon: number };
  destination: {
    lat: number;
    lon: number;
    name: string;
    category?: string;
  };
  onClose: () => void;
}

export function NavigationOverlay({ origin, destination, onClose }: NavigationOverlayProps) {
  const [route, setRoute] = useState<RouteFetchResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchWalkingRoute(origin, destination).then((r) => {
      if (!cancelled) {
        setRoute(r);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [origin, destination]);

  const steps: OSRMStep[] = route?.steps ?? [];
  const { stepIdx, currentPosition } = useLiveNavigation(steps);

  const currentStep = steps[stepIdx] ?? null;
  const arrived = stepIdx >= steps.length - 1 && steps.length > 0;
  const remainingM = route?.distanceM ?? 0;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-navy-950 text-white"
      data-testid="navigation-overlay"
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 pt-safe-top py-3.5 glass-panel rounded-none border-t-0 border-x-0 border-b border-white/15 shrink-0 backdrop-blur-2xl">
        <div className="flex-1 min-w-0">
          <p className="text-[10px] text-sky-400 uppercase tracking-widest font-extrabold m-0">Live Walking Route</p>
          <h2 className="text-[17px] font-extrabold text-white m-0 truncate tracking-tight">{destination.name}</h2>
        </div>
        <button
          onClick={onClose}
          className="ml-3 px-4 py-2 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 font-bold text-[13px] cursor-pointer active:scale-95 transition-transform glass-pill"
          data-testid="nav-stop-btn"
        >
          Stop
        </button>
      </div>

      {/* OSRM-fallback notice — §14.4 */}
      <RouteFallbackNotice visible={route?.source === 'straight_line_estimate'} />

      {/* Turn banner */}
      <TurnBanner
        step={currentStep}
        remainingM={remainingM}
        arrived={arrived}
        destinationName={destination.name}
      />

      {/* Map */}
      <div className="flex-1 relative overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-navy-950/90 backdrop-blur-md">
            <p className="text-sky-300 text-[14px] font-bold">Calculating fastest walking path…</p>
          </div>
        ) : (
          <NavigationMap
            path={route?.path ?? []}
            userPosition={currentPosition}
            destination={destination}
          />
        )}
      </div>

      {/* Bottom sheet */}
      <div className="shrink-0 glass-panel border-b-0 border-x-0 border-t border-white/20 px-5 py-4 pb-safe-bottom flex items-center justify-between gap-4 backdrop-blur-2xl">
        <div>
          <p className="text-[10px] text-muted-soft uppercase tracking-widest font-extrabold m-0 mb-0.5">
            Remaining Distance & Time
          </p>
          <p className="text-[20px] font-extrabold text-white m-0 tracking-tight">
            {remainingSecondsToMinutes(remainingM)}
          </p>
          <p className="text-[12px] text-sky-300 font-semibold m-0">
            {remainingM >= 1000
              ? `${(remainingM / 1000).toFixed(1)} km`
              : `${Math.round(remainingM)} m`}
          </p>
        </div>

        <button
          onClick={onClose}
          className="px-6 py-3 rounded-2xl bg-rose-500 hover:bg-rose-600 text-white font-extrabold text-[14px] border border-white/25 cursor-pointer active:scale-95 transition-transform shadow-[0_0_18px_rgba(244,63,94,0.45)]"
          data-testid="nav-end-btn"
        >
          End
        </button>
      </div>
    </div>
  );
}
