export interface PricingSummary {
  min_price: number;
  max_price: number;
  average_price: number;
  median_price: number;
  suggested_min: number;
  suggested_max: number;
  underpriced: Array<{ title: string; price: number; shop_name: string }>;
  overpriced: Array<{ title: string; price: number; shop_name: string }>;
  competitor_min_price?: number;
  competitor_max_price?: number;
  competitor_average_price?: number;
  competitor_median_price?: number;
  user_average_price?: number;
  price_buckets?: Array<{ range: string; count: number }>;
  pricing_recommendation?: string;
}

export interface KeywordInsight {
  tag: string;
  keyword_type: string;
  competitor_usage_count: number;
  user_usage_count: number;
  search_volume_estimate: string;
  competition_estimate: string;
  engagement_estimate: string;
  opportunity_score: number;
  trend_direction: string;
  related_tags: string[];
  example_competitor_listings: Array<{ title: string; url: string; shop_name: string; price: number }>;
  example_user_listings: Array<{ title: string; url: string; shop_name: string; price: number }>;
  suggested_action: string;
  suggested_title_phrases?: string[];
  suggested_etsy_tags?: string[];
  suggested_description_phrase?: string;
  pricing_context?: string | null;
}

export interface MissingTagOpportunity {
  tag: string;
  competitor_usage_count: number;
  user_usage_count: number;
  example_competitor_listings: Array<{ title: string; url: string; shop_name: string; price: number }>;
  why_it_matters: string;
  suggested_listings_to_add: string[];
}

export interface LongTailOpportunity {
  tag: string;
  estimated_demand: string;
  estimated_competition: string;
  opportunity_score: number;
  recommended_listing_type: string;
  suggested_title_phrase: string;
  suggested_etsy_tag: string;
}

export interface TagGapAnalysis {
  user_frequent_tags: string[];
  competitor_frequent_tags: string[];
  shared_tags: string[];
  missing_tags: string[];
  weak_generic_tags: string[];
}

export interface TagSummaryStats {
  total_tags_analyzed: number;
  top_opportunity_tag: string;
  highest_competitor_tag: string;
  missing_tags_count: number;
  overused_generic_count: number;
  long_tail_count: number;
}

export interface KeywordSummary {
  top_keywords: Array<{ keyword: string; count: number }>;
  common_tags: Array<{ tag: string; count: number }>;
  missing_opportunities: string[];
  competitor_keywords?: Array<{ keyword: string; count: number }>;
  keyword_clusters?: Array<{ name: string; keywords: string[] }>;
  suggested_actions?: string[];
  tag_insights?: KeywordInsight[];
  summary_stats?: TagSummaryStats;
  missing_tag_opportunities?: MissingTagOpportunity[];
  long_tail_opportunities?: LongTailOpportunity[];
  tag_gap_analysis?: TagGapAnalysis;
}

export interface Listing {
  id: number;
  analysis_id: number;
  platform: string;
  title: string;
  url: string;
  shop_name: string;
  price: number;
  currency: string;
  rating: number;
  review_count: number;
  image_url: string;
  description: string;
  tags: string[];
  detected_keywords: string[];
  listing_source?: "user_shop" | "competitor_search" | "user" | "competitor";
}

export interface Competitor {
  id: number;
  analysis_id: number;
  competitor_name: string;
  platform: string;
  product_count: number;
  average_price: number;
  total_reviews: number;
  average_rating: number;
  common_keywords: string[];
  matched_queries: string[];
  example_listing_urls: string[];
  example_listing_titles: string[];
  match_score: number;
  positioning_summary: string;
}

export interface CompetitorDetail extends Competitor {
  discovered_label: string;
  competing_listings: Array<{
    title: string;
    url: string;
    price: number;
    rating: number;
    review_count: number;
    image_url: string;
  }>;
  price_comparison: {
    user_average_price: number;
    competitor_average_price: number;
    delta: number;
  };
  keyword_overlap: string[];
  user_unique_keywords: string[];
  competitor_unique_keywords: string[];
  product_gaps: string[];
  differentiation_opportunities: string[];
}

