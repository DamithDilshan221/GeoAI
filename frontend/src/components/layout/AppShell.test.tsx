import { render, screen } from '@testing-library/react';
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

    expect(screen.getByText('Campus Washroom Finder')).toBeDefined();
    expect(screen.getByTestId('test-content')).toBeDefined();
  });
});
