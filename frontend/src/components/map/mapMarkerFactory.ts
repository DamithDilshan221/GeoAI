import L from 'leaflet';

const getCategoryColor = (cat: string) => {
  if (cat.includes('male') && !cat.includes('female')) return '#2F6FED'; // men
  if (cat.includes('female')) return '#FF5FA0'; // women
  if (cat.includes('unisex') || cat.includes('neutral')) return '#E7AE4E'; // unisex
  if (cat.includes('accessible')) return '#6E7FD1'; // accessible
  return '#3FCBBE'; // default teal
};

const CATEGORY_ICON_SVG: Record<string, string> = {
  male: `<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="5" r="3"/><path d="M12 9c-3 0-5 2-5 5v7h3v-6h4v6h3v-7c0-3-2-5-5-5z"/></svg>`,
  female: `<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="4.5" r="3"/><path d="M12 8c-1 0-1.8.6-2.1 1.6L8 15h2l.4 6h3.2l.4-6h2l-1.9-5.4C13.8 8.6 13 8 12 8z"/></svg>`,
  unisex: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 8v8M15 8v8M9 12h6"/></svg>`,
  accessible: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.2" r="1.7"/><path d="M11 8.5v4.5l-3.5 5.5"/><path d="M11 10h5l-1.2 3"/><circle cx="15" cy="17.5" r="3.3"/></svg>`
};
const GENERIC_PIN_SVG = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-7.3-7-12a7 7 0 0 1 14 0c0 4.7-7 12-7 12z"/><circle cx="12" cy="9" r="2.3"/></svg>`;

function resolveCategoryKey(category?: string): string {
  const cat = category?.toLowerCase() || '';
  if (cat.includes('male') && !cat.includes('female')) return 'male';
  if (cat.includes('female')) return 'female';
  if (cat.includes('unisex') || cat.includes('neutral')) return 'unisex';
  if (cat.includes('accessible')) return 'accessible';
  return 'other';
}

export function buildFacilityDivIcon(category?: string): L.DivIcon {
  const color = category ? getCategoryColor(category.toLowerCase()) : '#3FCBBE';
  const glyph = CATEGORY_ICON_SVG[resolveCategoryKey(category)] ?? GENERIC_PIN_SVG;
  return L.divIcon({
    className: '',
    html: `<div class="leaflet-div-pin" style="background:${color}">${glyph}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 28],
  });
}

export function buildUserLocationDivIcon(): L.DivIcon {
  return L.divIcon({ className: '', html: '<div class="user-dot"></div>', iconSize: [16, 16] });
}
