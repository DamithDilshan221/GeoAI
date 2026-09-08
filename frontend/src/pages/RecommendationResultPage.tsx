import React, { useEffect, useState } from 'react';
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
    <div className="space-y-6">
      <Link to="/nearby" className="text-sm text-blue-400 hover:text-blue-300 mb-4 inline-block">&larr; Back to list</Link>
      
      <div>
        <h2 className="text-2xl font-bold text-white">Recommended Route</h2>
        <p className="text-sm text-slate-400 mt-1">
          Based on your location and preferences
        </p>
      </div>

      <div className="rounded-xl border border-blue-700/50 bg-blue-900/10 p-6">
        <h3 className="text-xl font-semibold text-blue-300">Best Option: Main Station Restroom</h3>
        <p className="mt-2 text-slate-300">
          This facility is currently OPEN and is the fastest to reach from your current location (estimated 3 mins walking).
        </p>
        
        {/* Mock representation for Phase 12 nav */}
        <div className="mt-6 rounded border border-slate-700 bg-slate-800 p-4 text-center text-sm text-slate-400">
          [Map / Navigation UI will render here in Phase 12]
        </div>
      </div>
    </div>
  );
}
