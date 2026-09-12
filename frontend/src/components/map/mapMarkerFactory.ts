import L from 'leaflet';

const getCategoryColor = (cat: string) => {
  if (cat.includes('male') && !cat.includes('female')) return '#2F6FED'; // men
  if (cat.includes('female')) return '#FF5FA0'; // women
  return '#3FCBBE'; // default teal
};

const CATEGORY_ICON_SVG: Record<string, string> = {
  male: `<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="5" r="3"/><path d="M12 9c-3 0-5 2-5 5v7h3v-6h4v6h3v-7c0-3-2-5-5-5z"/></svg>`,
  female: `<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="4.5" r="3"/><path d="M12 8c-1 0-1.8.6-2.1 1.6L8 15h2l.4 6h3.2l.4-6h2l-1.9-5.4C13.8 8.6 13 8 12 8z"/></svg>`,
};
const GENERIC_PIN_SVG = `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-7.3-7-12a7 7 0 0 1 14 0c0 4.7-7 12-7 12z"/><circle cx="12" cy="9" r="2.3"/></svg>`;

function resolveCategoryKey(category?: string): string {
  const cat = category?.toLowerCase() || '';
  if (cat.includes('male') && !cat.includes('female')) return 'male';
  if (cat.includes('female')) return 'female';
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
