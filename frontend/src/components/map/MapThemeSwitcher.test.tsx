import '@testing-library/jest-dom/vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MapThemeSwitcher } from './MapThemeSwitcher';
import { MAP_THEMES } from '../../constants/map';

describe('MapThemeSwitcher', () => {
  const availableThemes = Object.values(MAP_THEMES);

  it('renders trigger button with layer icon', () => {
    render(
      <MapThemeSwitcher
        currentThemeId="osm"
        availableThemes={availableThemes}
        onSelectTheme={vi.fn()}
      />
    );

    expect(screen.getByRole('button', { name: /change map style/i })).toBeInTheDocument();
    expect(screen.getByText('Layers')).toBeInTheDocument();
  });

  it('opens popup menu on click and lists all themes', () => {
    const onSelect = vi.fn();
    render(
      <MapThemeSwitcher
        currentThemeId="osm"
        availableThemes={availableThemes}
        onSelectTheme={onSelect}
      />
    );

    const trigger = screen.getByRole('button', { name: /change map style/i });
    fireEvent.click(trigger);

    expect(screen.getByText(/Map Basemaps/i)).toBeInTheDocument();
    expect(screen.getByText('Night Dark Canvas')).toBeInTheDocument();
    expect(screen.getByText('Clean Light Canvas')).toBeInTheDocument();
    expect(screen.getByText('Satellite Aerial')).toBeInTheDocument();
    expect(screen.getByText('OpenTopo Terrain')).toBeInTheDocument();

    // Select Night Dark Canvas
    fireEvent.click(screen.getByText('Night Dark Canvas'));
    expect(onSelect).toHaveBeenCalledWith('esri-dark');
  });
});
