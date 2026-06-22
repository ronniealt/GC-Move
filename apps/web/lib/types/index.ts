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

export interface UpcomingInspectionItem {
  id: string;
  property_id: string;
  property_address: string;
  property_suburb: string;
  scheduled_at: string | null;
  status: string;
}

export interface DashboardResponse {
  top_recommendations: TopPropertyItem[];
  properties_reviewed: number;
  new_this_week: number;
  shortlist_count: number;
  recent_journal_count: number;
  upcoming_inspections: UpcomingInspectionItem[];
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

export interface AdvisorHistoryResponse {
  thread_id: string | null;
  messages: AdvisorMessageResponse[];
}

// --- Suburbs ---

export interface SuburbMetricResponse {
  owner_occupier_rate: number | null;
  owner_occupier_score: number | null;
  family_density_pct: number | null;
  family_density_score: number | null;
  educational_attainment_pct: number | null;
  educational_attainment_score: number | null;
  median_weekly_household_income_aud: number | null;
  median_income_score: number | null;
  crime_index: number | null;
  crime_score: number | null;
  community_engagement_score: number | null;
  community_score: number | null;
}

export interface SuburbLifestyleResponse {
  cafe_restaurant_count: number;
  gym_fitness_count: number;
  park_reserve_count: number;
  shopping_centre_count: number;
  medical_gp_count: number;
  supermarket_count: number;
  burleigh_drive_minutes: number | null;
  beach_access_minutes: number | null;
  travel_to_broadbeach_min: number | null;
  travel_to_airport_min: number | null;
  burleigh_access_score: number | null;
  beach_access_score: number | null;
  wellness_infrastructure_score: number | null;
  cafe_dining_score: number | null;
  outdoor_recreation_score: number | null;
  shopping_score: number | null;
  lifestyle_score: number | null;
}

export interface SchoolSummaryResponse {
  id: string;
  name: string;
  sector: string;
  school_type: string;
  address_suburb: string;
  year_range: string | null;
}

export interface SuburbListItem {
  id: string;
  name: string;
  postcode: string;
  tier: string | null;
  tier_label: string;
  slug: string;
  community_score: number | null;
  lifestyle_score: number | null;
  beach_access_minutes: number | null;
}

export interface SuburbDetailResponse {
  id: string;
  name: string;
  postcode: string;
  tier: string | null;
  tier_label: string;
  slug: string;
  latitude: number;
  longitude: number;
  lga: string | null;
  metrics: SuburbMetricResponse | null;
  lifestyle: SuburbLifestyleResponse | null;
  schools: SchoolSummaryResponse[];
}

// --- Schools ---

export interface SchoolMetricResponse {
  naplan_reading_pct_above_nms: number | null;
  naplan_numeracy_pct_above_nms: number | null;
  wellbeing_score: number | null;
  parent_community_score: number | null;
  academic_outcomes_score: number | null;
  commute_score: number | null;
  extracurricular_score: number | null;
  pathway_score: number | null;
  school_score: number | null;
  attendance_rate_pct: number | null;
  annual_fee_aud: number | null;
  has_boarding: boolean;
  extracurricular_notes: string | null;
  data_year: number | null;
}

export interface SchoolListItem {
  id: string;
  name: string;
  school_type: string;
  sector: string;
  address_suburb: string;
  address_postcode: string | null;
  year_range: string | null;
  icsea: number | null;
  total_enrolments: number | null;
  website_url: string | null;
  metrics: SchoolMetricResponse | null;
}

// --- Preferences ---

export interface PreferenceResponse {
  id: string;
  family_id: string;
  attribute: string;
  category: string;
  current_weight: number;
  confidence: number;
  status: "Emerging" | "Confirmed" | "Contradicted" | "Retired" | "Manual";
  positive_signal_count: number;
  negative_signal_count: number;
  is_deal_breaker: boolean;
  notes: string | null;
  last_signal_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PreferenceUpdate {
  status?: string;
  current_weight?: number;
  is_deal_breaker?: boolean;
  notes?: string;
}

// --- Journal ---

export interface JournalPropertySnippet {
  id: string;
  address_street: string;
  address_suburb: string;
  listing_price_aud: number | null;
}

export interface JournalEntryResponse {
  id: string;
  family_id: string;
  property_id: string | null;
  suburb_id: string | null;
  entry_type: "note" | "reflection" | "decision" | "question" | "milestone" | "concern";
  title: string | null;
  body: string;
  mood: "excited" | "positive" | "neutral" | "uncertain" | "concerned" | null;
  tags: string[] | null;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  property: JournalPropertySnippet | null;
}

// --- Inspections ---

export interface InspectionPropertySnippet {
  id: string;
  address_street: string;
  address_suburb: string;
}

export interface InspectionResponse {
  id: string;
  family_id: string;
  property_id: string;
  inspection_type: string;
  scheduled_at: string | null;
  completed_at: string | null;
  status: "scheduled" | "completed" | "cancelled" | "missed";
  overall_impression: string | null;
  notes: string | null;
  property: InspectionPropertySnippet | null;
  created_at: string;
  updated_at: string;
}

export interface InspectionCreate {
  property_id: string;
  scheduled_at: string;
  notes?: string;
  inspection_type?: string;
}

export interface InspectionUpdate {
  scheduled_at?: string;
  completed_at?: string;
  status?: string;
  notes?: string;
  overall_impression?: string;
}

export interface JournalEntryCreate {
  title?: string;
  body: string;
  entry_type?: string;
  mood?: string;
  tags?: string[];
  property_id?: string;
  suburb_id?: string;
  is_pinned?: boolean;
}
