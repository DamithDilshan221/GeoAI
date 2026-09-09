const getCategoryColor = (cat: string) => {
  const c = cat.toLowerCase();
  if (c.includes('men') && !c.includes('women')) return '#2F6FED'; // men
  if (c.includes('women') || c.includes('female')) return '#FF5FA0'; // women
  if (c.includes('unisex') || c.includes('neutral')) return '#E7AE4E'; // amber
  if (c.includes('access') || c.includes('wheelchair')) return '#6E7FD1'; // indigo
  return '#3FCBBE'; // teal
};

export function buildFacilityPin(PinElementCtor: typeof google.maps.marker.PinElement, category?: string) {
  const color = category ? getCategoryColor(category) : '#3FCBBE';
  return new PinElementCtor({
    background: color,
    borderColor: '#FFFFFF',
    glyphColor: '#FFFFFF',
  });
}

export function buildUserLocationPin(PinElementCtor: typeof google.maps.marker.PinElement) {
  return new PinElementCtor({
    background: '#2C7BE5',
    borderColor: '#FFFFFF',
    glyph: '●',
    scale: 0.8,
  });
}

export function buildFacilityInfoWindowContent(
  facilityName: string,
  onViewDetails: () => void
): HTMLElement {
  const container = document.createElement('div');
  container.className = 'p-2 space-y-2';

  const title = document.createElement('h3');
  title.className = 'font-semibold text-slate-900';
  title.textContent = facilityName;

  const button = document.createElement('button');
  button.className = 'w-full bg-blue-600 text-white rounded px-3 py-1.5 text-sm hover:bg-blue-700 transition-colors';
  button.textContent = 'View details';
  button.addEventListener('click', onViewDetails);

  container.appendChild(title);
  container.appendChild(button);

  return container;
}
