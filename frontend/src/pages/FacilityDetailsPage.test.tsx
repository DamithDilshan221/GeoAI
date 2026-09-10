import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { FacilityDetailsPage } from './FacilityDetailsPage';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import * as useFacilityModule from '../hooks/useFacility';
import React from 'react';

vi.mock('../hooks/useFacility');

describe('FacilityDetailsPage', () => {
  it('renders fixtures grid when fixtures exist', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: {
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
        latitude: 0,
        longitude: 0,
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <MemoryRouter initialEntries={['/facilities/1']}>
        <Routes>
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Accessible Restroom')).toBeDefined();
    expect(screen.getByText('attached')).toBeDefined();
    expect(screen.getByText('2')).toBeDefined();
    expect(screen.getByText('normal')).toBeDefined();
    expect(screen.getByText('4')).toBeDefined();
  });

  it('renders graceful empty state when fixtures is empty', () => {
    vi.mocked(useFacilityModule.useFacility).mockReturnValue({
      data: {
        id: 1,
        name: 'Empty Restroom',
        location_name: 'Main Building',
        category: 'UNISEX',
        audience: 'VISITOR',
        status: 'OPEN',
        status_updated_at: '2023-01-01',
        rating: 5,
        total_stalls: 0,
        fixtures: {},
        data_source: 'REAL',
        latitude: 0,
        longitude: 0,
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    render(
      <MemoryRouter initialEntries={['/facilities/1']}>
        <Routes>
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );

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

    render(
      <MemoryRouter initialEntries={['/facilities/999']}>
        <Routes>
          <Route path="/facilities/:id" element={<FacilityDetailsPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Washroom Not Found')).toBeDefined();
    // Does not render generic error message
    expect(screen.queryByText('Failed to load washroom details.')).toBeNull();
  });
});
