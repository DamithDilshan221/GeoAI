import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { SearchProvider, useSearchContext } from './SearchContext';
import React, { useEffect } from 'react';

function TestComponent() {
  const { state, dispatch } = useSearchContext();
  
  useEffect(() => {
    dispatch({ type: 'SET_CATEGORY', payload: 'FEMALE' });
    dispatch({ type: 'SET_AUDIENCE', payload: 'VISITOR' });
  }, [dispatch]);

  return (
    <div>
      <span data-testid="cat">{state.selectedCategory}</span>
      <span data-testid="aud">{state.selectedAudience}</span>
    </div>
  );
}

describe('SearchContext', () => {
  it('updates state via dispatch', () => {
    render(
      <SearchProvider>
        <TestComponent />
      </SearchProvider>
    );

    expect(screen.getByTestId('cat').textContent).toBe('FEMALE');
    expect(screen.getByTestId('aud').textContent).toBe('VISITOR');
  });

  it('throws if useSearchContext is outside provider', () => {
    // Suppress console.error for expected error
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<TestComponent />)).toThrow('useSearchContext must be used within a SearchProvider');
    spy.mockRestore();
  });

  it('toggles saved facilities in state', () => {
    function ToggleHelper() {
      const { state, dispatch } = useSearchContext();
      return (
        <div>
          <span data-testid="count">{Object.keys(state.savedFacilities || {}).length}</span>
          <button
            onClick={() =>
              dispatch({
                type: 'TOGGLE_SAVED',
                payload: {
                  id: 1,
                  name: 'Test Fac',
                  category: 'MALE',
                  status: 'OPEN',
                  rating: 4.5,
                },
              })
            }
          >
            Toggle
          </button>
        </div>
      );
    }

    render(
      <SearchProvider>
        <ToggleHelper />
      </SearchProvider>
    );

    expect(screen.getByTestId('count').textContent).toBe('0');
    fireEvent.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByTestId('count').textContent).toBe('1');
    fireEvent.click(screen.getByRole('button', { name: 'Toggle' }));
    expect(screen.getByTestId('count').textContent).toBe('0');
  });
});
