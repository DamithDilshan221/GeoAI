import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { FacilityList } from '../components/facility/FacilityList';
import { MapView } from '../components/map/MapView';
import { useNearbyFacilities } from '../hooks/useNearbyFacilities';
import { useCategories } from '../hooks/useCategories';
import { 
  DEFAULT_RADIUS_M, 
  MAX_RADIUS_M, 
  RADIUS_EXPAND_MULTIPLIER, 
  SERVICE_UNAVAILABLE_MESSAGE 
} from '../constants/search';

export function NearbyFacilitiesPage() {
  const { state, dispatch } = useSearchContext();
  const [radiusM, setRadiusM] = useState(DEFAULT_RADIUS_M);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  const locationObj = useLocation();
  const queryParams = new URLSearchParams(locationObj.search);
  const currentView = queryParams.get('view') || 'list';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [mapInstance, setMapInstance] = useState<any>(null);

  useEffect(() => {
    if (currentView === 'map' && mapInstance) {
      // Force Leaflet to recalculate tiles after the display:none is removed
      setTimeout(() => mapInstance.invalidateSize(), 50);
    }
  }, [currentView, mapInstance]);

  const { selectedCategory, selectedAudience, location } = state;

  useEffect(() => {
    if (!selectedCategory || !location) {
      navigate('/', { replace: true });
    }
  }, [selectedCategory, location, navigate]);

  const { data: categories } = useCategories();
  
  const { data, isLoading, isError, error, refetch } = useNearbyFacilities(
    selectedCategory && location
      ? { lat: location.lat, lon: location.lon, category: selectedCategory, radius_m: radiusM, audience: selectedAudience }
      : null
  );

  if (!selectedCategory || !location) {
    return null;
  }

  if (isLoading) {
    return <LoadingState message="Finding washrooms near you..." />;
  }

  if (isError) {
    const is503 = (error as { response?: { status?: number } })?.response?.status === 503;
    const message = is503 
      ? SERVICE_UNAVAILABLE_MESSAGE 
      : 'An error occurred while fetching washrooms.';
    return <ErrorState message={message} onRetry={refetch} />;
  }

  const mapMarkers = (data || []).map(f => ({
    id: f.id,
    lat: f.latitude,
    lon: f.longitude,
    title: f.name,
    category: f.category
  }));

  const userLocation = { lat: location.lat, lon: location.lon };

  const handleCategoryClick = (code: string) => {
    dispatch({ type: 'SET_CATEGORY', payload: code });
  };

  const renderChips = () => (
    <div className="flex gap-2 overflow-x-auto mt-3.5 pb-0.5 no-scrollbar">
      <div
        onClick={() => navigate('/recommend')}
        className="shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-full text-[12px] font-bold cursor-pointer select-none transition-all active:scale-[0.96] glass-button-glow text-white shadow-[0_0_16px_rgba(139,92,246,0.45)]"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M10 2L11.8 7.8L17.5 9.5L11.8 11.2L10 17L8.2 11.2L2.5 9.5L8.2 7.8L10 2Z" />
          <path d="M19.5 13.5L20.3 16.2L23 17L20.3 17.8L19.5 20.5L18.7 17.8L16 17L18.7 16.2L19.5 13.5Z" />
          <path d="M18.5 2.5L19 4L20.5 4.5L19 5L18.5 6.5L18 5L16.5 4.5L18 4L18.5 2.5Z" />
        </svg>
        <span>AI Recommender</span>
      </div>
      {categories?.map((cat) => {
        const isSelected = selectedCategory === cat.code;
        return (
          <div 
            key={cat.id}
            onClick={() => handleCategoryClick(cat.code)}
            className={`shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-full text-[12px] font-bold cursor-pointer select-none transition-all active:scale-[0.96] ${
              isSelected 
                ? 'bg-gradient-to-r from-sky-400 to-indigo-500 text-white shadow-[0_0_16px_rgba(56,189,248,0.45)] border border-white/40' 
                : 'glass-pill text-muted hover:text-ink'
            }`}
          >
            <span>{cat.label}</span>
          </div>
        );
      })}
    </div>
  );

  return (
    <>
      <div className={`flex flex-col h-full ${currentView === 'list' ? '' : 'hidden'}`}>
        <div className="px-[18px] pt-3 shrink-0">
          <div className="flex items-center gap-3 px-4 py-3 rounded-2xl glass-pill shadow-glass-specular">
            <svg className="shrink-0 text-sky-400" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input 
              id="search-facilities"
              name="search-facilities"
              type="text" 
              placeholder="Search building or facility name..." 
              className="border-none bg-transparent outline-none text-ink font-sans text-[14px] w-full placeholder:text-muted font-medium"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {renderChips()}
        </div>
        
        <div className="flex-1 px-[18px] py-[16px] pb-8 overflow-y-auto -webkit-overflow-scrolling-touch">
          {data && data.length === 0 ? (
            <div className="flex flex-col items-center text-center py-16 px-7 text-muted glass-panel rounded-3xl mt-4">
              <div className="w-16 h-16 rounded-2xl glass-pill flex items-center justify-center text-sky-400 mb-4 shadow-inner">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="9" r="9" />
                  <polygon points="14.5,9.5 10,10 9.5,14.5 14,14" />
                </svg>
              </div>
              <h3 className="m-0 mb-1.5 text-ink text-base font-extrabold">No washrooms match this search.</h3>
              <p className="m-0 mb-5 text-[13px] text-muted max-w-[260px]">Try widening your search — clear filters to see every washroom on campus.</p>
              <button
                disabled={radiusM >= MAX_RADIUS_M}
                onClick={() => setRadiusM(prev => Math.min(prev * RADIUS_EXPAND_MULTIPLIER, MAX_RADIUS_M))}
                className="glass-button-glow text-white rounded-xl px-6 py-3 font-bold text-[13.5px] cursor-pointer disabled:opacity-50 active:scale-95 transition-transform"
              >
                Search wider area
              </button>
            </div>
          ) : (
            <>
              <div className="text-[12px] text-muted-soft mb-3 font-bold tracking-wide uppercase px-1">
                {data?.length || 0} {data?.length === 1 ? 'washroom' : 'washrooms'} available
              </div>
              <FacilityList facilities={(data || []).filter(f => f.name.toLowerCase().includes(searchTerm.toLowerCase()) || f.category.toLowerCase().includes(searchTerm.toLowerCase()))} />
            </>
          )}
        </div>
      </div>

      <div className={`relative w-full h-full z-0 ${currentView === 'map' ? '' : 'hidden'}`}>
        <MapView 
          className="w-full h-full"
          markers={mapMarkers} 
          userLocation={userLocation} 
          onMarkerClick={(id) => navigate(`/facilities/${id}`)}
          onMapReady={setMapInstance}
        />
        <button className="absolute right-4 bottom-5 flex items-center gap-2 glass-button-glow text-white rounded-full py-3 px-5 font-bold text-[13px] shadow-lg cursor-pointer z-50 active:scale-95 transition-transform">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
            <circle cx="12" cy="12" r="3" />
            <line x1="12" y1="2" x2="12" y2="5" />
            <line x1="12" y1="19" x2="12" y2="22" />
            <line x1="2" y1="12" x2="5" y2="12" />
            <line x1="19" y1="12" x2="22" y2="12" />
          </svg>
          <span>Near me (100m)</span>
        </button>
      </div>
    </>
  );
}
