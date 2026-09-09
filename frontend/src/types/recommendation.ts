import type { Facility } from './facility';

export interface FacilityRecommendation {
  id: number;
  name: string;
  category: string;
  status: Facility['status'];
  rating: number | null;
  distance_m: number;
  estimated_time_s: number;
  travel_source: 'network' | 'straight_line_estimate';
  predicted_usage: number;
  crowd_level: string;
  prediction_source: string;
  recommendation_score: number;
  rank_position: number;
}

export interface RecommendationResponse {
  recommended_facility: FacilityRecommendation | null;
  ranked_facilities: FacilityRecommendation[];
  explanation: string | null;
  message: string | null;
}
