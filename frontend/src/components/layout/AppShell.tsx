import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BottomNav } from './BottomNav';

export function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const isSettings = location.pathname === '/settings';
  const isSaved = location.pathname === '/saved';

  const title = isSettings ? 'Settings' : isSaved ? 'Saved Washrooms' : 'Campus Washroom Finder';
  const subtitle = isSettings ? 'Customise your experience' : isSaved ? 'Your bookmarked facilities' : 'Peradeniya University';

  return (
    <div className="flex h-[100dvh] flex-col relative overflow-hidden app-shell-bg text-ink max-w-[440px] mx-auto shadow-[0_0_80px_rgba(0,0,0,0.6)] border-x border-hairline">
      {/* Subtle background ambient light flares */}
      <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-80 bg-indigo-500/15 rounded-full blur-3xl opacity-70" />
      <div className="pointer-events-none absolute top-1/3 -right-20 w-64 h-64 bg-fuchsia-500/10 rounded-full blur-3xl opacity-60" />
      <div className="pointer-events-none absolute bottom-20 -left-20 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl opacity-60" />

      <header className="flex-shrink-0 px-5 pt-6 pb-3 text-ink relative z-10">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 min-w-0">
            {isSettings && (
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="w-9 h-9 rounded-xl glass-pill flex items-center justify-center text-ink hover:text-purple-400 active:scale-95 transition-all cursor-pointer shrink-0 border border-white/15"
                title="Back"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </button>
            )}

            <div className="relative flex shrink-0 items-center justify-center w-[48px] h-[48px] rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 shadow-[0_0_22px_rgba(99,102,241,0.55)] border border-indigo-400/50 text-white">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C7.58 2 4 5.58 4 10c0 5.25 8 12 8 12s8-6.75 8-12c0-4.42-3.58-8-8-8z" fill="#818CF8" fillOpacity="0.4" stroke="white" strokeWidth="1.8" />
                <circle cx="9.2" cy="7.2" r="1.3" fill="white" />
                <path d="M9.2 9.2c-1.1 0-1.9.8-1.9 1.9v3h1.1v2.5h1.6v-2.5h1.1v-3c0-1.1-.8-1.9-1.9-1.9z" fill="white" />
                <circle cx="14.5" cy="7" r="1.2" fill="white" />
                <path d="M14.5 8.9c-.5 0-.9.3-1 .8l-.9 2.6h1l.2 3h1.5l.2-3h1l-.9-2.6c-.1-.5-.5-.8-1.1-.8z" fill="white" />
              </svg>
            </div>
            <div className="min-w-0">
              <h1 className="text-[21.5px] font-black tracking-tight m-0 text-ink leading-tight truncate">
                {title}
              </h1>
              <p className="text-[13px] font-bold text-muted-soft m-0 tracking-wide mt-0.5 truncate">{subtitle}</p>
            </div>
          </div>
          <div className="live-badge px-3.5 py-1.5 rounded-full flex items-center gap-1.5 text-[13px] font-extrabold shadow-sm shrink-0">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"></span>
            <span>Live</span>
          </div>
        </div>
      </header>

      <main className="flex-1 relative overflow-hidden z-10">
        <div className="absolute inset-0 overflow-y-auto overflow-x-hidden">
          {children}
        </div>
      </main>

      <BottomNav />
    </div>
  );
}


