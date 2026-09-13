import { useState } from 'react';
import { useMapTheme } from '../hooks/useMapTheme';

export function SettingsView() {
  const [isDarkMode, setIsDarkMode] = useState(() => !document.body.classList.contains('day'));
  const [preferStaffWashrooms, setPreferStaffWashrooms] = useState(() => localStorage.getItem('preferStaffWashrooms') === 'true');
  const { themeId, setTheme, availableThemes } = useMapTheme();

  const toggleTheme = () => {
    const nextMode = !isDarkMode;
    setIsDarkMode(nextMode);
    if (nextMode) {
      document.body.classList.remove('day');
      localStorage.setItem('theme_mode', 'dark');
    } else {
      document.body.classList.add('day');
      localStorage.setItem('theme_mode', 'light');
    }
  };

  const toggleStaffPreference = () => {
    const nextPref = !preferStaffWashrooms;
    setPreferStaffWashrooms(nextPref);
    localStorage.setItem('preferStaffWashrooms', String(nextPref));
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-5 pt-4 pb-2 shrink-0">
        <h2 className="text-[22px] font-extrabold text-ink m-0 tracking-tight">Settings</h2>
        <p className="text-[12px] text-muted-soft m-0 font-medium">Preferences & interface appearance</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 pb-8 -webkit-overflow-scrolling-touch space-y-6">
        
        {/* Appearance Section */}
        <div>
          <h3 className="text-[12px] font-extrabold text-indigo-600 dark:text-purple-300 uppercase tracking-widest mb-2.5 m-0 px-1">Appearance</h3>
          <div className="glass-panel rounded-3xl overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <div>
                <span className="text-ink text-[15px] font-extrabold block">Dark Mode</span>
                <span className="text-muted text-[12px]">Switch between Pearl Dark & Ethereal Day</span>
              </div>
              
              <button 
                className={`relative w-[54px] h-[30px] rounded-full transition-all cursor-pointer border border-white/25 shadow-inner ${isDarkMode ? 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_14px_rgba(139,92,246,0.6)]' : 'bg-slate-300/60'}`}
                onClick={toggleTheme}
              >
                <div className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-md ${isDarkMode ? 'translate-x-[27px]' : 'translate-x-[4px]'}`}></div>
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4">
              <div>
                <span className="text-ink text-[15px] font-extrabold block">High Contrast Text</span>
                <span className="text-muted text-[12px]">Maximize map label readability</span>
              </div>
              <button className="relative w-[54px] h-[30px] rounded-full transition-colors cursor-pointer border border-white/15 shadow-inner bg-slate-300/40">
                <div className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-sm translate-x-[4px]"></div>
              </button>
            </div>
          </div>
        </div>

        {/* Map Styles Section */}
        <div>
          <h3 className="text-[12px] font-extrabold text-indigo-600 dark:text-purple-300 uppercase tracking-widest mb-2.5 m-0 px-1">Map Theme & Layers</h3>
          <div className="glass-panel rounded-3xl p-4 space-y-3.5">
            <div className="flex items-center justify-between mb-1 px-1">
              <span className="text-ink text-[14.5px] font-extrabold">Default Basemap</span>
              <span className="text-[12px] text-sky-600 dark:text-sky-400 font-bold glass-pill px-2.5 py-0.5 rounded-full">
                {availableThemes.find(t => t.id === themeId)?.name || 'Custom'}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              {availableThemes.map((t) => {
                const isSelected = t.id === themeId;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setTheme(t.id)}
                    className={`flex items-center gap-2.5 p-2.5 rounded-2xl border text-left cursor-pointer transition-all duration-200 ${
                      isSelected
                        ? 'bg-gradient-to-r from-indigo-500/30 to-purple-500/30 border-purple-400 text-ink font-extrabold shadow-[0_0_16px_rgba(168,85,247,0.35)] scale-[1.02]'
                        : 'glass-pill text-muted hover:text-ink border-white/10'
                    }`}
                  >
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-white/40 shrink-0 shadow-sm"
                      style={{ background: t.previewColor }}
                    />
                    <span className="text-[12px] truncate font-semibold">{t.name.split(' (')[0]}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
        
        {/* Preferences Section */}
        <div>
          <h3 className="text-[12px] font-extrabold text-indigo-600 dark:text-purple-300 uppercase tracking-widest mb-2.5 m-0 px-1">Preferences</h3>
          <div className="glass-panel rounded-3xl overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <span className="text-ink text-[15px] font-extrabold">Default Search Radius</span>
              <span className="text-indigo-600 dark:text-purple-300 text-[13px] font-bold glass-pill px-2.5 py-0.5 rounded-full">500m</span>
            </div>
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <div className="flex flex-col pr-3">
                <span className="text-ink text-[15px] font-extrabold">Prefer Staff Washrooms</span>
                <span className="text-muted text-[12px] mt-0.5">Show staff facilities first when available</span>
              </div>
              <button 
                className={`relative w-[54px] h-[30px] shrink-0 rounded-full transition-all cursor-pointer border border-white/25 shadow-inner ${preferStaffWashrooms ? 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_14px_rgba(139,92,246,0.6)]' : 'bg-slate-300/60'}`}
                onClick={toggleStaffPreference}
              >
                <div className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-md ${preferStaffWashrooms ? 'translate-x-[27px]' : 'translate-x-[4px]'}`}></div>
              </button>
            </div>
            <div className="flex items-center justify-between p-4">
              <span className="text-ink text-[15px] font-extrabold">Live Navigation Updates</span>
              <span className="text-emerald-600 dark:text-emerald-400 text-[12px] font-bold glass-pill px-2.5 py-0.5 rounded-full">Enabled</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

