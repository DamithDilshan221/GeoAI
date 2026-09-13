import { useLocation, useNavigate } from 'react-router-dom';

export function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(location.search);
  const view = searchParams.get('view');

  const isMapActive = location.pathname === '/' || (location.pathname === '/nearby' && (!view || view === 'map'));
  const isSearchActive = (location.pathname === '/nearby' && view === 'list') || location.pathname === '/recommend';
  const isSavedActive = location.pathname === '/saved';
  const isSettingsActive = location.pathname === '/settings';

  return (
    <nav className="flex shrink-0 z-50 glass-panel border-x-0 border-b-0 border-t border-white/10 px-4 pb-[calc(env(safe-area-inset-bottom,8px)+6px)] pt-3 backdrop-blur-2xl">
      {/* Map Tab */}
      <button
        type="button"
        onClick={() => navigate('/nearby?view=map')}
        className="flex-1 flex flex-col items-center justify-center gap-1 bg-transparent border-none cursor-pointer p-0 select-none group"
      >
        <div className={`transition-all duration-200 ${isMapActive ? 'bottom-nav-active-accent scale-105' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={isMapActive ? '2.3' : '1.9'}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polygon points="1,6 1,22 8,18 16,22 23,18 23,2 16,6 8,2" />
            <line x1="8" y1="2" x2="8" y2="18" />
            <line x1="16" y1="6" x2="16" y2="22" />
          </svg>
        </div>
        <span className={`text-[11.5px] font-semibold tracking-tight transition-colors ${isMapActive ? 'bottom-nav-active-accent font-bold' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          Map
        </span>
        <div className={`h-[2.5px] rounded-full transition-all duration-200 ${isMapActive ? 'w-6 bottom-nav-active-indicator' : 'w-0 bg-transparent'}`} />
      </button>

      {/* Search Tab */}
      <button
        type="button"
        onClick={() => navigate('/nearby?view=list')}
        className="flex-1 flex flex-col items-center justify-center gap-1 bg-transparent border-none cursor-pointer p-0 select-none group"
      >
        <div className={`transition-all duration-200 ${isSearchActive ? 'bottom-nav-active-accent scale-105' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={isSearchActive ? '2.3' : '1.9'}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
        <span className={`text-[11.5px] font-semibold tracking-tight transition-colors ${isSearchActive ? 'bottom-nav-active-accent font-bold' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          Search
        </span>
        <div className={`h-[2.5px] rounded-full transition-all duration-200 ${isSearchActive ? 'w-6 bottom-nav-active-indicator' : 'w-0 bg-transparent'}`} />
      </button>

      {/* Saved Tab */}
      <button
        type="button"
        onClick={() => navigate('/saved')}
        className="flex-1 flex flex-col items-center justify-center gap-1 bg-transparent border-none cursor-pointer p-0 select-none group"
      >
        <div className={`transition-all duration-200 ${isSavedActive ? 'bottom-nav-active-accent scale-105' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={isSavedActive ? '2.3' : '1.9'}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6 3h12v18l-6-4-6 4V3z" />
          </svg>
        </div>
        <span className={`text-[11.5px] font-semibold tracking-tight transition-colors ${isSavedActive ? 'bottom-nav-active-accent font-bold' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          Saved
        </span>
        <div className={`h-[2.5px] rounded-full transition-all duration-200 ${isSavedActive ? 'w-6 bottom-nav-active-indicator' : 'w-0 bg-transparent'}`} />
      </button>

      {/* Settings Tab */}
      <button
        type="button"
        onClick={() => navigate('/settings')}
        className="flex-1 flex flex-col items-center justify-center gap-1 bg-transparent border-none cursor-pointer p-0 select-none group"
      >
        <div className={`transition-all duration-200 ${isSettingsActive ? 'bottom-nav-active-accent scale-105' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={isSettingsActive ? '2.3' : '1.9'}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1 1.55V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1 2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 0 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 0 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1z" />
          </svg>
        </div>
        <span className={`text-[11.5px] font-semibold tracking-tight transition-colors ${isSettingsActive ? 'bottom-nav-active-accent font-bold' : 'text-slate-400/70 group-hover:text-slate-200'}`}>
          Settings
        </span>
        <div className={`h-[2.5px] rounded-full transition-all duration-200 ${isSettingsActive ? 'w-6 bottom-nav-active-indicator' : 'w-0 bg-transparent'}`} />
      </button>
    </nav>
  );
}

