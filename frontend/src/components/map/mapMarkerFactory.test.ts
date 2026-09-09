/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  buildFacilityPin,
  buildUserLocationPin,
  buildFacilityInfoWindowContent,
} from './mapMarkerFactory';
import { setupGoogleMapsMock, resetGoogleMapsMock } from '../../test-utils/googleMapsMock';

describe('mapMarkerFactory', () => {
  beforeEach(() => {
    setupGoogleMapsMock();
  });

  afterEach(() => {
    resetGoogleMapsMock();
  });

  it('buildFacilityPin constructs a red-ish PinElement', () => {
    const pin = buildFacilityPin(google.maps.marker.PinElement) as any;
    expect(pin.options.background).toBe('#3FCBBE');
    expect(pin.options.borderColor).toBe('#FFFFFF');
    expect(pin.options.glyphColor).toBe('#FFFFFF');
  });

  it('buildUserLocationPin constructs a blue PinElement', () => {
    const pin = buildUserLocationPin(google.maps.marker.PinElement) as any;
    expect(pin.options.background).toBe('#2C7BE5');
    expect(pin.options.borderColor).toBe('#FFFFFF');
    expect(pin.options.glyph).toBe('●');
    expect(pin.options.scale).toBe(0.8);
  });

  it('buildFacilityInfoWindowContent returns an HTMLElement that triggers onViewDetails on click', () => {
    const onViewDetails = vi.fn();
    const content = buildFacilityInfoWindowContent('Test Facility', onViewDetails);
    
    expect(content).toBeInstanceOf(HTMLElement);
    expect(content.querySelector('h3')?.textContent).toBe('Test Facility');
    
    const button = content.querySelector('button');
    expect(button).not.toBeNull();
    expect(button?.textContent).toBe('View details');
    
    button?.click();
    expect(onViewDetails).toHaveBeenCalledTimes(1);
  });
});
