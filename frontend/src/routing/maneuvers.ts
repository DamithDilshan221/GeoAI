/**
 * Maneuver text and rotation maps + helper functions.
 *
 * Transcribed verbatim from pera-rest-nav.html's MANEUVER_TEXT and
 * MANEUVER_ROTATION constants and their companion helpers.
 *
 * All inputs use the typed OSRMStep shape below — no loose object access.
 */

export interface OSRMStep {
  maneuver: {
    type: string;
    modifier?: string;
    location?: [number, number]; // [lon, lat]
  };
  distance: number;
}

/** Maps OSRM maneuver type+modifier to a human-readable instruction. */
const MANEUVER_TEXT: Record<string, string> = {
  depart: 'Head',
  arrive: 'You have arrived',
  'turn-left': 'Turn left',
  'turn-right': 'Turn right',
  'turn-sharp left': 'Turn sharp left',
  'turn-sharp right': 'Turn sharp right',
  'turn-slight left': 'Slight left',
  'turn-slight right': 'Slight right',
  'turn-uturn': 'Make a U-turn',
  'continue-straight': 'Continue straight',
  'continue-left': 'Continue left',
  'continue-right': 'Continue right',
  'continue-slight left': 'Continue slight left',
  'continue-slight right': 'Continue slight right',
  'roundabout-left': 'At the roundabout, turn left',
  'roundabout-right': 'At the roundabout, turn right',
  'rotary-left': 'At the rotary, turn left',
  'rotary-right': 'At the rotary, turn right',
  'merge-left': 'Merge left',
  'merge-right': 'Merge right',
  'fork-left': 'Keep left at the fork',
  'fork-right': 'Keep right at the fork',
  'end of road-left': 'At the end of the road, turn left',
  'end of road-right': 'At the end of the road, turn right',
};

/** Maps OSRM maneuver type+modifier to a CSS rotation degrees for the arrow icon. */
const MANEUVER_ROTATION: Record<string, number> = {
  depart: 0,
  arrive: 0,
  'turn-left': -90,
  'turn-right': 90,
  'turn-sharp left': -135,
  'turn-sharp right': 135,
  'turn-slight left': -45,
  'turn-slight right': 45,
  'turn-uturn': 180,
  'continue-straight': 0,
  'continue-left': -90,
  'continue-right': 90,
  'continue-slight left': -45,
  'continue-slight right': 45,
  'roundabout-left': -90,
  'roundabout-right': 90,
  'rotary-left': -90,
  'rotary-right': 90,
  'merge-left': -45,
  'merge-right': 45,
  'fork-left': -45,
  'fork-right': 45,
  'end of road-left': -90,
  'end of road-right': 90,
};

function maneuverKey(step: OSRMStep): string {
  const { type, modifier } = step.maneuver;
  return modifier ? `${type}-${modifier}` : type;
}

/** Returns the human-readable turn instruction for a step. */
export function stepInstruction(step: OSRMStep): string {
  return MANEUVER_TEXT[maneuverKey(step)] ?? 'Continue';
}

/** Returns the CSS rotation degrees for the turn arrow icon. */
export function stepRotation(step: OSRMStep): number {
  return MANEUVER_ROTATION[maneuverKey(step)] ?? 0;
}

/**
 * Converts a remaining distance in metres to a friendly "X min" string.
 * Walking speed: 1.2 m/s (matches PEDESTRIAN_WALKING_SPEED_MPS).
 */
export function remainingSecondsToMinutes(distM: number): string {
  const seconds = distM / 1.2;
  if (seconds < 60) return '<1 min';
  const mins = Math.round(seconds / 60);
  return `${mins} min`;
}
