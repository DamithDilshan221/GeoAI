import { describe, it, expect } from 'vitest';
import { buildFacilityDivIcon, buildUserLocationDivIcon } from './mapMarkerFactory';

describe('mapMarkerFactory', () => {
  describe('buildFacilityDivIcon', () => {
    it('returns a divIcon for male category', () => {
      const icon = buildFacilityDivIcon('male');
      expect(icon.options.className).toBe('');
      expect(icon.options.iconSize).toEqual([30, 30]);
      expect(icon.options.html).toContain('background:#2F6FED');
      expect(icon.options.html).toContain('<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="5" r="3"/><path d="M12 9c-3 0-5 2-5 5v7h3v-6h4v6h3v-7c0-3-2-5-5-5z"/></svg>');
    });

    it('returns a default pin for unknown category', () => {
      const icon = buildFacilityDivIcon('unknown_cat');
      expect(icon.options.html).toContain('background:#3FCBBE');
      expect(icon.options.html).toContain('<circle cx="12" cy="9" r="2.3"/>');
    });

    it('returns a default pin when category is undefined', () => {
      const icon = buildFacilityDivIcon(undefined);
      expect(icon.options.html).toContain('background:#3FCBBE');
      expect(icon.options.html).toContain('<circle cx="12" cy="9" r="2.3"/>');
    });
  });

  describe('buildUserLocationDivIcon', () => {
    it('returns a user-dot icon', () => {
      const icon = buildUserLocationDivIcon();
      expect(icon.options.html).toContain('class="user-dot"');
      expect(icon.options.iconSize).toEqual([16, 16]);
    });
  });
});
