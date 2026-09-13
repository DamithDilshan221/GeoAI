import { useTheme } from '../../hooks/useTheme';

export function ThemeToggleButton({ className = '' }: { className?: string }) {
  const { isDay, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`w-9 h-9 rounded-xl glass-pill flex items-center justify-center text-ink hover:text-sky-400 active:scale-90 transition-all duration-200 cursor-pointer border border-white/15 shadow-[0_2px_8px_rgba(0,0,0,0.15)] ${className}`}
      title={isDay ? 'Switch to Dark mode' : 'Switch to Light mode'}
      aria-label={isDay ? 'Switch to Dark mode' : 'Switch to Light mode'}
      data-testid="theme-toggle-btn"
    >
      {isDay ? (
        /* Moon Icon (Dark Mode Switch) */
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-indigo-600 dark:text-indigo-400 transition-transform duration-300 rotate-0 hover:-rotate-12"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="currentColor" fillOpacity="0.15" />
        </svg>
      ) : (
        /* Sun Icon (Light Mode Switch) */
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-amber-400 transition-transform duration-300 rotate-0 hover:rotate-45"
        >
          <circle cx="12" cy="12" r="4.5" fill="currentColor" fillOpacity="0.25" />
          <line x1="12" y1="1.5" x2="12" y2="3.5" />
          <line x1="12" y1="20.5" x2="12" y2="22.5" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1.5" y1="12" x2="3.5" y2="12" />
          <line x1="20.5" y1="12" x2="22.5" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      )}
    </button>
  );
}
