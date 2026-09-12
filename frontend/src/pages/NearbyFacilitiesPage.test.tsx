/* eslint-disable @typescript-eslint/no-explicit-any */
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NearbyFacilitiesPage } from './NearbyFacilitiesPage';
import { SearchProvider } from '../context/SearchContext';
import * as SearchContextModule from '../context/SearchContext';
import { setupLeafletMock, resetLeafletMock } from '../test-utils/leafletMock';
import { getNearbyWashrooms } from '../api/washrooms';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import {
  DEFAULT_RADIUS_M,
  MAX_RADIUS_M,
  RADIUS_EXPAND_MULTIPLIER,
  SERVICE_UNAVAILABLE_MESSAGE
} from '../constants/search';

vi.mock('react-leaflet', () => import('../test-utils/leafletMock'));

vi.mock('../api/washrooms', () => ({
  getNearbyWashrooms: vi.fn(),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

interface MockSearchState {
  selectedCategory: string | null;
  selectedAudience: 'VISITOR' | 'STAFF' | null;
  location: { lat: number; lon: number; accuracy: number } | null;
  locationStatus: 'idle' | 'requesting' | 'granted' | 'denied' | 'unavailable';
}

const defaultState: MockSearchState = {
  selectedCategory: 'UNISEX',
  selectedAudience: null,
  location: { lat: 10, lon: 20, accuracy: 10 },
  locationStatus: 'granted',
};

let queryClient: QueryClient;

const renderWithContext = (state: MockSearchState = defaultState) => {
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
    setupLeafletMock();
  });

  afterEach(() => {
    resetLeafletMock();
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
    vi.mocked(getNearbyWashrooms).mockReturnValue(new Promise(() => {})); // Never resolves
    renderWithContext();
    expect(screen.getByText('Finding washrooms near you...')).toBeInTheDocument();
  });

  it('renders EmptyState and expands radius on click', async () => {
    const user = userEvent.setup();
    vi.mocked(getNearbyWashrooms).mockResolvedValue([]);

    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText('No washrooms match this search.')).toBeInTheDocument();
    });

    const button = screen.getByRole('button', { name: 'Search wider area' });
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();

    // First call
    expect(getNearbyWashrooms).toHaveBeenCalledTimes(1);
    expect(getNearbyWashrooms).toHaveBeenCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M
    });

    await user.click(button);

    // Second call
    await waitFor(() => {
      expect(getNearbyWashrooms).toHaveBeenCalledTimes(2);
    });
    expect(getNearbyWashrooms).toHaveBeenLastCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M * RADIUS_EXPAND_MULTIPLIER
    });
  });

  it('disables Search wider area button when MAX_RADIUS_M is reached', async () => {
    const user = userEvent.setup();
    vi.mocked(getNearbyWashrooms).mockResolvedValue([]);

    renderWithContext();

    // Default is 1000. 1000 -> 2000 -> 4000 -> 8000 -> 10000 (4 clicks)
    for (let i = 0; i < 4; i++) {
      const button = await screen.findByRole('button', { name: 'Search wider area' });
      await user.click(button);
    }

    const disabledButton = await screen.findByRole('button', { name: 'Search wider area' });
    expect(disabledButton).toBeDisabled();

    expect(getNearbyWashrooms).toHaveBeenLastCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: MAX_RADIUS_M
    });
  });

  it('renders 503 ErrorState exactly', async () => {
    vi.mocked(getNearbyWashrooms).mockRejectedValue({ response: { status: 503 } });
    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeInTheDocument();
    });
  });

  it('renders generic ErrorState for non-503 errors', async () => {
    vi.mocked(getNearbyWashrooms).mockRejectedValue(new Error('Network error'));
    renderWithContext();

    await waitFor(() => {
      expect(screen.getByText('An error occurred while fetching washrooms.')).toBeInTheDocument();
    });
    expect(screen.queryByText(SERVICE_UNAVAILABLE_MESSAGE)).not.toBeInTheDocument();
  });

  it('renders MapView and FacilityList with real data, selectedAudience is passed correctly to the api call', async () => {
    const mockData = [
      { id: 100, name: 'Real API Facility', category: 'UNISEX', status: 'OPEN', rating: 5, distance_m: 50, latitude: 10.1, longitude: 20.1 } as any
    ];
    vi.mocked(getNearbyWashrooms).mockResolvedValue(mockData);

    renderWithContext({ ...defaultState, selectedAudience: 'VISITOR' });

    await waitFor(() => {
      expect(screen.queryByText('Finding washrooms near you...')).not.toBeInTheDocument();
    });

    // selectedAudience SHOULD be passed to API wrapper (the wrapper drops it if undefined, but component passes it)
    expect(getNearbyWashrooms).toHaveBeenCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M, audience: 'VISITOR'
    });

    // Check List
    expect(screen.getAllByText('Real API Facility')[0]).toBeInTheDocument();

    // Check Map
    expect(screen.queryByText('Map unavailable — showing list only')).not.toBeInTheDocument();
  });
  
  it('does NOT redirect when selectedAudience is null, fetches normally', async () => {
    const mockData = [
      { id: 101, name: 'Real API Facility 2', category: 'UNISEX', status: 'OPEN', rating: 4, distance_m: 50, latitude: 10.1, longitude: 20.1 } as any
    ];
    vi.mocked(getNearbyWashrooms).mockResolvedValue(mockData);

    renderWithContext({ ...defaultState, selectedAudience: null });

    await waitFor(() => {
      expect(screen.queryByText('Finding washrooms near you...')).not.toBeInTheDocument();
    });
    
    expect(mockNavigate).not.toHaveBeenCalledWith('/', { replace: true });
    
    expect(getNearbyWashrooms).toHaveBeenCalledWith({
      lat: 10, lon: 20, category: 'UNISEX', radius_m: DEFAULT_RADIUS_M
    });
  });
});
