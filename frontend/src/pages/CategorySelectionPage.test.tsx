import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { CategorySelectionPage } from './CategorySelectionPage';
import { SearchProvider } from '../context/SearchContext';
import { MemoryRouter } from 'react-router-dom';
import * as useCategoriesModule from '../hooks/useCategories';
import { useSearchContext } from '../context/SearchContext';
import React from 'react';

vi.mock('../hooks/useCategories');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function LocationSpy() {
  const { state } = useSearchContext();
  return <div data-testid="loc-spy">{state.location ? `${state.location.lat},${state.location.lon}` : 'null'}</div>;
}

describe('CategorySelectionPage', () => {
  let mockGetCurrentPosition: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockNavigate.mockClear();
    mockGetCurrentPosition = vi.fn();
    Object.defineProperty(global.navigator, 'geolocation', {
      value: { getCurrentPosition: mockGetCurrentPosition },
      writable: true,
    });
  });

  it('renders category buttons from mocked API data', () => {
    vi.mocked(useCategoriesModule.useCategories).mockReturnValue({
      data: [
        { id: 1, code: 'TEST_CAT_1', label: 'Test Category 1' },
        { id: 2, code: 'TEST_CAT_2', label: 'Test Category 2' },
      ],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <SearchProvider>
        <MemoryRouter>
          <CategorySelectionPage />
        </MemoryRouter>
      </SearchProvider>
    );

    expect(screen.getByText('Test Category 1')).toBeDefined();
    expect(screen.getByText('Test Category 2')).toBeDefined();
    // Prove Male/Female/Unisex are not hardcoded
    expect(screen.queryByText('Male')).toBeNull();
  });

  it('triggers geolocation request after category selection, not before', async () => {
    vi.mocked(useCategoriesModule.useCategories).mockReturnValue({
      data: [{ id: 1, code: 'MEN', label: 'Men\'s' }],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <SearchProvider>
        <MemoryRouter>
          <CategorySelectionPage />
        </MemoryRouter>
      </SearchProvider>
    );

    expect(mockGetCurrentPosition).not.toHaveBeenCalled();

    // Click Visitor chip
    fireEvent.click(screen.getByText('Visitor'));

    expect(mockGetCurrentPosition).toHaveBeenCalled();
  });

  it('dispatches SET_LOCATION and navigates to /nearby once geolocation resolves', async () => {
    vi.mocked(useCategoriesModule.useCategories).mockReturnValue({
      data: [{ id: 1, code: 'MEN', label: 'Men\'s' }],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    // Mock geolocation to instantly resolve successfully
    mockGetCurrentPosition.mockImplementation((success) => {
      success({ coords: { latitude: 10, longitude: 20, accuracy: 5 } });
    });

    render(
      <SearchProvider>
        <MemoryRouter>
          <CategorySelectionPage />
          <LocationSpy />
        </MemoryRouter>
      </SearchProvider>
    );

    // Click Category card
    fireEvent.click(screen.getByText("Men's"));

    // Navigate should be called with /nearby
    expect(mockNavigate).toHaveBeenCalledWith('/nearby');
    // Location spy should reflect the updated SearchContext state
    expect(screen.getByTestId('loc-spy').textContent).toBe('10,20');
  });

  it('dispatches SET_LOCATION and navigates to /nearby when Nearby card is clicked', async () => {
    vi.mocked(useCategoriesModule.useCategories).mockReturnValue({
      data: [{ id: 1, code: 'MEN', label: 'Men\'s' }],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    mockGetCurrentPosition.mockImplementation((success) => {
      success({ coords: { latitude: 30, longitude: 40, accuracy: 5 } });
    });

    render(
      <SearchProvider>
        <MemoryRouter>
          <CategorySelectionPage />
          <LocationSpy />
        </MemoryRouter>
      </SearchProvider>
    );

    // Click Nearby card
    fireEvent.click(screen.getByText('Nearby'));

    expect(mockNavigate).toHaveBeenCalledWith('/nearby');
    expect(screen.getByTestId('loc-spy').textContent).toBe('30,40');
  });
});
