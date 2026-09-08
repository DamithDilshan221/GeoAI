import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import * as useCategoriesModule from './hooks/useCategories';

vi.mock('./hooks/useCategories');

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <App />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('App', () => {
  it('renders the Category Selection page content at root', () => {
    vi.mocked(useCategoriesModule.useCategories).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);

    renderApp();
    expect(screen.getByText(/Find a Facility/i)).toBeDefined();
    expect(screen.getByText(/Select what you're looking for/i)).toBeDefined();
  });
});

