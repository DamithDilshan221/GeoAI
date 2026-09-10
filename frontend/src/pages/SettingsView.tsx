import { useState } from 'react';

export function SettingsView() {
  const [isDarkMode, setIsDarkMode] = useState(() => !document.body.classList.contains('day'));
  const [preferStaffWashrooms, setPreferStaffWashrooms] = useState(() => localStorage.getItem('preferStaffWashrooms') === 'true');

  const toggleTheme = () => {
    const nextMode = !isDarkMode;
    setIsDarkMode(nextMode);
    if (nextMode) {
      document.body.classList.remove('day');
    } else {
      document.body.classList.add('day');
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
        <h2 className="text-[22px] font-bold text-white m-0">Settings</h2>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5 pb-8 -webkit-overflow-scrolling-touch space-y-6">
        
        {/* Appearance Section */}
        <div>
          <h3 className="text-[13.5px] font-bold text-teal uppercase tracking-wider mb-3 m-0">Appearance</h3>
          <div className="bg-paper rounded-2xl overflow-hidden border border-pill-border">
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <span className="text-ink text-[15px] font-medium">Dark Mode</span>
              
              <button 
                className={`relative w-[52px] h-[28px] rounded-full transition-colors cursor-pointer border-none shadow-inner ${isDarkMode ? 'bg-teal' : 'bg-pill-border'}`}
                onClick={toggleTheme}
              >
                <div className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-sm ${isDarkMode ? 'translate-x-[26px]' : 'translate-x-[4px]'}`}></div>
              </button>
            </div>
            
            <div className="flex items-center justify-between p-4">
              <span className="text-ink text-[15px] font-medium">High Contrast Text</span>
              <button className="relative w-[52px] h-[28px] rounded-full transition-colors cursor-pointer border-none shadow-inner bg-pill-border">
                <div className="absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-sm translate-x-[4px]"></div>
              </button>
            </div>
          </div>
        </div>
        
        {/* Preferences Section */}
        <div>
          <h3 className="text-[13.5px] font-bold text-teal uppercase tracking-wider mb-3 m-0">Preferences</h3>
          <div className="bg-paper rounded-2xl overflow-hidden border border-pill-border">
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <span className="text-ink text-[15px] font-medium">Default Search Radius</span>
              <span className="text-muted-soft text-[14px]">500m</span>
            </div>
            <div className="flex items-center justify-between p-4 border-b border-hairline">
              <div className="flex flex-col">
                <span className="text-ink text-[15px] font-medium">Prefer Staff Washrooms</span>
                <span className="text-muted-soft text-[13px] mt-0.5">Show staff facilities first when searching nearby</span>
              </div>
              <button 
                className={`relative w-[52px] h-[28px] shrink-0 rounded-full transition-colors cursor-pointer border-none shadow-inner ${preferStaffWashrooms ? 'bg-teal' : 'bg-pill-border'}`}
                onClick={toggleStaffPreference}
              >
                <div className={`absolute top-1/2 -translate-y-1/2 w-5 h-5 bg-white rounded-full transition-transform shadow-sm ${preferStaffWashrooms ? 'translate-x-[26px]' : 'translate-x-[4px]'}`}></div>
              </button>
            </div>
            <div className="flex items-center justify-between p-4">
              <span className="text-ink text-[15px] font-medium">Push Notifications</span>
              <span className="text-muted-soft text-[14px]">Disabled</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
