"""Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from app.config import get_settings


class InputType(str, Enum):
    shop_name = "shop_name"
    shop_url = "shop_url"
    product_url = "product_url"
    marketplace_url = "marketplace_url"
    keyword = "keyword"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ProductListingSchema(BaseModel):
    platform: str
    title: str
    url: str = ""
    shop_name: str = ""
    price: float = 0.0
    currency: str = "USD"
    rating: float = 0.0
    review_count: int = 0
    image_url: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    detected_keywords: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    listing_source: str = ""


class AnalysisCreate(BaseModel):
    platform: str
    input_type: InputType
    input_value: str
    country: str = Field(default_factory=lambda: get_settings().default_country)
    currency: str = Field(default_factory=lambda: get_settings().default_currency)
    language: str = Field(default_factory=lambda: get_settings().default_language)
    locale: str = Field(default_factory=lambda: get_settings().default_locale)

    @model_validator(mode="after")
    def apply_locale_defaults(self) -> "AnalysisCreate":
        settings = get_settings()
        if not self.language:
            self.language = settings.default_language
        if not self.locale:
            self.locale = settings.default_locale
        if not self.country:
            self.country = settings.default_country
        if not self.currency:
            self.currency = settings.default_currency
        return self


class ListingRead(BaseModel):
    id: int
    analysis_id: int
    platform: str
    title: str
    url: str
    shop_name: str
    price: float
    currency: str
    rating: float
    review_count: int
    image_url: str
    description: str
    tags: List[str]
    detected_keywords: List[str]
    listing_source: str = "user_shop"

    model_config = {"from_attributes": True}


class CompetitorRead(BaseModel):
    id: int
    analysis_id: int
    competitor_name: str
    platform: str
    product_count: int
    average_price: float
    total_reviews: int
    average_rating: float = 0.0
    common_keywords: List[str]
    matched_queries: List[str] = Field(default_factory=list)
    example_listing_urls: List[str] = Field(default_factory=list)
    example_listing_titles: List[str] = Field(default_factory=list)
    match_score: float = 0.0
    positioning_summary: str

    model_config = {"from_attributes": True}


class CompetitorDetailRead(CompetitorRead):
    discovered_label: str = ""
    competing_listings: List[Dict[str, Any]] = Field(default_factory=list)
    price_comparison: Dict[str, Any] = Field(default_factory=dict)
    keyword_overlap: List[str] = Field(default_factory=list)
    user_unique_keywords: List[str] = Field(default_factory=list)
    competitor_unique_keywords: List[str] = Field(default_factory=list)
    product_gaps: List[str] = Field(default_factory=list)
    differentiation_opportunities: List[str] = Field(default_factory=list)


class ListingIssueRead(BaseModel):
    id: int
    analysis_id: int
    listing_id: Optional[int]
    severity: str
    category: str
    issue: str
    suggestion: str

    model_config = {"from_attributes": True}


class RecommendationRead(BaseModel):
    id: int
    analysis_id: int
    listing_id: Optional[int]
    category: str
    recommendation: str
    reasoning: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TrendRead(BaseModel):
    id: int
    analysis_id: int
    trend_name: str
    trend_type: str
    evidence: str
    opportunity: str
    competitor_examples: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_product_idea: str = ""
    keywords: List[str] = Field(default_factory=list)
    price_range: str = ""
    confidence: float = 0.0

    model_config = {"from_attributes": True}


class PricingSummary(BaseModel):
    min_price: float = 0.0
    max_price: float = 0.0
    average_price: float = 0.0
    median_price: float = 0.0
    suggested_min: float = 0.0
    suggested_max: float = 0.0
    underpriced: List[Dict[str, Any]] = Field(default_factory=list)
    overpriced: List[Dict[str, Any]] = Field(default_factory=list)
    competitor_min_price: float = 0.0
    competitor_max_price: float = 0.0
    competitor_average_price: float = 0.0
    competitor_median_price: float = 0.0
    user_average_price: float = 0.0
    price_buckets: List[Dict[str, Any]] = Field(default_factory=list)
    pricing_recommendation: str = ""


class KeywordInsight(BaseModel):
    tag: str
    keyword_type: str
    competitor_usage_count: int = 0
    user_usage_count: int = 0
    search_volume_estimate: str = "Low"
    competition_estimate: str = "Low"
    engagement_estimate: str = "medium"
    opportunity_score: int = 0
    trend_direction: str = "stable"
    related_tags: List[str] = Field(default_factory=list)
    example_competitor_listings: List[Dict[str, Any]] = Field(default_factory=list)
    example_user_listings: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_action: str = ""
    suggested_title_phrases: List[str] = Field(default_factory=list)
    suggested_etsy_tags: List[str] = Field(default_factory=list)
    suggested_description_phrase: str = ""
    pricing_context: Optional[str] = None


class KeywordSummary(BaseModel):
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    common_tags: List[Dict[str, Any]] = Field(default_factory=list)
    missing_opportunities: List[str] = Field(default_factory=list)
    competitor_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    keyword_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    tag_insights: List[Dict[str, Any]] = Field(default_factory=list)
    summary_stats: Dict[str, Any] = Field(default_factory=dict)
    missing_tag_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    long_tail_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    tag_gap_analysis: Dict[str, Any] = Field(default_factory=dict)


class AnalysisRead(BaseModel):
    id: int
    platform: str
    input_type: str
    input_value: str
    country: str
    currency: str
    status: str
    data_source: str = "live"
    created_at: datetime
    updated_at: datetime
    pricing_summary: Optional[PricingSummary] = None
    keyword_summary: Optional[KeywordSummary] = None

    model_config = {"from_attributes": True}


class AnalysisDetail(AnalysisRead):
    listings: List[ListingRead] = Field(default_factory=list)
    competitors: List[CompetitorRead] = Field(default_factory=list)
    listing_issues: List[ListingIssueRead] = Field(default_factory=list)
    recommendations: List[RecommendationRead] = Field(default_factory=list)
    trends: List[TrendRead] = Field(default_factory=list)
    warning: Optional[str] = None
    generated_queries: List[str] = Field(default_factory=list)


class AnalysisCreateResponse(AnalysisDetail):
    pass


class FreeformSearchRequest(BaseModel):
    analysis_id: int
    question: str


class FreeformSearchResponse(BaseModel):
    answer: str
    supporting_evidence: List[str] = Field(default_factory=list)
    uncertainty_notes: List[str] = Field(default_factory=list)
    data_source: str = "live"


class CodexStatusResponse(BaseModel):
    enabled: bool
    mode: str
    allow_file_patch: bool
    require_human_review: bool
    message: str


class AdapterRepairRequest(BaseModel):
    platform: str
    failing_url: str
    failing_html_sample: str = ""
    error_message: str = ""
    adapter_file_path: str = ""


class ExtractionQARequest(BaseModel):
    platform: str
    sample_raw_content: str = ""
    parsed_listings: List[Dict[str, Any]] = Field(default_factory=list)


class TestGeneratorRequest(BaseModel):
    target_file: str
    behavior_description: str


class CodexAgentResponse(BaseModel):
    success: bool
    enabled: bool
    message: str
    result: Dict[str, Any] = Field(default_factory=dict)


class SettingsStatusResponse(BaseModel):
    default_country: str
    default_language: str
    default_locale: str
    default_currency: str
    bright_data_configured: bool
    openai_configured: bool
    codex_enabled: bool
    database_status: str
    backend_api_url: str
    data_mode: str
