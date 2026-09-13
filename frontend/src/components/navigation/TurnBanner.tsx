/**
 * TurnBanner — the turn-by-turn instruction banner.
 *
 * Pure presentational component. Displays the rotating arrow icon, instruction
 * text, and distance-to-next-turn. Shows an arrival state when arrived=true.
 *
 * Matches the prototype's #navOverlay turnBanner/turn-arrow/turn-instruction/
 * turn-distance markup and arrived-state swap to a checkmark.
 */

import { stepInstruction, stepRotation, remainingSecondsToMinutes } from '../../routing/maneuvers';
import type { OSRMStep } from '../../routing/maneuvers';

export interface TurnBannerProps {
  step: OSRMStep | null;
  remainingM: number;
  arrived: boolean;
  destinationName: string;
}

export function TurnBanner({ step, remainingM, arrived, destinationName }: TurnBannerProps) {
  if (arrived) {
    return (
      <div
        className="flex items-center gap-3 px-5 py-3.5 glass-panel bg-emerald-500/10 border-b border-emerald-500/30"
        data-testid="turn-banner-arrived"
      >
        <div className="w-10 h-10 rounded-2xl bg-emerald-500 flex items-center justify-center shrink-0 shadow-[0_0_16px_rgba(16,185,129,0.5)]">
          {/* Checkmark on arrival */}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div>
          <p className="text-[13.5px] font-bold text-emerald-300 m-0">You have arrived</p>
          <p className="text-[12px] text-muted m-0">{destinationName}</p>
        </div>
      </div>
    );
  }

  if (!step) return null;

  const instruction = stepInstruction(step);
  const rotation = stepRotation(step);
  const timeLabel = remainingSecondsToMinutes(remainingM);

  return (
    <div
      className="flex items-center gap-3 px-5 py-3 glass-panel border-b border-white/15 backdrop-blur-xl"
      data-testid="turn-banner"
    >
      {/* Rotating turn arrow */}
      <div
        className="w-10 h-10 rounded-2xl glass-pill bg-sky-500/15 border border-sky-400/30 flex items-center justify-center shrink-0 transition-transform duration-300 shadow-inner"
        style={{ transform: `rotate(${rotation}deg)` }}
        data-testid="turn-arrow"
        data-rotation={rotation}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="19" x2="12" y2="5" />
          <polyline points="5 12 12 5 19 12" />
        </svg>
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-[14px] font-extrabold text-ink m-0 truncate" data-testid="turn-instruction">
          {instruction}
        </p>
        <p className="text-[12px] text-muted-soft m-0" data-testid="turn-distance">
          {timeLabel} away
        </p>
      </div>

      {/* Distance bubble */}
      <div className="text-right shrink-0">
        <span className="text-[12px] font-extrabold text-sky-300 glass-pill px-2.5 py-1 rounded-full">
          {remainingM >= 1000
            ? `${(remainingM / 1000).toFixed(1)} km`
            : `${Math.round(remainingM)} m`}
        </span>
      </div>
    </div>
  );
}
