/**
 * RouteFallbackNotice — shown inside NavigationOverlay when OSRM is unavailable
 * and the displayed route is a straight-line estimate rather than a real
 * walking route.
 *
 * §14.4 requires a distinct, clear user-facing notice in this case.
 * This component handles that requirement in isolation so NavigationOverlay
 * stays focused on orchestration.
 *
 * Props:
 *   visible — when false the component renders nothing (no DOM node at all)
 */

interface RouteFallbackNoticeProps {
  visible: boolean;
}

export function RouteFallbackNotice({ visible }: RouteFallbackNoticeProps) {
  if (!visible) return null;

  return (
    <div
      role="status"
      data-testid="route-fallback-notice"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 12px',
        margin: '0 12px 4px',
        borderRadius: '10px',
        backgroundColor: 'color-mix(in srgb, var(--amber) 15%, transparent)',
        border: '1px solid color-mix(in srgb, var(--amber-dark) 40%, transparent)',
        color: 'var(--amber-dark)',
        fontSize: '12px',
        fontWeight: 600,
        lineHeight: 1.4,
      }}
    >
      {/* Warning icon */}
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        style={{ flexShrink: 0 }}
      >
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      Couldn't calculate a walking route — showing straight-line direction.
    </div>
  );
}
