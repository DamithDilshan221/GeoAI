import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { FacilityDetailsPage } from './FacilityDetailsPage';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import * as useFacilityModule from '../hooks/useFacility';
import React from 'react';
import { SERVICE_UNAVAILABLE_MESSAGE } from '../constants/search';

vi.mock('../hooks/useFacility');

// Mock Leaflet (MapView) to avoid jsdom issues
vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="map-container">{children}</div>
  ),
  TileLayer: () => <div data-testid="tile-layer" />,
  Marker: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="marker">{children}</div>
  ),
  Tooltip: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="tooltip">{children}</div>
  ),
  ZoomControl: () => <div data-testid="zoom-control" />,
  Polyline: () => <div data-testid="polyline" />,
  useMap: () => ({ fitBounds: vi.fn() }),
}));

// Mock NavigationOverlay to avoid deep OSRM/geolocation chain in unit tests
vi.mock('../components/navigation/NavigationOverlay', () => ({
  NavigationOverlay: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="navigation-overlay">
      <button onClick={onClose} data-testid="overlay-close">Close</button>
    </div>
  ),
}));

const makeFacility = (overrides = {}) => ({
  id: 1,
  name: 'Accessible Restroom',
  location_name: 'Main Building',
  category: 'UNISEX',
  audience: 'VISITOR',
  status: 'OPEN',
  status_updated_at: '2023-01-01',
  rating: 5,
  total_stalls: 6,
  fixtures: { attached: 2, normal: 4 },
  data_source: 'REAL',
  latitude: 7.2545,
  longitude: 80.5965,
  ...overrides,
});

import { SearchProvider } from '../context/SearchContext';

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={['/facilities/1']}>
      <SearchProvider>
        <Routes>
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
        </Routes>
      </SearchProvider>
    </MemoryRouter>,
  );

describe('FacilityDetailsPage', () => {
  beforeEach(() => {
    // Default geolocation mock
    Object.defineProperty(global.navigator, 'geolocation', {
      value: {
        getCurrentPosition: vi.fn((success) =>
          success({ coords: { latitude: 7.2545, longitude: 80.5965, accuracy: 10 } }),
        ),
      },
      writable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders fixtures grid when fixtures exist', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: makeFacility(),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();

    // The facility name appears in both the h2 heading and the map Tooltip — query by role
    expect(screen.getByRole('heading', { name: 'Accessible Restroom' })).toBeDefined();
    expect(screen.getByText('attached')).toBeDefined();
    expect(screen.getByText('2')).toBeDefined();
    expect(screen.getByText('normal')).toBeDefined();
    expect(screen.getByText('4')).toBeDefined();
  });

  it('renders graceful empty state when fixtures is empty', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: makeFacility({ fixtures: {}, total_stalls: 0 }),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    expect(screen.getByText('No fixture details available')).toBeDefined();
  });

  it('renders "not found" variant on 404', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: { response: { status: 404 } },
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    expect(screen.getByText('Washroom Not Found')).toBeDefined();
    expect(screen.queryByText('Failed to load washroom details.')).toBeNull();
  });

  it('opens NavigationOverlay when Navigate button clicked and geolocation succeeds', async () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: makeFacility(),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    const navBtn = screen.getByText('Navigate');
    await userEvent.click(navBtn);

    await waitFor(() => {
      expect(screen.getByTestId('navigation-overlay')).toBeInTheDocument();
    });
  });

  it('shows geolocation error when permission denied', async () => {
    Object.defineProperty(global.navigator, 'geolocation', {
      value: {
        getCurrentPosition: vi.fn((_, error) => error({ code: 1 })),
      },
      writable: true,
    });

    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: makeFacility(),
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    await userEvent.click(screen.getByText('Navigate'));

    await waitFor(() => {
      expect(screen.getByTestId('nav-error')).toBeInTheDocument();
    });
  });

  it('shows SERVICE_UNAVAILABLE_MESSAGE when error status is 503', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: { response: { status: 503 } },
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    expect(screen.getByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeInTheDocument();
    expect(screen.queryByText('Failed to load washroom details.')).toBeNull();
  });

  it('shows generic fallback message when error is non-503, non-404', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: { response: { status: 500 } },
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderPage();
    expect(screen.getByText('Failed to load washroom details.')).toBeInTheDocument();
    expect(screen.queryByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeNull();
  });
});
