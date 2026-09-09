import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import type { NearbyFacility } from '../../types/facility';

interface FacilityListItemProps {
  facility: NearbyFacility;
}

export function FacilityListItem({ facility }: FacilityListItemProps) {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);

  const getCategoryTheme = (cat: string) => {
    const c = cat.toLowerCase();
    if (c.includes('men') && !c.includes('women')) return { color: 'var(--men)', label: "Men's" };
    if (c.includes('women') || c.includes('female')) return { color: 'var(--women)', label: "Women's" };
    if (c.includes('unisex') || c.includes('neutral')) return { color: 'var(--amber-dark)', label: 'Gender-Neutral' };
    if (c.includes('access') || c.includes('wheelchair')) return { color: 'var(--indigo)', label: 'Accessible' };
    return { color: 'var(--teal)', label: cat };
  };

  const theme = getCategoryTheme(facility.category);

  return (
    <div
      onClick={() => navigate(`/facilities/${facility.id}`)}
      className="flex gap-3 bg-paper text-ink rounded-[16px] p-[13px] mb-2.5 cursor-pointer shadow-card transition-transform active:scale-[0.985] relative"
      style={{ borderLeft: `5px solid ${theme.color}` }}
    >
      <button 
        className={`absolute top-2 right-2 w-[26px] h-[26px] rounded-full border-none bg-transparent flex items-center justify-center cursor-pointer z-10 ${saved ? 'text-amber-dark' : 'text-muted-soft'}`}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setSaved(!saved);
        }}
        aria-label="Save"
      >
        {saved ? (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
        ) : (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>
        )}
      </button>
      
      <div 
        className="w-10 h-10 rounded-[11px] flex items-center justify-center shrink-0 text-white"
        style={{ background: theme.color }}
      >
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 21s-7-7.3-7-12a7 7 0 0 1 14 0c0 4.7-7 12-7 12z"/><circle cx="12" cy="9" r="2.3"/></svg>
      </div>

      <div className="flex-1 min-w-0 pr-4">
        <h3 className="m-0 mb-0.5 text-[14.5px] font-semibold leading-[1.3] truncate">{facility.name}</h3>
        <p className="m-0 text-[12.5px] text-muted-soft truncate">{facility.category}</p>
      </div>
      <div className="shrink-0 text-right flex flex-col justify-center items-end gap-[5px]">
        <span className="font-bold text-[14px] text-ink">{facility.distance_m} m</span>
        <span className="text-[10.5px] font-bold py-[3px] px-[9px] rounded-full text-white" style={{ background: theme.color }}>
          {theme.label}
        </span>
      </div>
    </div>
  );
}
