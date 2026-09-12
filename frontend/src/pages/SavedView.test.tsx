import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { SavedView } from './SavedView';
import { SearchProvider, useSearchContext } from '../context/SearchContext';
import React, { useEffect } from 'react';

function PopulatedSavedHelper() {
  const { dispatch } = useSearchContext();

  useEffect(() => {
    dispatch({
      type: 'TOGGLE_SAVED',
      payload: {
        id: 42,
        name: 'Library 2nd Floor Male',
        category: 'MALE',
        status: 'OPEN',
        distance_m: 85,
        rating: 4.8,
        latitude: 7.2545,
        longitude: 80.5965,
        audience: 'VISITOR',
      },
    });
  }, [dispatch]);

  return <SavedView />;
}

describe('SavedView', () => {
  it('renders EmptyState when no facilities are saved', () => {
    render(
      <MemoryRouter>
        <SearchProvider>
          <SavedView />
        </SearchProvider>
      </MemoryRouter>
    );

    expect(
      screen.getByText(/No saved washrooms yet/i)
    ).toBeInTheDocument();
  });

  it('renders saved facilities from shared SearchContext', () => {
    render(
      <MemoryRouter>
        <SearchProvider>
          <PopulatedSavedHelper />
        </SearchProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Library 2nd Floor Male')).toBeInTheDocument();
    expect(screen.getByText('85 m')).toBeInTheDocument();
  });
});