export interface ListingIssue {
  id: number;
  analysis_id: number;
  listing_id: number | null;
  severity: "low" | "medium" | "high";
  category: string;
  issue: string;
  suggestion: string;
}

export interface Recommendation {
  id: number;
  analysis_id: number;
  listing_id: number | null;
  category: string;
  recommendation: string;
  reasoning: string;
  confidence: number;
  created_at?: string;
}

export interface Trend {
  id: number;
  analysis_id: number;
  trend_name: string;
  trend_type: string;
  evidence: string;
  opportunity: string;
  competitor_examples?: Array<{ title: string; shop_name: string; price: number; url: string }>;
  suggested_product_idea?: string;
  keywords?: string[];
  price_range?: string;
  confidence?: number;
}

export interface Analysis {
  id: number;
  platform: string;
  input_type: string;
  input_value: string;
  country: string;
  currency: string;
  status: string;
  data_source: string;
  created_at: string;
  updated_at: string;
  pricing_summary?: PricingSummary;
  keyword_summary?: KeywordSummary;
}

export interface AnalysisDetail extends Analysis {
  listings: Listing[];
  competitors: Competitor[];
  listing_issues: ListingIssue[];
  recommendations: Recommendation[];
  trends: Trend[];
  warning?: string;
  generated_queries?: string[];
}

export interface AnalysisCreateRequest {
  platform: string;
  input_type: "shop_name" | "shop_url" | "product_url" | "marketplace_url" | "keyword";
  input_value: string;
  country: string;
  currency: string;
  language?: string;
  locale?: string;
}

export interface FreeformResponse {
  answer: string;
  supporting_evidence: string[];
  uncertainty_notes: string[];
  data_source: string;
}

export interface CodexStatus {
  enabled: boolean;
  mode: string;
  allow_file_patch: boolean;
  require_human_review: boolean;
  message: string;
}

export interface CodexAgentResponse {
  success: boolean;
  enabled: boolean;
  message: string;
  result: Record<string, unknown>;
}

export interface SettingsStatus {
  default_country: string;
  default_language: string;
  default_locale: string;
  default_currency: string;
  bright_data_configured: boolean;
  openai_configured: boolean;
  codex_enabled: boolean;
  database_status: string;
  backend_api_url: string;
  data_mode: string;
}

export const PLATFORMS = [
  { value: "etsy", label: "Etsy" },
  { value: "google_shopping", label: "Google Shopping" },
  { value: "amazon", label: "Amazon (stub)" },
  { value: "ebay", label: "eBay (stub)" },
  { value: "shopify", label: "Shopify (stub)" },
  { value: "shopee", label: "Shopee (stub)" },
  { value: "tiktok_shop", label: "TikTok Shop (stub)" },
  { value: "generic", label: "Generic Marketplace" },
];

export const INPUT_TYPES = [
  { value: "keyword", label: "Niche Keyword" },
  { value: "shop_url", label: "Shop URL" },
  { value: "product_url", label: "Product URL" },
  { value: "marketplace_url", label: "Marketplace URL" },
];

export const COUNTRY_OPTIONS = [
  { value: "US", label: "United States" },
  { value: "UK", label: "United Kingdom" },
  { value: "CA", label: "Canada" },
  { value: "AU", label: "Australia" },
  { value: "DE", label: "Germany" },
  { value: "FR", label: "France" },
];

export const LANGUAGE_OPTIONS = [
  { value: "en-US", label: "English" },
  { value: "es-ES", label: "Spanish" },
  { value: "fr-FR", label: "French" },
  { value: "de-DE", label: "German" },
];

export const COUNTRIES = COUNTRY_OPTIONS.map((option) => option.value);
export const CURRENCIES = ["USD", "GBP", "CAD", "AUD", "EUR"];
export const LANGUAGES = LANGUAGE_OPTIONS.map((option) => option.value);
