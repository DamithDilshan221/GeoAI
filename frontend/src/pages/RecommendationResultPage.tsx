import { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';

export function RecommendationResultPage() {
  const { state } = useSearchContext();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock data delay - to be replaced with endpoint in Phase 11
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (!state.selectedCategory) {
    return <Navigate to="/" replace />;
  }

  if (isLoading) {
    return <LoadingState message="Generating optimal recommendation..." />;
  }

  return (
    <div className="flex flex-col h-full overflow-hidden relative">
      <div className="px-5 pt-4 pb-2 shrink-0 flex items-center justify-between">
        <h2 className="text-[22px] font-bold text-white m-0">Recommended Route</h2>
        <Link to="/nearby" className="text-[14px] text-teal hover:text-teal/80 font-bold no-underline active:scale-95 transition-transform">
          Cancel
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-3 pb-8 -webkit-overflow-scrolling-touch">
        <p className="text-[13.5px] text-muted-soft mt-0 mb-6 max-w-[280px]">
          Based on your location, filters, and current washroom statuses.
        </p>
        
        <div className="relative rounded-[20px] bg-paper text-ink p-5 shadow-[0_8px_32px_rgba(63,203,190,0.2)] border border-teal/40 overflow-hidden mb-6">
          <div className="absolute top-0 right-0 w-32 h-32 bg-teal/10 blur-2xl rounded-full translate-x-10 -translate-y-10"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-indigo/10 blur-xl rounded-full -translate-x-5 translate-y-5"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded-full bg-teal/20 flex items-center justify-center text-teal">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-teal">Top Match</span>
            </div>
            
            <h3 className="text-xl font-bold text-white m-0 mb-2 leading-tight">Main Station Restroom</h3>
            <p className="text-[13.5px] text-muted m-0 mb-5 leading-relaxed">
              Currently OPEN. This is the fastest accessible route from your current location.
            </p>
            
            <div className="flex gap-4 mb-6">
              <div className="flex flex-col">
                <span className="text-[11px] text-muted-soft uppercase font-bold tracking-wide mb-0.5">Est. Time</span>
                <span className="text-lg font-bold text-white">3 min</span>
              </div>
              <div className="w-px bg-pill-border"></div>
              <div className="flex flex-col">
                <span className="text-[11px] text-muted-soft uppercase font-bold tracking-wide mb-0.5">Distance</span>
                <span className="text-lg font-bold text-white">120m</span>
              </div>
            </div>
            
            <button className="w-full bg-teal text-[#06302D] border-none rounded-xl py-3.5 font-bold text-[14.5px] cursor-pointer shadow-soft font-display active:scale-[0.98] transition-transform flex items-center justify-center gap-2">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
              Start Navigation
            </button>
          </div>
        </div>

        <div className="rounded-[16px] border border-pill-border bg-pill-bg/30 p-5 text-center flex flex-col items-center justify-center min-h-[200px]">
          <div className="w-12 h-12 rounded-full bg-pill-bg border border-pill-border flex items-center justify-center text-muted mb-3">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
          </div>
          <span className="text-[13.5px] text-muted-soft font-medium">Map / Navigation UI will render here in Phase 12</span>
        </div>
      </div>
    </div>
  );
}
