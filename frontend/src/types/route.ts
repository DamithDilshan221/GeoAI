export interface Route {
  distance_m: number;
  estimated_time_s: number;
  path: [number, number][];
  source: 'network' | 'straight_line_estimate';
}
