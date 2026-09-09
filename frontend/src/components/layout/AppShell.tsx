import React from 'react';
import { BottomNav } from './BottomNav';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-[100dvh] flex-col relative overflow-hidden bg-[radial-gradient(140%_60%_at_15%_-10%,var(--navy-700)_0%,transparent_60%),linear-gradient(180deg,var(--navy-900)_0%,var(--navy-950)_55%,var(--navy-950)_100%)] text-ink max-w-[430px] mx-auto shadow-[0_0_60px_rgba(0,0,0,0.45)]">
      <header className="flex-shrink-0 px-5 pt-[22px] pb-1 text-white">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="relative flex shrink-0 items-center justify-center w-[34px] h-[34px] rounded-[11px] bg-[linear-gradient(145deg,#16314C_0%,#0A1826_100%)] shadow-[0_0_0_1px_rgba(63,203,190,0.35),0_0_14px_rgba(63,203,190,0.45)]">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="#fff">
                <circle cx="8.3" cy="4.8" r="2.3" />
                <path d="M8.3 8.2c-2.2 0-3.8 1.6-3.8 3.8v6h2.2v5h3.2v-5h2.2v-6c0-2.2-1.6-3.8-3.8-3.8z" />
                <circle cx="16.4" cy="4.3" r="2.1" />
                <path d="M16.4 7.6c-.8 0-1.5.5-1.7 1.3l-1.5 4.4h1.6l.3 5h2.6l.3-5h1.6l-1.5-4.4c-.2-.8-.9-1.3-1.7-1.3z" />
              </svg>
              <div className="absolute -bottom-[3px] left-1/2 -translate-x-1/2 w-[9px] h-[9px] rounded-full bg-teal border-2 border-navy-950"></div>
            </div>
            <h1 className="text-[21px] font-bold tracking-[0.1px] m-0">Campus Washroom Finder</h1>
          </div>
          <button className="flex shrink-0 items-center justify-center w-10 h-10 rounded-xl border border-pill-border bg-pill-bg text-inherit transition-all active:scale-[0.94]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="4" y1="7" x2="20" y2="7" />
              <line x1="4" y1="12" x2="20" y2="12" />
              <line x1="4" y1="17" x2="20" y2="17" />
            </svg>
          </button>
        </div>
      </header>

      <main className="flex-1 relative overflow-hidden">
        <div className="absolute inset-0 overflow-y-auto overflow-x-hidden">
          {children}
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
