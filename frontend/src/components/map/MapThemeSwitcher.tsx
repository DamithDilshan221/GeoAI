import { useState, useRef, useEffect } from 'react';
import { type MapThemeOption } from '../../constants/map';

interface MapThemeSwitcherProps {
  currentThemeId: string;
  availableThemes: MapThemeOption[];
  onSelectTheme: (themeId: string) => void;
  className?: string;
}

export function MapThemeSwitcher({
  currentThemeId,
  availableThemes,
  onSelectTheme,
  className = '',
}: MapThemeSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const activeTheme =
    availableThemes.find((t) => t.id === currentThemeId) || availableThemes[0];

  return (
    <div ref={menuRef} className={`absolute top-3 right-3 z-[1000] ${className}`}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Change map style"
        title="Change map style"
        className="flex items-center gap-2 glass-pill text-ink backdrop-blur-xl border border-white/25 px-3.5 py-2 rounded-2xl shadow-glass-specular cursor-pointer transition-all hover:scale-105 active:scale-95"
      >
        <span
          className="w-3.5 h-3.5 rounded-full border border-white/40 shrink-0 shadow-sm"
          style={{ background: activeTheme.previewColor }}
        />
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
        <span className="text-[12px] font-extrabold tracking-tight pr-0.5">Layers</span>
      </button>

      {/* Floating Theme Menu Popup */}
      {isOpen && (
        <div className="absolute top-12 right-0 w-72 glass-panel rounded-3xl shadow-[0_16px_40px_rgba(0,0,0,0.6)] p-3 flex flex-col gap-1.5 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-2 py-1.5 border-b border-hairline flex items-center justify-between">
            <span className="text-[11px] font-extrabold text-indigo-600 dark:text-purple-300 uppercase tracking-widest">
              Map Basemaps
            </span>
            <span className="text-[10px] text-sky-600 dark:text-sky-400 font-bold glass-pill px-2 py-0.5 rounded-full">
              {availableThemes.length} Styles
            </span>
          </div>

          <div className="max-h-72 overflow-y-auto space-y-1.5 pr-1">
            {availableThemes.map((theme) => {
              const isSelected = theme.id === currentThemeId;
              return (
                <button
                  key={theme.id}
                  type="button"
                  onClick={() => {
                    onSelectTheme(theme.id);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-start gap-2.5 p-2.5 rounded-2xl border text-left cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'bg-gradient-to-r from-indigo-500/30 to-purple-500/30 border-purple-400 text-ink shadow-[0_0_14px_rgba(168,85,247,0.35)]'
                      : 'glass-pill border-transparent text-muted hover:text-ink hover:border-white/10'
                  }`}
                >
                  <span
                    className="w-4 h-4 rounded-full border border-white/40 shrink-0 mt-0.5 shadow-sm"
                    style={{ background: theme.previewColor }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-[13px] font-extrabold text-ink m-0 truncate">
                        {theme.name}
                      </p>
                      {isSelected && (
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#c084fc"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      )}
                    </div>
                    <p className="text-[11px] text-muted-soft m-0 leading-tight line-clamp-1 mt-0.5">
                      {theme.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
