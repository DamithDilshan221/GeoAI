import '@testing-library/jest-dom/vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { SettingsView } from './SettingsView';

describe('SettingsView', () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.className = '';
  });

  it('renders all 4 main settings cards', () => {
    render(<SettingsView />);
    expect(screen.getByText('Appearance')).toBeInTheDocument();
    expect(screen.getByText('Map & Location')).toBeInTheDocument();
    expect(screen.getByText('AI Recommendation')).toBeInTheDocument();
    expect(screen.getByText('Navigation')).toBeInTheDocument();
  });

  it('toggles theme mode between Dark, Light, and System', () => {
    render(<SettingsView />);
    const lightBtn = screen.getByRole('button', { name: /Light/i });
    fireEvent.click(lightBtn);
    expect(document.body.classList.contains('day')).toBe(true);
    expect(localStorage.getItem('theme_mode')).toBe('light');

    const darkBtn = screen.getByRole('button', { name: /Dark/i });
    fireEvent.click(darkBtn);
    expect(document.body.classList.contains('day')).toBe(false);
    expect(localStorage.getItem('theme_mode')).toBe('dark');
  });

  it('renders priority sliders and updates weights', () => {
    render(<SettingsView />);
    expect(screen.getByText('Distance')).toBeInTheDocument();
    expect(screen.getByText('Rating & Cleanliness')).toBeInTheDocument();
    expect(screen.getByText('Availability')).toBeInTheDocument();

    const sliders = screen.getAllByRole('slider');
    expect(sliders.length).toBe(3);

    fireEvent.change(sliders[0], { target: { value: '60' } });
    expect(localStorage.getItem('geoai_weight_distance')).toBe('60');
  });

  it('cycles through radius and walking options when clicked', () => {
    render(<SettingsView />);
    const radiusBtn = screen.getByRole('button', { name: /Search Radius/i });
    expect(radiusBtn).toHaveTextContent('500 m');

    fireEvent.click(radiusBtn);
    expect(radiusBtn).toHaveTextContent('1000 m');

    const walkingBtn = screen.getByRole('button', { name: /Walking Route/i });
    expect(walkingBtn).toHaveTextContent('Walking');
    fireEvent.click(walkingBtn);
    expect(walkingBtn).toHaveTextContent('Accessible');
  });
});
