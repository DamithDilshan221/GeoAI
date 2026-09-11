import { describe, it, expect } from 'vitest';
import type { OSRMStep } from './maneuvers';
import { stepInstruction, stepRotation, remainingSecondsToMinutes } from './maneuvers';

const makeStep = (type: string, modifier?: string, distance = 50): OSRMStep => ({
  maneuver: { type, modifier },
  distance,
});

describe('stepInstruction', () => {
  it('returns "Head" for depart', () => {
    expect(stepInstruction(makeStep('depart'))).toBe('Head');
  });

  it('returns "You have arrived" for arrive', () => {
    expect(stepInstruction(makeStep('arrive'))).toBe('You have arrived');
  });

  it('returns "Turn left" for turn+left', () => {
    expect(stepInstruction(makeStep('turn', 'left'))).toBe('Turn left');
  });

  it('returns "Turn right" for turn+right', () => {
    expect(stepInstruction(makeStep('turn', 'right'))).toBe('Turn right');
  });

  it('returns fallback "Continue" for unknown type', () => {
    expect(stepInstruction(makeStep('unknown_type'))).toBe('Continue');
  });
});

describe('stepRotation', () => {
  it('returns 0 for depart', () => {
    expect(stepRotation(makeStep('depart'))).toBe(0);
  });

  it('returns -90 for turn-left', () => {
    expect(stepRotation(makeStep('turn', 'left'))).toBe(-90);
  });

  it('returns 90 for turn-right', () => {
    expect(stepRotation(makeStep('turn', 'right'))).toBe(90);
  });

  it('returns 180 for u-turn', () => {
    expect(stepRotation(makeStep('turn', 'uturn'))).toBe(180);
  });

  it('returns 0 fallback for unknown type', () => {
    expect(stepRotation(makeStep('unknown_type'))).toBe(0);
  });
});

describe('remainingSecondsToMinutes', () => {
  it('returns "<1 min" for short distances', () => {
    expect(remainingSecondsToMinutes(60)).toBe('<1 min'); // 60m / 1.2 = 50s → <1 min
  });

  it('returns "1 min" for ~72 metres', () => {
    expect(remainingSecondsToMinutes(72)).toBe('1 min'); // 72/1.2 = 60s = 1 min
  });

  it('returns "5 min" for 360 metres', () => {
    expect(remainingSecondsToMinutes(360)).toBe('5 min'); // 360/1.2 = 300s = 5 min
  });
});
