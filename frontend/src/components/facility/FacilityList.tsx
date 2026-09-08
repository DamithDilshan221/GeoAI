import React from 'react';
import { NearbyFacility } from '../../types/facility';
import { FacilityListItem } from './FacilityListItem';
import { EmptyState } from '../status/EmptyState';

interface FacilityListProps {
  facilities: NearbyFacility[];
}

export function FacilityList({ facilities }: FacilityListProps) {
  if (facilities.length === 0) {
    return <EmptyState message="No facilities found nearby." />;
  }

  return (
    <div className="space-y-4">
      {facilities.map((facility) => (
        <FacilityListItem key={facility.id} facility={facility} />
      ))}
    </div>
  );
}
