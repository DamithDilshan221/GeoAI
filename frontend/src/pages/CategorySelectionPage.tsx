import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCategories } from '../hooks/useCategories';
import { useGeolocation } from '../hooks/useGeolocation';
import { useSearchContext } from '../context/SearchContext';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';
import { PermissionDeniedState } from '../components/status/PermissionDeniedState';
import { CategoryButton } from '../components/facility/CategoryButton';

export function CategorySelectionPage() {
  const navigate = useNavigate();
  const { data: categories, isLoading, error, refetch } = useCategories();
  const { status: geoStatus, errorMessage, request: requestLocation } = useGeolocation();
  const { state, dispatch } = useSearchContext();

  useEffect(() => {
    if (geoStatus === 'granted') {
      navigate('/nearby');
    }
  }, [geoStatus, navigate]);

  if (isLoading) return <LoadingState message="Loading categories..." />;
  if (error) return <ErrorState message="Failed to load categories." onRetry={refetch} />;

  if (geoStatus === 'requesting') {
    return <LoadingState message="Locating you..." />;
  }

  if (geoStatus === 'denied' || geoStatus === 'unavailable') {
    return (
      <PermissionDeniedState
        message={errorMessage || 'Location error'}
        onRetry={requestLocation}
      />
    );
  }

  const handleCategoryClick = (code: string) => {
    dispatch({ type: 'SET_CATEGORY', payload: code });
    requestLocation();
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold tracking-tight text-white">Find a Facility</h2>
        <p className="mt-2 text-slate-400">Select what you're looking for to see nearby options.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categories?.map((cat) => (
          <CategoryButton
            key={cat.id}
            label={cat.label}
            code={cat.code}
            isSelected={state.selectedCategory === cat.code}
            onClick={() => handleCategoryClick(cat.code)}
          />
        ))}
      </div>

      <div className="mt-8 flex items-center justify-center space-x-3 rounded-lg border border-slate-700 bg-slate-800/50 p-4">
        <input
          type="checkbox"
          id="accessibleOnly"
          checked={state.accessibleOnly}
          onChange={(e) => dispatch({ type: 'SET_ACCESSIBLE_ONLY', payload: e.target.checked })}
          className="h-5 w-5 rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800"
        />
        <label htmlFor="accessibleOnly" className="text-sm font-medium text-slate-300">
          Wheelchair-accessible routes only
        </label>
      </div>
    </div>
  );
}
