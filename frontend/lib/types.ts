export interface PricingSummary {
  min_price: number;
  max_price: number;
  average_price: number;
  median_price: number;
  suggested_min: number;
  suggested_max: number;
  underpriced: Array<{ title: string; price: number; shop_name: string }>;
  overpriced: Array<{ title: string; price: number; shop_name: string }>;
}

export interface KeywordSummary {
  top_keywords: Array<{ keyword: string; count: number }>;
  common_tags: Array<{ tag: string; count: number }>;
  missing_opportunities: string[];
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
}

export interface Competitor {
  id: number;
  analysis_id: number;
  competitor_name: string;
  platform: string;
  product_count: number;
  average_price: number;
  total_reviews: number;
  common_keywords: string[];
  positioning_summary: string;
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
}

export interface AnalysisCreateRequest {
  platform: string;
  input_type: "shop_url" | "product_url" | "marketplace_url" | "keyword";
  input_value: string;
  country: string;
  currency: string;
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

export const COUNTRIES = ["US", "UK", "CA", "AU", "DE", "FR"];
export const CURRENCIES = ["USD", "GBP", "CAD", "AUD", "EUR"];
