import React from 'react';
import { Link } from 'react-router-dom';
import { NearbyFacility } from '../../types/facility';

interface FacilityListItemProps {
  facility: NearbyFacility;
}

export function FacilityListItem({ facility }: FacilityListItemProps) {
  return (
    <Link
      to={`/facilities/${facility.id}`}
      className="block rounded-lg border border-slate-700 bg-slate-800 p-4 transition-colors hover:border-slate-500 hover:bg-slate-700/50"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">{facility.name}</h3>
          <p className="text-sm text-slate-400">{facility.category}</p>
        </div>
        <div className="text-right">
          <span
            className={`inline-block rounded px-2 py-1 text-xs font-medium ${
              facility.status === 'OPEN'
                ? 'bg-emerald-900/50 text-emerald-400'
                : facility.status === 'CLOSED'
                  ? 'bg-red-900/50 text-red-400'
                  : 'bg-yellow-900/50 text-yellow-400'
            }`}
          >
            {facility.status.replace('_', ' ')}
          </span>
          <p className="mt-2 text-sm text-slate-300">{facility.distance_m}m away</p>
        </div>
      </div>
    </Link>
  );
}
