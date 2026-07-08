"""Analysis orchestration service."""

import json
import logging
from typing import List

from sqlalchemy.orm import Session

from app.analysis.competitor_discovery import _shop_key, is_own_shop
from app.analysis.competitors import analyze_competitors, build_competitor_detail
from app.analysis.keywords import extract_keywords
from app.analysis.listing_audit import audit_listings
from app.analysis.pricing import calculate_pricing_summary
from app.analysis.product_expansion import suggest_expansion
from app.analysis.trends import detect_trends
from app.models.database import Analysis, Competitor, Listing, ListingIssue, Recommendation, Trend
from app.schemas import AnalysisCreate, InputType
from app.services.ingestion import IngestionService
from app.services.normalization import normalize_listings

logger = logging.getLogger(__name__)


def _competing_listings_for_shop(competitor_listings: List, shop_name: str) -> List[dict]:
    shop_key = _shop_key(shop_name)
    results = []
    for listing in competitor_listings:
        if _shop_key(listing.shop_name) != shop_key:
            continue
        results.append({
            "title": listing.title,
            "url": listing.url,
            "price": listing.price,
            "rating": listing.rating,
            "review_count": listing.review_count,
            "image_url": listing.image_url,
        })
    return results[:12]


class AnalysisRunner:
  def __init__(self):
    self.ingestion = IngestionService()

  def run(self, db: Session, request: AnalysisCreate) -> Analysis:
    collected = self.ingestion.collect(
      request.platform,
      InputType(request.input_type),
      request.input_value,
      request.country,
      request.currency,
      request.language,
      request.locale,
    )
    listings_data = normalize_listings(collected.listings, request.currency)
    for listing in listings_data:
      listing.listing_source = listing.listing_source or "user_shop"
      listing.raw_data = {**(listing.raw_data or {}), "listing_source": "user_shop"}
    competitor_listings = (
      normalize_listings(collected.competitor_listings, request.currency)
      if collected.competitor_listings
      else []
    )
    user_shop_keys = collected.user_shop_keys or {_shop_key(request.input_value)}
    competitor_listings = [
      listing for listing in competitor_listings
      if listing.shop_name.strip() and not is_own_shop(listing.shop_name, user_shop_keys)
    ]
    for listing in competitor_listings:
      listing.listing_source = listing.listing_source or "competitor_search"
      listing.raw_data = {**(listing.raw_data or {}), "listing_source": "competitor_search"}

    logger.info(
      "Analysis shop=%s user_listings=%d competitor_listings=%d user_shop_keys=%s",
      request.input_value,
      len(listings_data),
      len(competitor_listings),
      sorted(user_shop_keys),
    )

    analysis = Analysis(
      platform=request.platform,
      input_type=request.input_type,
      input_value=request.input_value,
      country=request.country,
      currency=request.currency,
      status="completed",
      data_source=collected.data_source,
    )
    db.add(analysis)
    db.flush()

    db_listings = []
    for ld in listings_data:
      listing = Listing(
        analysis_id=analysis.id,
        platform=ld.platform,
        title=ld.title,
        url=ld.url,
        shop_name=ld.shop_name,
        price=ld.price,
        currency=ld.currency or request.currency,
        rating=ld.rating,
        review_count=ld.review_count,
        image_url=ld.image_url,
        description=ld.description,
        tags_json=json.dumps(ld.tags),
        detected_keywords_json=json.dumps(ld.detected_keywords),
        raw_data_json=json.dumps(ld.raw_data),
        listing_source="user_shop",
      )
      db.add(listing)
      db_listings.append(listing)

    for ld in competitor_listings:
      listing = Listing(
        analysis_id=analysis.id,
        platform=ld.platform,
        title=ld.title,
        url=ld.url,
        shop_name=ld.shop_name,
        price=ld.price,
        currency=ld.currency or request.currency,
        rating=ld.rating,
        review_count=ld.review_count,
        image_url=ld.image_url,
        description=ld.description,
        tags_json=json.dumps(ld.tags),
        detected_keywords_json=json.dumps(ld.detected_keywords),
        raw_data_json=json.dumps(ld.raw_data),
        listing_source="competitor_search",
      )
      db.add(listing)
    db.flush()

    pricing = calculate_pricing_summary(listings_data, competitor_listings or None)
    keywords = extract_keywords(
      listings_data,
      competitor_listings=competitor_listings or None,
    )
    analysis.pricing_summary_json = pricing.model_dump_json()
    analysis.keyword_summary_json = keywords.model_dump_json()

    comp_data = analyze_competitors(
      competitor_listings,
      analysis.id,
      request.platform,
      user_listings=listings_data,
      exclude_shop_keys=collected.user_shop_keys,
    ) if competitor_listings else []

    logger.info(
      "Competitor shops discovered for analysis=%s count=%d names=%s",
      analysis.id,
      len(comp_data),
      [item["competitor_name"] for item in comp_data],
    )

    for c in comp_data:
      db.add(Competitor(
        analysis_id=analysis.id,
        competitor_name=c["competitor_name"],
        platform=c["platform"],
        product_count=c["product_count"],
        average_price=c["average_price"],
        total_reviews=c["total_reviews"],
        average_rating=c.get("average_rating", 0.0),
        common_keywords_json=json.dumps(c["common_keywords"]),
        matched_queries_json=json.dumps(c.get("matched_queries", [])),
        example_listing_urls_json=json.dumps(c.get("example_listing_urls", [])),
        example_listing_titles_json=json.dumps(c.get("example_listing_titles", [])),
        competing_listings_json=json.dumps(
          _competing_listings_for_shop(competitor_listings, c["competitor_name"])
        ),
        match_score=c.get("match_score", 0.0),
        positioning_summary=c["positioning_summary"],
      ))

    top_kw = [k["keyword"] for k in keywords.top_keywords]
    issues = audit_listings(listings_data, analysis.id, pricing, top_kw)
    for issue in issues:
      db.add(ListingIssue(**issue))

    trends = detect_trends(listings_data + competitor_listings, analysis.id)
    for t in trends:
      details = t.pop("details", {})
      trend = Trend(
        analysis_id=analysis.id,
        trend_name=t["trend_name"],
        trend_type=t["trend_type"],
        evidence=t["evidence"],
        opportunity=t["opportunity"],
      )
      trend.details = details
      db.add(trend)

    expansion = suggest_expansion(listings_data, trends, comp_data)
    for e in expansion:
      db.add(Recommendation(
        analysis_id=analysis.id,
        category=e["category"],
        recommendation=e["recommendation"],
        reasoning=e["reasoning"],
        confidence=e["confidence"],
      ))

    db.commit()
    db.refresh(analysis)
    analysis._warning = collected.warning
    analysis._generated_queries = collected.generated_queries
    analysis._competitor_listings = competitor_listings
    analysis._user_listings = listings_data
    return analysis
