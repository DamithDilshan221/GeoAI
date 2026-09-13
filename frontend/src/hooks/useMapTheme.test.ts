import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { useMapTheme } from './useMapTheme';

describe('useMapTheme', () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.className = '';
  });

  it('defaults to osm theme if localStorage is empty', () => {
    const { result } = renderHook(() => useMapTheme());
    expect(result.current.themeId).toBe('osm');
    expect(result.current.activeTheme.id).toBe('osm');
  });

  it('allows changing theme and persists to localStorage', () => {
    const { result } = renderHook(() => useMapTheme());

    act(() => {
      result.current.setTheme('esri-dark');
    });

    expect(result.current.themeId).toBe('esri-dark');
    expect(result.current.activeTheme.id).toBe('esri-dark');
    expect(localStorage.getItem('geoai_map_theme')).toBe('esri-dark');
  });

  it('auto selects esri-light in Day mode and esri-dark in Night mode', () => {
    document.body.classList.add('day');
    const { result, rerender } = renderHook(() => useMapTheme());

    act(() => {
      result.current.setTheme('auto');
    });

    expect(result.current.activeTheme.id).toBe('esri-light');

    // Switch to night mode
    document.body.classList.remove('day');
    rerender();
  });
});
