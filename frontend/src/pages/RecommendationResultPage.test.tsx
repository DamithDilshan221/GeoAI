/* eslint-disable @typescript-eslint/no-explicit-any */
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecommendationResultPage } from './RecommendationResultPage';
import * as SearchContextModule from '../context/SearchContext';
import * as useRecommendationModule from '../hooks/useRecommendation';
import type { RecommendationResponse } from '../types/recommendation';
import { SERVICE_UNAVAILABLE_MESSAGE } from '../constants/search';

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return { ...actual, Navigate: ({ to }: { to: string }) => <div data-testid="redirect" data-to={to} /> };
});

vi.mock('../hooks/useRecommendation', () => ({
  useRecommendation: vi.fn(),
}));

// Mock NavigationOverlay to avoid deep OSRM chain in unit tests
vi.mock('../components/navigation/NavigationOverlay', () => ({
  NavigationOverlay: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="navigation-overlay">
      <button onClick={onClose} data-testid="overlay-close">Close</button>
    </div>
  ),
}));

const mockState = (overrides = {}) => ({
  selectedCategory: 'MALE',
  location: { lat: 6.9, lon: 79.8, accuracy: 10 },
  locationStatus: 'granted' as const,
  ...overrides,
});

const renderPage = (state: ReturnType<typeof mockState> = mockState()) => {
  vi.spyOn(SearchContextModule, 'useSearchContext').mockReturnValue({
    state: state as any,
    dispatch: vi.fn(),
  });

  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>
        <RecommendationResultPage />
      </QueryClientProvider>
    </MemoryRouter>,
  );
};

const mockUseRecommendation = (overrides: Partial<ReturnType<typeof useRecommendationModule.useRecommendation>> = {}) => {
  vi.mocked(useRecommendationModule.useRecommendation).mockReturnValue({
    isLoading: false,
    isError: false,
    data: undefined,
    refetch: vi.fn(),
    ...overrides,
  } as any);
};

const sampleFacility = {
  id: 1,
  name: 'Main Washroom',
  category: 'MALE',
  status: 'OPEN' as const,
  rating: 4.5,
  latitude: 7.2545,
  longitude: 80.5965,
  distance_m: 120,
  estimated_time_s: 100,
  travel_source: 'network' as const,
  predicted_usage: 3,
  crowd_level: 'LOW',
  prediction_source: 'heuristic',
  recommendation_score: 88.97,
  rank_position: 1,
};

const sampleResponse: RecommendationResponse = {
  recommended_facility: sampleFacility,
  ranked_facilities: [sampleFacility],
  explanation: 'Recommended because it is very close to your location.',
  message: null,
};

describe('RecommendationResultPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(globalThis.navigator, 'geolocation', {
      value: {
        getCurrentPosition: vi.fn((success) =>
          success({ coords: { latitude: 6.9, longitude: 79.8, accuracy: 10 } }),
        ),
      },
      writable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('redirects to / when no location or category', () => {
    mockUseRecommendation();
    renderPage(mockState({ location: null, selectedCategory: null }));
    expect(screen.getByTestId('redirect')).toHaveAttribute('data-to', '/');
  });

  it('shows loading state', () => {
    mockUseRecommendation({ isLoading: true });
    renderPage();
    expect(screen.getByText(/generating optimal recommendation/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockUseRecommendation({ isError: true });
    renderPage();
    expect(screen.getByText(/failed to fetch/i)).toBeInTheDocument();
  });

  it('shows message when no facilities found', () => {
    mockUseRecommendation({
      data: {
        recommended_facility: null,
        ranked_facilities: [],
        explanation: null,
        message: 'No suitable facilities were found within the current search radius.',
      } as RecommendationResponse,
    });
    renderPage();
    expect(screen.getByText(/no suitable facilities/i)).toBeInTheDocument();
  });

  it('renders top recommendation name, explanation, and stats', async () => {
    mockUseRecommendation({ data: sampleResponse });
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Main Washroom')).toBeInTheDocument();
      expect(screen.getByText(/Recommended because it is very close/)).toBeInTheDocument();
      expect(screen.getByText('120 m')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
    });
  });

  it('does NOT show "estimated" in time when travel_source is network', async () => {
    mockUseRecommendation({ data: sampleResponse });
    renderPage();

    await waitFor(() => {
      const timeElements = screen.getAllByText(/min/i);
      expect(timeElements.every((el) => !el.textContent?.includes('estimated'))).toBe(true);
    });
  });

  it('shows "estimated" in time when travel_source is straight_line_estimate', async () => {
    const response: RecommendationResponse = {
      ...sampleResponse,
      recommended_facility: {
        ...sampleFacility,
        travel_source: 'straight_line_estimate',
      },
      ranked_facilities: [
        {
          ...sampleFacility,
          travel_source: 'straight_line_estimate',
        },
      ],
    };
    mockUseRecommendation({ data: response });
    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/estimated/i)).toBeInTheDocument();
    });
  });

  it('opens NavigationOverlay when Start Navigation is clicked and geolocation succeeds', async () => {
    mockUseRecommendation({ data: sampleResponse });
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Main Washroom')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('Start Navigation'));

    await waitFor(() => {
      expect(screen.getByTestId('navigation-overlay')).toBeInTheDocument();
    });
  });

  it('shows geolocation error when permission denied on Start Navigation', async () => {
    Object.defineProperty(globalThis.navigator, 'geolocation', {
      value: {
        getCurrentPosition: vi.fn((_, error) => error({ code: 1 })),
      },
      writable: true,
    });

    mockUseRecommendation({ data: sampleResponse });
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Main Washroom')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('Start Navigation'));

    await waitFor(() => {
      expect(screen.getByTestId('rec-nav-error')).toBeInTheDocument();
    });
  });

  it('shows SERVICE_UNAVAILABLE_MESSAGE when error status is 503', () => {
    mockUseRecommendation({
      isError: true,
      error: { response: { status: 503 } } as any,
    });
    renderPage();
    expect(screen.getByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeInTheDocument();
  });

  it('shows generic fallback message when error is non-503', () => {
    mockUseRecommendation({
      isError: true,
      error: { response: { status: 500 } } as any,
    });
    renderPage();
    expect(screen.getByText(/failed to fetch recommendations/i)).toBeInTheDocument();
    expect(screen.queryByText(SERVICE_UNAVAILABLE_MESSAGE)).toBeNull();
  });
});
