import { useState, useEffect, useCallback } from 'react';
import { MAP_THEMES, DEFAULT_MAP_THEME_ID, type MapThemeOption } from '../constants/map';

const STORAGE_KEY = 'geoai_map_theme';

export function useMapTheme() {
  const [selectedThemeId, setSelectedThemeId] = useState<string>(() => {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_MAP_THEME_ID;
  });

  const [isDayMode, setIsDayMode] = useState<boolean>(() => {
    return document.body.classList.contains('day');
  });

  // Track body class changes (Day/Night mode toggles)
  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDayMode(document.body.classList.contains('day'));
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const setTheme = useCallback((themeId: string) => {
    setSelectedThemeId(themeId);
    localStorage.setItem(STORAGE_KEY, themeId);
  }, []);

  // Compute active theme config
  const activeTheme: MapThemeOption =
    selectedThemeId === 'auto'
      ? isDayMode
        ? MAP_THEMES['esri-light']
        : MAP_THEMES['esri-dark']
      : MAP_THEMES[selectedThemeId] || MAP_THEMES[DEFAULT_MAP_THEME_ID];

  return {
    themeId: selectedThemeId,
    activeTheme,
    setTheme,
    availableThemes: Object.values(MAP_THEMES),
    isDayMode,
  };
}
