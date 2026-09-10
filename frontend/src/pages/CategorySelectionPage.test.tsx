import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { CategorySelectionPage } from './CategorySelectionPage';
import { SearchProvider } from '../context/SearchContext';
import { MemoryRouter } from 'react-router-dom';
import * as useCategoriesModule from '../hooks/useCategories';
import React from 'react';

vi.mock('../hooks/useCategories');

describe('CategorySelectionPage', () => {
  let mockGetCurrentPosition: ReturnType<typeof vi.fn>;

  beforeEach(() => {
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
});
