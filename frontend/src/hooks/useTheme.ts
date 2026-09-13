import { useState, useEffect, useCallback } from 'react';

export type ThemeMode = 'dark' | 'light' | 'system';

export function useTheme() {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    return (localStorage.getItem('theme_mode') as ThemeMode) || 'dark';
  });

  const [isDay, setIsDay] = useState<boolean>(() => {
    if (typeof document !== 'undefined') {
      return document.body.classList.contains('day');
    }
    return false;
  });

  const applyTheme = useCallback((mode: ThemeMode) => {
    setThemeModeState(mode);
    localStorage.setItem('theme_mode', mode);

    let dayActive: boolean;
    if (mode === 'light') {
      dayActive = true;
      document.body.classList.add('day');
    } else if (mode === 'dark') {
      dayActive = false;
      document.body.classList.remove('day');
    } else {
      const isSystemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      dayActive = !isSystemDark;
      if (dayActive) {
        document.body.classList.add('day');
      } else {
        document.body.classList.remove('day');
      }
    }
    setIsDay(dayActive);
    window.dispatchEvent(new CustomEvent('themechange', { detail: { mode, isDay: dayActive } }));
  }, []);

  const toggleTheme = useCallback(() => {
    // If currently Day/Light, switch to Dark. If Dark, switch to Light.
    const currentIsDay = document.body.classList.contains('day');
    const nextMode: ThemeMode = currentIsDay ? 'dark' : 'light';
    applyTheme(nextMode);
  }, [applyTheme]);

  useEffect(() => {
    const handleThemeChange = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail) {
        setThemeModeState(customEvent.detail.mode);
        setIsDay(customEvent.detail.isDay);
      } else {
        setIsDay(document.body.classList.contains('day'));
        setThemeModeState((localStorage.getItem('theme_mode') as ThemeMode) || 'dark');
      }
    };

    window.addEventListener('themechange', handleThemeChange);
    return () => window.removeEventListener('themechange', handleThemeChange);
  }, []);

  return { themeMode, isDay, applyTheme, toggleTheme };
}
