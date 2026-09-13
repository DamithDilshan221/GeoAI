import { useState, useEffect } from 'react';
import { useMapTheme } from '../hooks/useMapTheme';

export function SettingsView() {
  // Theme Mode ('dark' | 'light' | 'system')
  const [themeMode, setThemeMode] = useState<'dark' | 'light' | 'system'>(() => {
    return (localStorage.getItem('theme_mode') as 'dark' | 'light' | 'system') || 'dark';
  });

  // Toggles state with persistence
  const [highContrast, setHighContrast] = useState(() => localStorage.getItem('geoai_high_contrast') === 'true');
  const [reduceMotion, setReduceMotion] = useState(() => localStorage.getItem('geoai_reduce_motion') === 'true');
  const [autoDetectLocation, setAutoDetectLocation] = useState(() => localStorage.getItem('geoai_auto_detect_location') !== 'false');
  const [showClosedFacilities, setShowClosedFacilities] = useState(() => localStorage.getItem('geoai_show_closed') === 'true');
  const [smartRecommendations, setSmartRecommendations] = useState(() => localStorage.getItem('geoai_smart_recs') !== 'false');
  const [explainRecommendations, setExplainRecommendations] = useState(() => localStorage.getItem('geoai_explain_recs') !== 'false');
  const [liveUpdates, setLiveUpdates] = useState(() => localStorage.getItem('geoai_live_nav') !== 'false');
  const [voiceGuidance, setVoiceGuidance] = useState(() => localStorage.getItem('geoai_voice_guidance') !== 'false');

  // Sliders state
  const [distanceWeight, setDistanceWeight] = useState<number>(() => {
    const val = localStorage.getItem('geoai_weight_distance');
    return val ? Number(val) : 40;
  });
  const [ratingWeight, setRatingWeight] = useState<number>(() => {
    const val = localStorage.getItem('geoai_weight_rating');
    return val ? Number(val) : 30;
  });
  const [availabilityWeight, setAvailabilityWeight] = useState<number>(() => {
    const val = localStorage.getItem('geoai_weight_availability');
    return val ? Number(val) : 30;
  });

  // Dropdown / Cycling selectors
  const radiusOptions = ['250 m', '500 m', '1000 m', '2000 m'];
  const [radiusIndex, setRadiusIndex] = useState<number>(() => {
    const val = localStorage.getItem('geoai_radius_idx');
    return val ? Number(val) : 1; // default 500 m
  });

  const walkingOptions = ['Walking', 'Accessible', 'Fast Walk'];
  const [walkingIndex, setWalkingIndex] = useState<number>(() => {
    const val = localStorage.getItem('geoai_walking_idx');
    return val ? Number(val) : 0;
  });

  const routePrefOptions = ['Fastest route', 'Sheltered path', 'Well-lit walkway', 'Accessible path'];
  const [routePrefIndex, setRoutePrefIndex] = useState<number>(() => {
    const val = localStorage.getItem('geoai_route_pref_idx');
    return val ? Number(val) : 0;
  });

  // Map theme hook
  const { themeId, setTheme, availableThemes } = useMapTheme();

  // Apply Theme Mode changes
  const applyThemeMode = (mode: 'dark' | 'light' | 'system') => {
    setThemeMode(mode);
    localStorage.setItem('theme_mode', mode);

    if (mode === 'light') {
      document.body.classList.add('day');
    } else if (mode === 'dark') {
      document.body.classList.remove('day');
    } else {
      // System mode
      const isSystemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isSystemDark) {
        document.body.classList.remove('day');
      } else {
        document.body.classList.add('day');
      }
    }
  };

  useEffect(() => {
    if (themeMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = (e: MediaQueryListEvent) => {
        if (e.matches) {
          document.body.classList.remove('day');
        } else {
          document.body.classList.add('day');
        }
      };
      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    }
  }, [themeMode]);

  // Handlers for toggles
  const handleToggle = (setter: React.Dispatch<React.SetStateAction<boolean>>, storageKey: string) => {
    setter((prev) => {
      const next = !prev;
      localStorage.setItem(storageKey, String(next));
      return next;
    });
  };

  const handleSliderChange = (
    value: number,
    setter: React.Dispatch<React.SetStateAction<number>>,
    storageKey: string
  ) => {
    setter(value);
    localStorage.setItem(storageKey, String(value));
  };

  const cycleRadius = () => {
    const next = (radiusIndex + 1) % radiusOptions.length;
    setRadiusIndex(next);
    localStorage.setItem('geoai_radius_idx', String(next));
  };

  const cycleMapTheme = () => {
    const currentIndex = availableThemes.findIndex((t) => t.id === themeId);
    const nextIndex = (currentIndex + 1) % availableThemes.length;
    const nextTheme = availableThemes[nextIndex];
    if (nextTheme) {
      setTheme(nextTheme.id);
    }
  };

  const cycleWalking = () => {
    const next = (walkingIndex + 1) % walkingOptions.length;
    setWalkingIndex(next);
    localStorage.setItem('geoai_walking_idx', String(next));
  };

  const cycleRoutePref = () => {
    const next = (routePrefIndex + 1) % routePrefOptions.length;
    setRoutePrefIndex(next);
    localStorage.setItem('geoai_route_pref_idx', String(next));
  };

  const activeThemeName = availableThemes.find((t) => t.id === themeId)?.name.split(' (')[0].split(' ')[0] || 'OpenStreetMap';

  const isDay = document.body.classList.contains('day');
  const getSliderBg = (val: number) => {
    if (isDay) {
      return `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${val}%, rgba(99, 102, 241, 0.18) ${val}%, rgba(99, 102, 241, 0.18) 100%)`;
    }
    return `linear-gradient(to right, #818cf8 0%, #c084fc ${val}%, rgba(255, 255, 255, 0.15) ${val}%, rgba(255, 255, 255, 0.15) 100%)`;
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-24 -webkit-overflow-scrolling-touch">

        {/* Card 1: Appearance */}
        <div className="glass-panel rounded-3xl p-4 sm:p-5 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 flex items-center justify-center text-white shadow-[0_0_18px_rgba(168,85,247,0.45)] border border-white/30 shrink-0">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="13.5" cy="6.5" r=".5" fill="currentColor" />
                  <circle cx="17.5" cy="10.5" r=".5" fill="currentColor" />
                  <circle cx="8.5" cy="7.5" r=".5" fill="currentColor" />
                  <circle cx="6.5" cy="12.5" r=".5" fill="currentColor" />
                  <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-[16px] font-extrabold text-ink tracking-tight m-0 leading-tight">Appearance</h3>
                <p className="text-[12px] text-muted-soft font-semibold m-0 mt-0.5">Theme, display & interface</p>
              </div>
            </div>
            <div className="text-muted-soft opacity-60">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          {/* Theme Selector Segmented Pill */}
          <div className="flex items-center justify-between py-2.5 border-b border-hairline">
            <span className="text-[14px] font-bold text-ink">Theme</span>
            <div className="flex items-center p-1 rounded-full glass-pill border border-white/10 gap-0.5 shadow-inner">
              <button
                type="button"
                onClick={() => applyThemeMode('dark')}
                className={`px-3 py-1.5 rounded-full text-[12px] font-black flex items-center gap-1.5 transition-all duration-200 cursor-pointer ${
                  themeMode === 'dark'
                    ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white shadow-[0_0_14px_rgba(139,92,246,0.6)] border border-white/30 scale-[1.02]'
                    : 'text-muted hover:text-ink'
                }`}
              >
                <span className="text-[12px]">🌙</span>
                <span>Dark</span>
              </button>
              <button
                type="button"
                onClick={() => applyThemeMode('light')}
                className={`px-3 py-1.5 rounded-full text-[12px] font-black flex items-center gap-1.5 transition-all duration-200 cursor-pointer ${
                  themeMode === 'light'
                    ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white shadow-[0_0_14px_rgba(139,92,246,0.6)] border border-white/30 scale-[1.02]'
                    : 'text-muted hover:text-ink'
                }`}
              >
                <span className="text-[12px]">☀️</span>
                <span>Light</span>
              </button>
              <button
                type="button"
                onClick={() => applyThemeMode('system')}
                className={`px-3 py-1.5 rounded-full text-[12px] font-black flex items-center gap-1.5 transition-all duration-200 cursor-pointer ${
                  themeMode === 'system'
                    ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 text-white shadow-[0_0_14px_rgba(139,92,246,0.6)] border border-white/30 scale-[1.02]'
                    : 'text-muted hover:text-ink'
                }`}
              >
                <span className="text-[12px]">⚙️</span>
                <span>System</span>
              </button>
            </div>
          </div>

          {/* High Contrast */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-purple-400 dark:text-purple-300">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">High Contrast</div>
                <div className="text-[11.5px] text-muted-soft">Better visibility</div>
              </div>
            </div>
            <Switch
              checked={highContrast}
              onChange={() => handleToggle(setHighContrast, 'geoai_high_contrast')}
            />
          </div>

          {/* Reduce Motion */}
          <div className="flex items-center justify-between pt-3">
            <div className="flex items-center gap-3">
              <div className="text-purple-400 dark:text-purple-300">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Reduce Motion</div>
                <div className="text-[11.5px] text-muted-soft">Minimise animations</div>
              </div>
            </div>
            <Switch
              checked={reduceMotion}
              onChange={() => handleToggle(setReduceMotion, 'geoai_reduce_motion')}
            />
          </div>
        </div>

        {/* Card 2: Map & Location */}
        <div className="glass-panel rounded-3xl p-4 sm:p-5 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-sky-400 via-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-[0_0_18px_rgba(56,189,248,0.45)] border border-white/30 shrink-0">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <div>
                <h3 className="text-[16px] font-extrabold text-ink tracking-tight m-0 leading-tight">Map & Location</h3>
                <p className="text-[12px] text-muted-soft font-semibold m-0 mt-0.5">Search radius, map style & location</p>
              </div>
            </div>
            <div className="text-muted-soft opacity-60">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          {/* Search Radius */}
          <button
            type="button"
            onClick={cycleRadius}
            className="w-full flex items-center justify-between py-3 border-b border-hairline text-left group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="text-sky-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="22" y1="12" x2="18" y2="12" />
                  <line x1="6" y1="12" x2="2" y2="12" />
                  <line x1="12" y1="6" x2="12" y2="2" />
                  <line x1="12" y1="22" x2="12" y2="18" />
                </svg>
              </div>
              <div className="text-[14px] font-bold text-ink">Search Radius</div>
            </div>
            <div className="flex items-center gap-1.5 text-[13px] font-extrabold text-muted-soft group-hover:text-ink transition-colors">
              <span>{radiusOptions[radiusIndex]}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </button>

          {/* Map Style */}
          <button
            type="button"
            onClick={cycleMapTheme}
            className="w-full flex items-center justify-between py-3 border-b border-hairline text-left group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="text-sky-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                  <line x1="8" y1="2" x2="8" y2="18" />
                  <line x1="16" y1="6" x2="16" y2="22" />
                </svg>
              </div>
              <div className="text-[14px] font-bold text-ink">Map Style</div>
            </div>
            <div className="flex items-center gap-1.5 text-[13px] font-extrabold text-muted-soft group-hover:text-ink transition-colors">
              <span>{activeThemeName}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </button>

          {/* Auto-detect My Location */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-sky-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C12.95 21.5 20 15.4 20 10a8 8 0 0 0-8-8z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Auto-detect My Location</div>
                <div className="text-[11.5px] text-muted-soft">Find me on the map</div>
              </div>
            </div>
            <Switch
              checked={autoDetectLocation}
              onChange={() => handleToggle(setAutoDetectLocation, 'geoai_auto_detect_location')}
            />
          </div>

          {/* Show Closed Facilities */}
          <div className="flex items-center justify-between pt-3">
            <div className="flex items-center gap-3">
              <div className="text-sky-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
                  <line x1="12" y1="2" x2="12" y2="12" />
                  <line x1="2" y1="2" x2="22" y2="22" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Show Closed Facilities</div>
                <div className="text-[11.5px] text-muted-soft">Display closed or unavailable washrooms</div>
              </div>
            </div>
            <Switch
              checked={showClosedFacilities}
              onChange={() => handleToggle(setShowClosedFacilities, 'geoai_show_closed')}
            />
          </div>
        </div>

        {/* Card 3: AI Recommendation */}
        <div className="glass-panel rounded-3xl p-4 sm:p-5 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-pink-500 via-fuchsia-600 to-purple-600 flex items-center justify-center text-white shadow-[0_0_18px_rgba(217,70,239,0.45)] border border-white/30 shrink-0">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
                  <path d="M5 3v4" />
                  <path d="M19 17v4" />
                  <path d="M3 5h4" />
                  <path d="M17 19h4" />
                </svg>
              </div>
              <div>
                <h3 className="text-[16px] font-extrabold text-ink tracking-tight m-0 leading-tight">AI Recommendation</h3>
                <p className="text-[12px] text-muted-soft font-semibold m-0 mt-0.5">Personalise your best matches</p>
              </div>
            </div>
            <div className="text-muted-soft opacity-60">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          {/* Smart Recommendations */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-fuchsia-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z" />
                  <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Smart Recommendations</div>
                <div className="text-[11.5px] text-muted-soft">Use AI to rank the best options</div>
              </div>
            </div>
            <Switch
              checked={smartRecommendations}
              onChange={() => handleToggle(setSmartRecommendations, 'geoai_smart_recs')}
            />
          </div>

          {/* Explain Recommendations */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-fuchsia-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Explain Recommendations</div>
                <div className="text-[11.5px] text-muted-soft">Show why a washroom is suggested</div>
              </div>
            </div>
            <Switch
              checked={explainRecommendations}
              onChange={() => handleToggle(setExplainRecommendations, 'geoai_explain_recs')}
            />
          </div>

          {/* Priority Section */}
          <div className="pt-3.5 space-y-3">
            <div>
              <div className="text-[13px] font-extrabold text-ink">Priority</div>
              <div className="text-[11.5px] text-muted-soft font-medium">What matters most to you?</div>
            </div>

            {/* Distance Slider */}
            <div className="flex items-center justify-between gap-3 pt-1">
              <div className="flex items-center gap-2.5 w-36 shrink-0">
                <div className="text-fuchsia-400">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                </div>
                <span className="text-[13px] font-bold text-ink truncate">Distance</span>
              </div>
              <div className="flex-1 flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={distanceWeight}
                  onChange={(e) => handleSliderChange(Number(e.target.value), setDistanceWeight, 'geoai_weight_distance')}
                  style={{ background: getSliderBg(distanceWeight) }}
                  className="priority-slider flex-1"
                />
                <span className="text-[12px] font-extrabold text-muted-soft w-9 text-right">{distanceWeight}%</span>
              </div>
            </div>

            {/* Rating & Cleanliness Slider */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 w-36 shrink-0">
                <div className="text-fuchsia-400">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                  </svg>
                </div>
                <span className="text-[13px] font-bold text-ink truncate">Rating & Cleanliness</span>
              </div>
              <div className="flex-1 flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={ratingWeight}
                  onChange={(e) => handleSliderChange(Number(e.target.value), setRatingWeight, 'geoai_weight_rating')}
                  style={{ background: getSliderBg(ratingWeight) }}
                  className="priority-slider flex-1"
                />
                <span className="text-[12px] font-extrabold text-muted-soft w-9 text-right">{ratingWeight}%</span>
              </div>
            </div>

            {/* Availability Slider */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 w-36 shrink-0">
                <div className="text-fuchsia-400">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                </div>
                <span className="text-[13px] font-bold text-ink truncate">Availability</span>
              </div>
              <div className="flex-1 flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={availabilityWeight}
                  onChange={(e) => handleSliderChange(Number(e.target.value), setAvailabilityWeight, 'geoai_weight_availability')}
                  style={{ background: getSliderBg(availabilityWeight) }}
                  className="priority-slider flex-1"
                />
                <span className="text-[12px] font-extrabold text-muted-soft w-9 text-right">{availabilityWeight}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 4: Navigation */}
        <div className="glass-panel rounded-3xl p-4 sm:p-5 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-sky-400 via-blue-500 to-indigo-500 flex items-center justify-center text-white shadow-[0_0_18px_rgba(56,189,248,0.45)] border border-white/30 shrink-0">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="7" y1="17" x2="17" y2="7" />
                  <polyline points="7 7 17 7 17 17" />
                </svg>
              </div>
              <div>
                <h3 className="text-[16px] font-extrabold text-ink tracking-tight m-0 leading-tight">Navigation</h3>
                <p className="text-[12px] text-muted-soft font-semibold m-0 mt-0.5">Route and guidance</p>
              </div>
            </div>
            <div className="text-muted-soft opacity-60">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          {/* Walking Route */}
          <button
            type="button"
            onClick={cycleWalking}
            className="w-full flex items-center justify-between py-3 border-b border-hairline text-left group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="text-indigo-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 4a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" fill="currentColor" />
                  <path d="M6 22l3-7 3 3v4" />
                  <path d="M17 22l-3-9 2-4-4-2-2 3" />
                </svg>
              </div>
              <div className="text-[14px] font-bold text-ink">Walking Route</div>
            </div>
            <div className="flex items-center gap-1.5 text-[13px] font-extrabold text-muted-soft group-hover:text-ink transition-colors">
              <span>{walkingOptions[walkingIndex]}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </button>

          {/* Live Navigation Updates */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-indigo-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4.93 19.07a10 10 0 0 1 0-14.14" />
                  <path d="M7.76 16.24a6 6 0 0 1 0-8.48" />
                  <circle cx="12" cy="12" r="2" fill="currentColor" />
                  <path d="M16.24 7.76a6 6 0 0 1 0 8.48" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Live Navigation Updates</div>
                <div className="text-[11.5px] text-muted-soft">Turn-by-turn directions</div>
              </div>
            </div>
            <Switch
              checked={liveUpdates}
              onChange={() => handleToggle(setLiveUpdates, 'geoai_live_nav')}
            />
          </div>

          {/* Voice Guidance */}
          <div className="flex items-center justify-between py-3 border-b border-hairline">
            <div className="flex items-center gap-3">
              <div className="text-indigo-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </svg>
              </div>
              <div>
                <div className="text-[14px] font-bold text-ink">Voice Guidance</div>
                <div className="text-[11.5px] text-muted-soft">Audio navigation</div>
              </div>
            </div>
            <Switch
              checked={voiceGuidance}
              onChange={() => handleToggle(setVoiceGuidance, 'geoai_voice_guidance')}
            />
          </div>

          {/* Route Preference */}
          <button
            type="button"
            onClick={cycleRoutePref}
            className="w-full flex items-center justify-between pt-3 text-left group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="text-indigo-400">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="6" cy="19" r="3" />
                  <path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15" />
                  <circle cx="18" cy="5" r="3" />
                </svg>
              </div>
              <div className="text-[14px] font-bold text-ink">Route Preference</div>
            </div>
            <div className="flex items-center gap-1.5 text-[13px] font-extrabold text-muted-soft group-hover:text-ink transition-colors">
              <span>{routePrefOptions[routePrefIndex]}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </button>
        </div>

      </div>
    </div>
  );
}

// Reusable toggle switch component with Pearl Glass aesthetic
function Switch({
  checked,
  onChange,
  id,
}: {
  checked: boolean;
  onChange: () => void;
  id?: string;
}) {
  return (
    <button
      type="button"
      id={id}
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className={`relative w-[48px] h-[28px] rounded-full transition-all duration-300 cursor-pointer border shrink-0 ${
        checked
          ? 'bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-500 border-purple-400/60 shadow-[0_0_14px_rgba(168,85,247,0.55)]'
          : 'bg-white/10 dark:bg-slate-700/60 border-white/20'
      }`}
    >
      <div
        className={`absolute top-[3px] w-5 h-5 bg-white rounded-full transition-transform duration-300 shadow-md ${
          checked ? 'translate-x-[23px]' : 'translate-x-[3px]'
        }`}
      />
    </button>
  );
}
