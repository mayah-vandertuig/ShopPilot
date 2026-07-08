"""Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InputType(str, Enum):
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


class AnalysisCreate(BaseModel):
    platform: str
    input_type: InputType
    input_value: str
    country: str = "US"
    currency: str = "USD"


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

    model_config = {"from_attributes": True}


class CompetitorRead(BaseModel):
    id: int
    analysis_id: int
    competitor_name: str
    platform: str
    product_count: int
    average_price: float
    total_reviews: int
    common_keywords: List[str]
    positioning_summary: str

    model_config = {"from_attributes": True}


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


class KeywordSummary(BaseModel):
    top_keywords: List[Dict[str, Any]] = Field(default_factory=list)
    common_tags: List[Dict[str, Any]] = Field(default_factory=list)
    missing_opportunities: List[str] = Field(default_factory=list)


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
