"""Analysis orchestration service."""

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.analysis.competitors import analyze_competitors
from app.analysis.keywords import extract_keywords
from app.analysis.listing_audit import audit_listings
from app.analysis.pricing import calculate_pricing_summary
from app.analysis.product_expansion import suggest_expansion
from app.analysis.trends import detect_trends
from app.models.database import Analysis, Competitor, Listing, ListingIssue, Recommendation, Trend
from app.schemas import AnalysisCreate, InputType
from app.services.ingestion import IngestionService
from app.services.normalization import normalize_listings


class AnalysisRunner:
  def __init__(self):
    self.ingestion = IngestionService()

  def run(self, db: Session, request: AnalysisCreate) -> Analysis:
    collected = self.ingestion.collect(
      request.platform,
      InputType(request.input_type),
      request.input_value,
      request.country,
    )
    listings_data = normalize_listings(collected.listings, request.currency)
    competitor_listings = (
      normalize_listings(collected.competitor_listings, request.currency)
      if collected.competitor_listings
      else []
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
      )
      db.add(listing)
      db_listings.append(listing)
    db.flush()

    pricing = calculate_pricing_summary(listings_data)
    keywords = extract_keywords(
      listings_data,
      competitor_listings=competitor_listings or None,
    )
    analysis.pricing_summary_json = pricing.model_dump_json()
    analysis.keyword_summary_json = keywords.model_dump_json()

    comp_data = analyze_competitors(competitor_listings, analysis.id, request.platform) if competitor_listings else []
    for c in comp_data:
      db.add(Competitor(
        analysis_id=analysis.id,
        competitor_name=c["competitor_name"],
        platform=c["platform"],
        product_count=c["product_count"],
        average_price=c["average_price"],
        total_reviews=c["total_reviews"],
        common_keywords_json=json.dumps(c["common_keywords"]),
        positioning_summary=c["positioning_summary"],
      ))

    top_kw = [k["keyword"] for k in keywords.top_keywords]
    issues = audit_listings(listings_data, analysis.id, pricing, top_kw)
    for issue in issues:
      db.add(ListingIssue(**issue))

    trends = detect_trends(listings_data + competitor_listings, analysis.id)
    for t in trends:
      db.add(Trend(**t))

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
    return analysis
