import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NavigationOverlay } from './NavigationOverlay';

// Mock the child map component (Leaflet) and OSRM client
vi.mock('../map/NavigationMap', () => ({
  NavigationMap: ({ destination }: { destination: { name: string } }) => (
    <div data-testid="navigation-map">{destination.name}</div>
  ),
}));

vi.mock('../../routing/osrmClient', () => ({
  fetchWalkingRoute: vi.fn(),
}));

vi.mock('../../hooks/useLiveNavigation', () => ({
  useLiveNavigation: vi.fn(() => ({ stepIdx: 0, currentPosition: null })),
}));

const { fetchWalkingRoute } = await import('../../routing/osrmClient');

const ORIGIN = { lat: 7.2545, lon: 80.5965 };
const DEST = { lat: 7.260, lon: 80.600, name: 'Test WC', category: 'male' };

const MOCK_ROUTE = {
  steps: [
    { maneuver: { type: 'depart' }, distance: 400 },
    { maneuver: { type: 'arrive' }, distance: 0 },
  ],
  path: [[7.2545, 80.5965], [7.260, 80.600]] as [number, number][],
  distanceM: 520,
  source: 'network' as const,
};

describe('NavigationOverlay', () => {
  beforeEach(() => {
    vi.mocked(fetchWalkingRoute).mockResolvedValue(MOCK_ROUTE);

    // Mock geolocation watchPosition (useLiveNavigation is mocked but the hook
    // itself will still call watchPosition unless fully mocked)
    Object.defineProperty(global.navigator, 'geolocation', {
      value: { watchPosition: vi.fn(() => 1), clearWatch: vi.fn() },
      writable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the overlay with destination name in top bar', async () => {
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    expect(screen.getByText('Test WC')).toBeInTheDocument();
  });

  it('renders Stop button', () => {
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    expect(screen.getByTestId('nav-stop-btn')).toBeInTheDocument();
  });

  it('renders End button', () => {
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    expect(screen.getByTestId('nav-end-btn')).toBeInTheDocument();
  });

  it('calls onClose when Stop button is clicked', async () => {
    const onClose = vi.fn();
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={onClose} />);
    await userEvent.click(screen.getByTestId('nav-stop-btn'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when End button is clicked', async () => {
    const onClose = vi.fn();
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={onClose} />);
    await userEvent.click(screen.getByTestId('nav-end-btn'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('shows NavigationMap after route loads', async () => {
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    await waitFor(() => {
      expect(screen.getByTestId('navigation-map')).toBeInTheDocument();
    });
  });

  it('calls fetchWalkingRoute with origin and destination', async () => {
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    await waitFor(() => {
      expect(fetchWalkingRoute).toHaveBeenCalledWith(ORIGIN, DEST);
    });
  });

  it('shows fallback notice when route source is straight_line_estimate', async () => {
    vi.mocked(fetchWalkingRoute).mockResolvedValue({
      ...MOCK_ROUTE,
      source: 'straight_line_estimate' as const,
    });
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    await waitFor(() => {
      expect(
        screen.getByText(/couldn't calculate a walking route/i),
      ).toBeInTheDocument();
    });
  });

  it('does NOT show fallback notice when route source is network', async () => {
    vi.mocked(fetchWalkingRoute).mockResolvedValue({
      ...MOCK_ROUTE,
      source: 'network' as const,
    });
    render(<NavigationOverlay origin={ORIGIN} destination={DEST} onClose={vi.fn()} />);
    // Wait for the route to load, then assert the notice is absent
    await waitFor(() => {
      expect(screen.getByTestId('navigation-map')).toBeInTheDocument();
    });
    expect(
      screen.queryByText(/couldn't calculate a walking route/i),
    ).toBeNull();
  });
});
