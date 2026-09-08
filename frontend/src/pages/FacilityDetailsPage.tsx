import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useFacility } from '../hooks/useFacility';
import { LoadingState } from '../components/status/LoadingState';
import { ErrorState } from '../components/status/ErrorState';

export function FacilityDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const facilityId = parseInt(id || '', 10);
  
  const { data: facility, isLoading, error, refetch } = useFacility(facilityId);

  if (isLoading) return <LoadingState message="Loading facility details..." />;

  if (error) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const is404 = (error as any).response?.status === 404;
    
    if (is404) {
      return (
        <div className="text-center p-8">
          <h2 className="text-2xl font-bold text-slate-300 mb-4">Facility Not Found</h2>
          <p className="text-slate-400 mb-6">The facility you're looking for doesn't exist or has been removed.</p>
          <Link to="/" className="text-blue-400 hover:text-blue-300 underline">Return to Search</Link>
        </div>
      );
    }
    return <ErrorState message="Failed to load facility details." onRetry={refetch} />;
  }

  if (!facility) return null;

  return (
    <div className="space-y-6">
      <Link to="/nearby" className="text-sm text-blue-400 hover:text-blue-300 mb-4 inline-block">&larr; Back to list</Link>
      
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
          <div>
            <h2 className="text-3xl font-bold text-white">{facility.name}</h2>
            <p className="text-lg text-slate-400 mt-1">{facility.category}</p>
          </div>
          
          <div className="flex flex-col items-start md:items-end gap-2">
            <span
              className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${
                facility.status === 'OPEN'
                  ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-800'
                  : facility.status === 'CLOSED'
                    ? 'bg-red-900/50 text-red-400 border border-red-800'
                    : 'bg-yellow-900/50 text-yellow-400 border border-yellow-800'
              }`}
            >
              {facility.status.replace('_', ' ')}
            </span>
            
            {facility.rating !== null && (
              <div className="flex items-center space-x-1 text-yellow-400">
                <span className="font-bold">{facility.rating.toFixed(1)}</span>
                <span>★</span>
              </div>
            )}
          </div>
        </div>

        {facility.accessibility?.wheelchair_friendly && (
          <div className="mt-6 inline-flex items-center space-x-2 rounded border border-blue-800/50 bg-blue-900/20 px-3 py-2 text-sm text-blue-300">
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
            </svg>
            <span>Wheelchair accessible</span>
          </div>
        )}
      </div>
      
      <div className="flex justify-center mt-8">
        <Link 
          to="/recommend"
          className="rounded-lg bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-500 shadow-lg shadow-blue-900/20"
        >
          Navigate Here
        </Link>
      </div>
    </div>
  );
}
