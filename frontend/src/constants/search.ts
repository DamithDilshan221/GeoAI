// Must be kept in sync by hand with backend/app/core/config.py's
// DEFAULT_SEARCH_RADIUS_M / MAX_SEARCH_RADIUS_M — the backend exposes
// no endpoint for these values, so there is no way to read them
// dynamically. See Phase 8's resolved decision #3.
export const DEFAULT_RADIUS_M = 1000;
export const MAX_RADIUS_M = 10000;
export const RADIUS_EXPAND_MULTIPLIER = 2;

export const EMPTY_NEARBY_MESSAGE =
  'No suitable facilities were found within the current search radius.';
export const SERVICE_UNAVAILABLE_MESSAGE =
  'The service is temporarily unavailable. Please try again shortly.';
