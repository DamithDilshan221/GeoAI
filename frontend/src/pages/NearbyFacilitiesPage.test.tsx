/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NearbyFacilitiesPage } from './NearbyFacilitiesPage';
import { SearchProvider } from '../context/SearchContext';
import * as SearchContextModule from '../context/SearchContext';
import { setupGoogleMapsMock } from '../test-utils/googleMapsMock';
import * as loaderModule from '../lib/googleMapsLoader';
import { getNearbyFacilities } from '../api/facilities';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import {
  DEFAULT_RADIUS_M,
  MAX_RADIUS_M,
  RADIUS_EXPAND_MULTIPLIER,
  EMPTY_NEARBY_MESSAGE,
  SERVICE_UNAVAILABLE_MESSAGE
} from '../constants/search';

vi.mock('../lib/googleMapsLoader', () => ({
  loadMapsLibrary: vi.fn().mockImplementation(() => Promise.resolve(global.google.maps)),
  loadMarkerLibrary: vi.fn().mockImplementation(() => Promise.resolve(global.google.maps.marker)),
}));

vi.mock('../api/facilities', () => ({
  getNearbyFacilities: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const defaultState = {
  selectedCategory: 'UNISEX',
  accessibleOnly: false,
  location: { lat: 10, lon: 20, accuracy: 10 },
  locationStatus: 'granted' as const,
};

let queryClient: QueryClient;

const renderWithContext = (state = defaultState) => {
  queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  vi.spyOn(SearchContextModule, 'useSearchContext').mockReturnValue({
    state: state as any,
    dispatch: vi.fn(),
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <SearchProvider>
          <NearbyFacilitiesPage />
        </SearchProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('NearbyFacilitiesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupGoogleMapsMock();
    vi.mocked(loaderModule.loadMapsLibrary).mockResolvedValue(global.google.maps as any);
    vi.mocked(loaderModule.loadMarkerLibrary).mockResolvedValue(global.google.maps.marker as any);
  });

  it('redirects to / when location is null', () => {
    renderWithContext({ ...defaultState, location: null });
    expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
  });

  it('redirects to / when selectedCategory is null', () => {
    renderWithContext({ ...defaultState, selectedCategory: null });
    expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true });
  });

  it('renders LoadingState when query is pending', () => {
    vi.mocked(getNearbyFacilities).mockReturnValue(new Promise(() => {})); // Never resolves
    renderWithContext();
    expect(screen.getByText('Finding facilities near you...')).toBeInTheDocument();
  });

  it('renders EmptyState and expands radius on click', async () => {
    const user = userEvent.setup();
    vi.mocked(getNearbyFacilities).mockResolvedValue([]);

    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText(EMPTY_NEARBY_MESSAGE)).toBeInTheDocument();
    });

    const button = screen.getByRole('button', { name: 'Search wider area' });
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();

    // First call
    expect(getNearbyFacilities).toHaveBeenCalledTimes(1);
    expect(getNearbyFacilities).toHaveBeenCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M
    });

    await user.click(button);

    // Second call
    await waitFor(() => {
      expect(getNearbyFacilities).toHaveBeenCalledTimes(2);
    });
    expect(getNearbyFacilities).toHaveBeenLastCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M * RADIUS_EXPAND_MULTIPLIER
    });
  });

  it('disables Search wider area button when MAX_RADIUS_M is reached', async () => {
    const user = userEvent.setup();
    vi.mocked(getNearbyFacilities).mockResolvedValue([]);

    renderWithContext();

    // Default is 1000. 1000 -> 2000 -> 4000 -> 8000 -> 10000 (4 clicks)
    for (let i = 0; i < 4; i++) {
      const button = await screen.findByRole('button', { name: 'Search wider area' });
      await user.click(button);
    }

    const disabledButton = await screen.findByRole('button', { name: 'Search wider area' });
    expect(disabledButton).toBeDisabled();

    expect(getNearbyFacilities).toHaveBeenLastCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: MAX_RADIUS_M
    });
  });

  it('renders 503 ErrorState exactly', async () => {
    vi.mocked(getNearbyFacilities).mockRejectedValue({ response: { status: 503 } });
    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeInTheDocument();
    });
  });

  it('renders generic ErrorState for non-503 errors', async () => {
    vi.mocked(getNearbyFacilities).mockRejectedValue(new Error('Network error'));
    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText('An error occurred while fetching facilities.')).toBeInTheDocument();
    });
    expect(screen.queryByText(SERVICE_UNAVAILABLE_MESSAGE)).not.toBeInTheDocument();
  });

  it('renders MapView and FacilityList with real data, accessibleOnly has no effect', async () => {
    const mockData = [
      { id: 100, name: 'Real API Facility', category: 'UNISEX', status: 'OPEN', rating: 5, distance_m: 50, latitude: 10.1, longitude: 20.1 } as any
    ];
    vi.mocked(getNearbyFacilities).mockResolvedValue(mockData);

    renderWithContext({ ...defaultState, accessibleOnly: true });

    await waitFor(() => {
      expect(screen.queryByText('Finding facilities near you...')).not.toBeInTheDocument();
    });

    // accessibleOnly should NOT be passed to API
    expect(getNearbyFacilities).toHaveBeenCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M
    });

    // Check List
    expect(screen.getByText('Real API Facility')).toBeInTheDocument();

    // Check Map
    expect(screen.queryByText('Map unavailable — showing list only')).not.toBeInTheDocument();
  });
});
