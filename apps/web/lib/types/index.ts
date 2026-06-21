// Mirror Pydantic schemas exactly — keep in sync with apps/api/app/schemas/

export type RecommendationLevel = "prioritise_immediately" | "inspect" | "monitor" | "ignore";
export type PropertyStatus = "ingesting" | "evaluating" | "evaluated" | "filtered" | "failed";

export interface Family {
  id: string;
  name: string;
  budget_min: number | null;
  budget_max: number | null;
  move_timeline: string | null;
  created_at: string;
}

export interface FamilyMember {
  id: string;
  family_id: string;
  name: string;
  role: string;
  age: number | null;
}

export interface Property {
  id: string;
  family_id: string;
  address: string;
  suburb: string;
  postcode: string;
  price_display: string | null;
  bedrooms: number | null;
  bathrooms: number | null;
  car_spaces: number | null;
  land_size_sqm: number | null;
  house_size_sqm: number | null;
  property_type: string;
  source_url: string;
  status: PropertyStatus;
  created_at: string;
}

export interface EvaluationScores {
  community: number | null;
  lifestyle: number | null;
  school: number | null;
  property_quality: number | null;
  financial: number | null;
  family_fit: number | null;
  five_year_fit: number | null;
  confidence: number;
}

export interface PropertyEvaluation {
  id: string;
  property_id: string;
  recommendation: RecommendationLevel;
  scores: EvaluationScores;
  has_critical_risk: boolean;
  meets_non_negotiables: boolean;
  executive_summary: string;
  why_it_fits: string;
  why_not_perfect: string;
  what_to_verify: string[];
  main_trade_off: string;
  next_action: string;
  five_year_prediction: string;
}

export interface DashboardResponse {
  top_recommendations: Array<Property & { evaluation: PropertyEvaluation }>;
  properties_reviewed: number;
  new_this_week: number;
  shortlist_count: number;
}
