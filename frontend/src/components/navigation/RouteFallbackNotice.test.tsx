import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { RouteFallbackNotice } from './RouteFallbackNotice';

const NOTICE_TEXT = "Couldn't calculate a walking route — showing straight-line direction.";

describe('RouteFallbackNotice', () => {
  it('renders nothing when visible is false', () => {
    const { container } = render(<RouteFallbackNotice visible={false} />);
    expect(container.firstChild).toBeNull();
    expect(screen.queryByText(NOTICE_TEXT)).toBeNull();
  });

  it('renders the fallback notice text when visible is true', () => {
    render(<RouteFallbackNotice visible={true} />);
    expect(screen.getByText(NOTICE_TEXT)).toBeInTheDocument();
  });

  it('has role="status" for accessibility when visible', () => {
    render(<RouteFallbackNotice visible={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
