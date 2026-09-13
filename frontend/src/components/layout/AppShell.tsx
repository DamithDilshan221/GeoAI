import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BottomNav } from './BottomNav';
import { RestNavLogo } from '../common/RestNavLogo';

export function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();

  const isSettings = location.pathname === '/settings';
  const isSaved = location.pathname === '/saved';

  const getHeaderInfo = () => {
    if (isSettings) {
      return {
        title: 'Settings',
        subtitle: 'Customise your experience',
        showBack: true,
      };
    }
    if (isSaved) {
      return {
        title: 'Saved Facilities',
        subtitle: 'Quick access bookmarks',
        showBack: true,
      };
    }
    return {
      title: 'RestNav',
      subtitle: 'Peradeniya University',
      showBack: false,
    };
  };

  const headerInfo = getHeaderInfo();

  return (
    <div className="flex h-[100dvh] flex-col relative overflow-hidden app-shell-bg text-ink max-w-[440px] mx-auto shadow-[0_0_80px_rgba(0,0,0,0.6)] border-x border-hairline">
      {/* Subtle background ambient light flares */}
      <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-80 bg-indigo-500/15 rounded-full blur-3xl opacity-70" />
      <div className="pointer-events-none absolute top-1/3 -right-20 w-64 h-64 bg-fuchsia-500/10 rounded-full blur-3xl opacity-60" />
      <div className="pointer-events-none absolute bottom-20 -left-20 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl opacity-60" />

      <header className="flex-shrink-0 px-5 pt-6 pb-3 text-ink relative z-10">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            {headerInfo.showBack && (
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="w-9 h-9 rounded-xl glass-pill flex items-center justify-center text-ink hover:text-purple-400 active:scale-95 transition-all cursor-pointer mr-0.5 border border-white/10"
                title="Go Back"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </button>
            )}

            <RestNavLogo size="md" />
            <div>
              <h1 className="text-[21.5px] font-black tracking-tight m-0 text-ink leading-tight">
                {headerInfo.title}
              </h1>
              <p className="text-[13px] font-bold text-muted-soft m-0 tracking-wide mt-0.5">
                {headerInfo.subtitle}
              </p>
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


