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
      className="fixed inset-0 z-50 flex flex-col bg-surface"
      data-testid="navigation-overlay"
    >
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 pt-safe-top py-3 bg-paper/95 backdrop-blur-md border-b border-hairline shrink-0">
        <div className="flex-1 min-w-0">
          <p className="text-[11px] text-muted-soft uppercase tracking-wider m-0">Navigating to</p>
          <h2 className="text-[16px] font-bold text-ink m-0 truncate">{destination.name}</h2>
        </div>
        <button
          onClick={onClose}
          className="ml-3 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 font-bold text-[13px] cursor-pointer active:scale-95 transition-transform"
          data-testid="nav-stop-btn"
        >
          Stop
        </button>
      </div>

      {/* OSRM-fallback notice — §14.4: shown whenever the route source is a
          straight-line estimate rather than a real OSRM walking route. */}
      <RouteFallbackNotice visible={route?.source === 'straight_line_estimate'} />

      {/* Turn banner */}
      <TurnBanner
        step={currentStep}
        remainingM={remainingM}
        arrived={arrived}
        destinationName={destination.name}
      />

      {/* Map — takes remaining vertical space */}
      <div className="flex-1 relative overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-surface">
            <p className="text-muted-soft text-[14px]">Getting route…</p>
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
      <div className="shrink-0 bg-paper border-t border-hairline px-5 py-4 pb-safe-bottom flex items-center justify-between gap-4">
        <div>
          <p className="text-[11px] text-muted-soft uppercase tracking-wider m-0 mb-0.5">
            Remaining
          </p>
          <p className="text-[18px] font-bold text-ink m-0">
            {remainingSecondsToMinutes(remainingM)}
          </p>
          <p className="text-[12px] text-muted-soft m-0">
            {remainingM >= 1000
              ? `${(remainingM / 1000).toFixed(1)} km`
              : `${Math.round(remainingM)} m`}
          </p>
        </div>

        <button
          onClick={onClose}
          className="px-6 py-3 rounded-2xl bg-red-500 text-white font-bold text-[14px] border-none cursor-pointer active:scale-95 transition-transform shadow-soft"
          data-testid="nav-end-btn"
        >
          End
        </button>
      </div>
    </div>
  );
}
