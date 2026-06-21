// Mirror Pydantic schemas exactly — keep in sync with apps/api/app/schemas/

export type RecommendationLevel = "prioritise_immediately" | "inspect" | "monitor" | "ignore";
export type PropertyStatus = "saved" | "shortlisted" | "inspecting" | "offer" | "rejected" | "sold" | "withdrawn";
export type PropertyType = "house" | "townhouse" | "unit" | "acreage" | "other";

// --- Family ---

export interface FamilyResponse {
  id: string;
  display_name: string;
  primary_suburb_target: string | null;
  budget_min_aud: number | null;
  budget_max_aud: number | null;
  target_move_date: string | null;
  is_active: boolean;
  onboarding_completed: boolean;
  scoring_model_version: string;
  weight_community: number;
  weight_lifestyle: number;
  weight_school: number;
  weight_property: number;
  weight_financial: number;
  created_at: string;
}

export interface FamilyMemberResponse {
  id: string;
  family_id: string;
  first_name: string;
  role: "primary_adult" | "secondary_adult" | "child" | "pet";
  age: number | null;
  birth_year: number | null;
  notes: string | null;
  avatar_emoji: string | null;
  created_at: string;
}

export interface FamilyCreateBody {
  display_name: string;
  user_display_name: string;
  user_email: string;
  primary_suburb_target?: string;
  budget_min_aud?: number;
  budget_max_aud?: number;
}

export interface FamilyUpdate {
  display_name?: string;
  primary_suburb_target?: string;
  budget_min_aud?: number;
  budget_max_aud?: number;
  target_move_date?: string;
  weight_community?: number;
  weight_lifestyle?: number;
  weight_school?: number;
  weight_property?: number;
  weight_financial?: number;
}

export interface FamilyMemberCreate {
  first_name: string;
  role: "primary_adult" | "secondary_adult" | "child" | "pet";
  age?: number;
  birth_year?: number;
  notes?: string;
  avatar_emoji?: string;
}

export interface InviteValidateResponse {
  family_name: string;
  inviter_name: string;
  email: string;
  role: string;
}

// --- Property ---

export interface PropertyFeatureResponse {
  feature_key: string;
  feature_value: string;
  feature_type: "boolean" | "text" | "numeric" | "enum";
  confidence: number | null;
  source: "extracted" | "manual" | "inferred";
}

export interface PropertyImageResponse {
  image_url: string;
  image_order: number;
  image_type: "listing" | "floorplan" | "streetview" | "inspection";
  caption: string | null;
}

export interface PropertyResponse {
  id: string;
  family_id: string;
  suburb_id: string | null;
  source_url: string | null;
  source_platform: "realestate" | "domain" | "manual" | "agent" | null;
  address_street: string;
  address_suburb: string;
  address_state: string;
  address_postcode: string;
  property_type: PropertyType;
  bedrooms: number | null;
  bathrooms: number | null;
  car_spaces: number | null;
  land_area_sqm: number | null;
  house_area_sqm: number | null;
  listing_price_aud: number | null;
  price_range_low_aud: number | null;
  price_range_high_aud: number | null;
  price_is_range: boolean;
  description_text: string | null;
  flood_risk_category: "high" | "medium" | "low" | "none" | "unknown" | null;
  agent_name: string | null;
  agency_name: string | null;
  data_quality_score: number;
  status: PropertyStatus;
  is_favourite: boolean;
  family_notes: string | null;
  created_at: string;
  features: PropertyFeatureResponse[];
  images: PropertyImageResponse[];
}

export interface PropertyListResponse {
  id: string;
  address_street: string;
  address_suburb: string;
  address_postcode: string;
  property_type: PropertyType;
  bedrooms: number | null;
  bathrooms: number | null;
  listing_price_aud: number | null;
  status: PropertyStatus;
  is_favourite: boolean;
  created_at: string;
}

export interface PropertyIngestRequest {
  url: string;
}

export interface PropertyIngestResponse {
  property_id: string;
  status: string;
}

// --- Evaluation ---

export interface EvaluationScoresResponse {
  community_score: number | null;
  lifestyle_score: number | null;
  school_score: number | null;
  property_score: number | null;
  financial_score: number | null;
  risk_score: number | null;
  family_fit_score: number | null;
  five_year_fit_score: number | null;
}

export interface MemberCommentaryResponse {
  member_id: string;
  commentary: string;
  key_positives: string[] | null;
  key_concerns: string[] | null;
  fit_score: number | null;
}

export interface EvaluationResponse {
  id: string;
  property_id: string;
  evaluation_version: string;
  evaluated_at: string;
  is_current: boolean;
  confidence_score: number;
  executive_summary: string | null;
  community_narrative: string | null;
  lifestyle_narrative: string | null;
  school_narrative: string | null;
  property_narrative: string | null;
  financial_narrative: string | null;
  five_year_narrative: string | null;
  deal_breakers_flagged: string[] | null;
  scores: EvaluationScoresResponse | null;
  per_member: MemberCommentaryResponse[];
}

export interface RecommendationResponse {
  id: string;
  property_id: string;
  rank_position: number | null;
  family_fit_score: number | null;
  score_delta: number | null;
  status: "active" | "archived" | "dismissed" | "accepted";
  headline: string | null;
  summary: string | null;
  ranked_at: string;
}

// --- Dashboard ---

export interface TopPropertyItem {
  id: string;
  address_street: string;
  address_suburb: string;
  listing_price_aud: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  status: PropertyStatus;
  rank_position: number | null;
  family_fit_score: number | null;
  confidence_score: number | null;
  executive_summary: string | null;
  suburb_tier: string | null;
  scores: EvaluationScoresResponse | null;
  hero_image_url: string | null;
}

export interface DashboardResponse {
  top_recommendations: TopPropertyItem[];
  properties_reviewed: number;
  new_this_week: number;
  shortlist_count: number;
  recent_journal_count: number;
}

// --- Advisor ---

export interface AdvisorMessageRequest {
  message: string;
  property_id?: string;
}

export interface AdvisorMessageResponse {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}
