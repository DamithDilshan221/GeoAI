export function buildFacilityPin(PinElementCtor: typeof google.maps.marker.PinElement) {
  return new PinElementCtor({
    background: '#EA4335',
    borderColor: '#B31412',
    glyphColor: '#FFFFFF',
  });
}

export function buildUserLocationPin(PinElementCtor: typeof google.maps.marker.PinElement) {
  return new PinElementCtor({
    background: '#4285F4',
    borderColor: '#1A56DB',
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
