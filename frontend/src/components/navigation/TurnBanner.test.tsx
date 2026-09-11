import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TurnBanner } from './TurnBanner';
import type { OSRMStep } from '../../routing/maneuvers';

const departStep: OSRMStep = { maneuver: { type: 'depart' }, distance: 300 };
const turnLeftStep: OSRMStep = { maneuver: { type: 'turn', modifier: 'left' }, distance: 100 };
const arriveStep: OSRMStep = { maneuver: { type: 'arrive' }, distance: 0 };

describe('TurnBanner', () => {
  it('shows arrival state when arrived=true', () => {
    render(
      <TurnBanner step={arriveStep} remainingM={0} arrived={true} destinationName="Test WC" />,
    );
    expect(screen.getByTestId('turn-banner-arrived')).toBeInTheDocument();
    expect(screen.getByText('You have arrived')).toBeInTheDocument();
    expect(screen.getByText('Test WC')).toBeInTheDocument();
  });

  it('renders null when step is null and not arrived', () => {
    const { container } = render(
      <TurnBanner step={null} remainingM={100} arrived={false} destinationName="Test WC" />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('shows turn instruction for a depart step', () => {
    render(
      <TurnBanner step={departStep} remainingM={300} arrived={false} destinationName="Test WC" />,
    );
    expect(screen.getByTestId('turn-instruction').textContent).toBe('Head');
  });

  it('shows turn instruction for a turn-left step', () => {
    render(
      <TurnBanner step={turnLeftStep} remainingM={100} arrived={false} destinationName="Test WC" />,
    );
    expect(screen.getByTestId('turn-instruction').textContent).toBe('Turn left');
  });

  it('applies -90 deg rotation for turn-left', () => {
    render(
      <TurnBanner step={turnLeftStep} remainingM={100} arrived={false} destinationName="Test WC" />,
    );
    const arrow = screen.getByTestId('turn-arrow');
    expect(arrow.getAttribute('data-rotation')).toBe('-90');
  });

  it('shows distance in metres when under 1km', () => {
    render(
      <TurnBanner step={departStep} remainingM={450} arrived={false} destinationName="Test WC" />,
    );
    expect(screen.getByText('450 m')).toBeInTheDocument();
  });

  it('shows distance in km when over 1km', () => {
    render(
      <TurnBanner step={departStep} remainingM={1500} arrived={false} destinationName="Test WC" />,
    );
    expect(screen.getByText('1.5 km')).toBeInTheDocument();
  });

  it('does not show arrival state when arrived=false', () => {
    render(
      <TurnBanner step={departStep} remainingM={300} arrived={false} destinationName="Test WC" />,
    );
    expect(screen.queryByTestId('turn-banner-arrived')).not.toBeInTheDocument();
    expect(screen.getByTestId('turn-banner')).toBeInTheDocument();
  });
});
