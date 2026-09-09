import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useFacility } from '../hooks/useFacility';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { MapView } from '../components/map/MapView';

export function FacilityDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const facilityId = parseInt(id || '', 10);
  const navigate = useNavigate();
  
  const { data: facility, isLoading, error, refetch } = useFacility(facilityId);
  const [saved, setSaved] = useState(false);

  if (isLoading) return <LoadingState message="Loading washroom details..." />;

  if (error) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const is404 = (error as any).response?.status === 404;
    
    if (is404) {
      return (
        <div className="text-center p-8 text-white h-full flex flex-col justify-center">
          <h2 className="text-2xl font-bold mb-4 text-ink">Washroom Not Found</h2>
          <p className="text-muted-soft mb-6">The washroom you're looking for doesn't exist or has been removed.</p>
          <Link to="/" className="text-teal font-bold underline">Return to Search</Link>
        </div>
      );
    }
    return <ErrorState message="Failed to load washroom details." onRetry={refetch} />;
  }

  if (!facility) return null;

  const getCategoryTheme = (cat: string) => {
    const c = cat.toLowerCase();
    if (c.includes('men') && !c.includes('women')) return { color: 'var(--men)', label: "Men's" };
    if (c.includes('women') || c.includes('female')) return { color: 'var(--women)', label: "Women's" };
    if (c.includes('unisex') || c.includes('neutral')) return { color: 'var(--amber-dark)', label: 'Gender-Neutral' };
    if (c.includes('access') || c.includes('wheelchair')) return { color: 'var(--indigo)', label: 'Accessible' };
    return { color: 'var(--teal)', label: cat };
  };

  const theme = getCategoryTheme(facility.category);

  // We can render a map in the background with just this facility
  const mapMarkers = [{
    id: facility.id,
    lat: facility.latitude,
    lon: facility.longitude,
    title: facility.name,
    category: facility.category
  }];

  return (
    <div className="relative w-full h-full flex flex-col overflow-hidden">
      {/* Background Map */}
      <div className="absolute inset-0">
        <MapView 
          className="w-full h-full"
          markers={mapMarkers} 
          userLocation={null} // We might not have it here easily without context, but that's okay
        />
        <button 
          onClick={() => navigate(-1)}
          className="absolute top-5 left-4 w-11 h-11 bg-paper/90 backdrop-blur-md rounded-full flex items-center justify-center border-none shadow-soft text-ink cursor-pointer z-10"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
      </div>

      {/* Bottom Sheet */}
      <div className="absolute bottom-0 left-0 right-0 bg-paper rounded-t-3xl shadow-[0_-4px_24px_rgba(0,0,0,0.08)] flex flex-col z-20 max-h-[85vh]">
        <div className="w-full flex justify-center py-3 pb-1 cursor-grab active:cursor-grabbing">
          <div className="w-10 h-1.5 bg-pill-border rounded-full"></div>
        </div>
        
        <div className="px-5 pt-3 pb-4 border-b border-hairline shrink-0">
          <div className="flex justify-between items-start mb-2 gap-3">
            <h2 className="m-0 text-[22px] font-bold text-ink leading-tight">{facility.name}</h2>
            {/* If backend returned distance, we could show it here. FacilityDetails doesn't have it natively unless passed. */}
          </div>
          
          <div className="flex items-center gap-3.5 mb-4.5 text-[13.5px] text-muted-soft">
            <span className="flex items-center gap-1.5 text-ink font-medium">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: theme.color }}></span>
              {theme.label}
            </span>
            {facility.rating !== null && (
              <span className="flex items-center gap-[3px] text-amber-dark font-bold">
                ★ {facility.rating.toFixed(1)}
              </span>
            )}
            <span className="text-muted-soft text-[12px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-pill-bg border border-pill-border">
              {facility.data_source || 'Verified'}
            </span>
          </div>
          
          <div className="flex gap-2.5">
            <button 
              onClick={() => navigate('/recommend')}
              className="flex-[2] bg-teal text-[#06302D] border-none rounded-2xl py-3.5 font-bold text-[14.5px] cursor-pointer shadow-soft font-display active:scale-[0.98] transition-transform"
            >
              Navigate
            </button>
            <button className="flex-1 bg-pill-bg text-ink border border-pill-border rounded-2xl flex items-center justify-center cursor-pointer active:scale-[0.98] transition-transform">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13"/></svg>
            </button>
            <button 
              onClick={() => setSaved(!saved)}
              className="flex-1 bg-pill-bg text-ink border border-pill-border rounded-2xl flex items-center justify-center cursor-pointer active:scale-[0.98] transition-transform"
            >
              {saved ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--amber-dark)" stroke="none"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
              )}
            </button>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto px-5 py-5 -webkit-overflow-scrolling-touch">
          <div className="mb-6">
            <h3 className="m-0 mb-3 text-[15px] font-bold text-ink">Features & Accessibility</h3>
            <ul className="list-none p-0 m-0 space-y-3">
              {facility.accessibility?.wheelchair_friendly && (
                <li className="flex items-center gap-3 text-[14px] text-ink">
                  <div className="w-8 h-8 rounded-full bg-[#E8F0FE] flex items-center justify-center text-indigo">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="4.2" r="1.7"/><path d="M11 8.5v4.5l-3.5 5.5"/><path d="M11 10h5l-1.2 3"/><circle cx="15" cy="17.5" r="3.3"/></svg>
                  </div>
                  Wheelchair Accessible
                </li>
              )}
              <li className="flex items-center gap-3 text-[14px] text-ink">
                <div className="w-8 h-8 rounded-full bg-pill-bg flex items-center justify-center text-muted-soft">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </div>
                Free to use
              </li>
            </ul>
          </div>
          
          <div className="mb-6">
            <h3 className="m-0 mb-3 text-[15px] font-bold text-ink">Current Status</h3>
            <div className={`p-4 rounded-xl border flex items-center gap-3 ${
              facility.status === 'OPEN'
                ? 'bg-[#E6F4EA] border-[#CEEAD6] text-[#137333]'
                : facility.status === 'CLOSED'
                  ? 'bg-[#FCE8E6] border-[#FAD2CF] text-[#C5221F]'
                  : 'bg-[#FEF7E0] border-[#FCE8B2] text-[#B06000]'
            }`}>
              <div className="w-2.5 h-2.5 rounded-full bg-current"></div>
              <span className="font-bold text-[14.5px]">Currently {facility.status.replace('_', ' ')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
