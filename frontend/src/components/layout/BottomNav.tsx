import React from 'react';
import { NavLink } from 'react-router-dom';

export function BottomNav() {
  return (
    <nav className="flex shrink-0 z-50 bg-navy-950 border-t border-hairline px-2 pb-[env(safe-area-inset-bottom,8px)] pt-2">
      <NavLink
        to="/nearby?view=map"
        className={({ isActive }) =>
          `flex-1 flex flex-col items-center gap-1 py-1.5 rounded-xl bg-transparent border-none cursor-pointer transition-colors ${
            isActive ? 'text-teal' : 'text-muted-soft'
          }`
        }
      >
        {({ isActive }) => (
          <>
            <span
              className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all duration-150 ${
                isActive
                  ? 'bg-teal border-teal shadow-[0_6px_16px_rgba(63,203,190,0.35)] text-[#06302D] scale-100'
                  : 'bg-pill-bg border-pill-border hover:scale-95'
              }`}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="1,6 1,22 8,18 16,22 23,18 23,2 16,6 8,2" />
                <line x1="8" y1="2" x2="8" y2="18" />
                <line x1="16" y1="6" x2="16" y2="22" />
              </svg>
            </span>
            <span className="text-[11.5px] font-bold font-display">Map</span>
          </>
        )}
      </NavLink>
      <NavLink
        to="/nearby?view=list"
        className={({ isActive }) =>
          `flex-1 flex flex-col items-center gap-1 py-1.5 rounded-xl bg-transparent border-none cursor-pointer transition-colors ${
            isActive ? 'text-teal' : 'text-muted-soft'
          }`
        }
      >
        {({ isActive }) => (
          <>
            <span
              className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all duration-150 ${
                isActive
                  ? 'bg-teal border-teal shadow-[0_6px_16px_rgba(63,203,190,0.35)] text-[#06302D] scale-100'
                  : 'bg-pill-bg border-pill-border hover:scale-95'
              }`}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
              >
                <circle cx="11" cy="11" r="7" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </span>
            <span className="text-[11.5px] font-bold font-display">Search</span>
          </>
        )}
      </NavLink>
      <NavLink
        to="/saved"
        className={({ isActive }) =>
          `flex-1 flex flex-col items-center gap-1 py-1.5 rounded-xl bg-transparent border-none cursor-pointer transition-colors ${
            isActive ? 'text-teal' : 'text-muted-soft'
          }`
        }
      >
        {({ isActive }) => (
          <>
            <span
              className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all duration-150 ${
                isActive
                  ? 'bg-teal border-teal shadow-[0_6px_16px_rgba(63,203,190,0.35)] text-[#06302D] scale-100'
                  : 'bg-pill-bg border-pill-border hover:scale-95'
              }`}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M6 3h12v18l-6-4-6 4V3z" />
              </svg>
            </span>
            <span className="text-[11.5px] font-bold font-display">Saved</span>
          </>
        )}
      </NavLink>
      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `flex-1 flex flex-col items-center gap-1 py-1.5 rounded-xl bg-transparent border-none cursor-pointer transition-colors ${
            isActive ? 'text-teal' : 'text-muted-soft'
          }`
        }
      >
        {({ isActive }) => (
          <>
            <span
              className={`w-11 h-11 rounded-2xl flex items-center justify-center border transition-all duration-150 ${
                isActive
                  ? 'bg-teal border-teal shadow-[0_6px_16px_rgba(63,203,190,0.35)] text-[#06302D] scale-100'
                  : 'bg-pill-bg border-pill-border hover:scale-95'
              }`}
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.55V21a2 2 0 0 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1H3a2 2 0 0 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.55V3a2 2 0 0 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.55 1H21a2 2 0 0 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1z" />
              </svg>
            </span>
            <span className="text-[11.5px] font-bold font-display">Settings</span>
          </>
        )}
      </NavLink>
    </nav>
  );
}
