import { render, screen, fireEvent } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { AppShell } from './AppShell';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';

describe('AppShell', () => {
  it('renders header and content', () => {
    render(
      <MemoryRouter>
        <AppShell>
          <div data-testid="test-content">Content</div>
        </AppShell>
      </MemoryRouter>
    );

    expect(screen.getByText('RestNav')).toBeDefined();
    expect(screen.getByTestId('test-content')).toBeDefined();
    expect(screen.getByTestId('theme-toggle-btn')).toBeDefined();
  });

  it('toggles theme between dark and light on click', () => {
    render(
      <MemoryRouter>
        <AppShell>
          <div>Content</div>
        </AppShell>
      </MemoryRouter>
    );

    const toggleBtn = screen.getByTestId('theme-toggle-btn');
    expect(toggleBtn).toBeDefined();

    // Reset initial state
    document.body.classList.remove('day');

    fireEvent.click(toggleBtn);
    expect(document.body.classList.contains('day')).toBe(true);
    expect(localStorage.getItem('theme_mode')).toBe('light');

    fireEvent.click(toggleBtn);
    expect(document.body.classList.contains('day')).toBe(false);
    expect(localStorage.getItem('theme_mode')).toBe('dark');
  });
});
